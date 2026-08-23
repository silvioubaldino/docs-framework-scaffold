#!/usr/bin/env python3
"""Probe do protocolo da camera (SPEC-001 de AYD-001).

Descobre o que uma IP camera realmente fala na rede local e emite o veredito
A / B / C que a arquitetura (ARCH) esta esperando:

  CAMINHO A -> RTSP + ONVIF com PTZ   : app fala direto com a camera
  CAMINHO B -> RTSP sem PTZ ONVIF     : video ok, PTZ precisa de ponte
  CAMINHO C -> nada aberto na LAN     : so a cloud do fabricante

Uso:
    python3 tools/probe_camera.py 192.168.15.16
    python3 tools/probe_camera.py 192.168.15.16 --user admin --password SENHA
    python3 tools/probe_camera.py 192.168.15.16 --json tools/out/probe.json

Sem dependencias alem da biblioteca padrao. Precisa rodar numa maquina da MESMA
rede da camera.

Contrato de saida: ver AYD-001, secao "Contratos".
  exit 0 -> concluiu (veredito no stdout)
  exit 1 -> host inalcancavel ou entrada invalida
"""
import argparse
import base64
import errno
import hashlib
import json
import os
import re
import socket
import ssl
import sys
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Alvos de varredura
# ---------------------------------------------------------------------------

# (porta, servico provavel, o que significa se estiver aberta)
PORTS = [
    (80,    "http",          "UI web / servico ONVIF"),
    (81,    "http-alt",      "UI web alternativa"),
    (443,   "https",         "UI web sobre TLS"),
    (554,   "rtsp",          "RTSP padrao - forte indicio de stream direto"),
    (555,   "rtsp-alt",      "RTSP alternativo"),
    (1935,  "rtmp",          "RTMP (raro em camera domestica)"),
    (2020,  "onvif-alt",     "ONVIF em porta alternativa"),
    (5000,  "upnp/misc",     "servico auxiliar"),
    (6668,  "tuya-local",    "protocolo local da familia Tuya"),
    (8000,  "hikvision-sdk", "SDK proprietario Hikvision"),
    (8080,  "http-alt",      "UI web / ONVIF"),
    (8081,  "http-alt",      "UI web alternativa"),
    (8443,  "https-alt",     "UI web sobre TLS"),
    (8554,  "rtsp-alt",      "RTSP alternativo - stream direto"),
    (8899,  "onvif-alt",     "ONVIF em firmware chines generico"),
    (9000,  "misc",          "servico auxiliar"),
    (34567, "dvrip",         "familia XMEye/Xiongmai (proprietario)"),
    (37777, "dahua",         "protocolo proprietario Dahua"),
]

# Portas que, abertas, sugerem um fabricante
VENDOR_PORT_HINTS = {
    6668:  "familia Tuya (protocolo local na 6668)",
    34567: "familia XMEye/Xiongmai (DVRIP na 34567)",
    37777: "familia Dahua (protocolo proprietario na 37777)",
    8000:  "possivel Hikvision (SDK na 8000)",
}

# Caminhos de stream mais comuns em firmware de camera IP
RTSP_PATHS = [
    "/", "/live", "/live/ch00_0", "/live/ch01_0", "/live/main", "/live/sub",
    "/live0.264", "/live1.264", "/11", "/12", "/h264", "/h264_stream",
    "/stream1", "/stream2", "/video1", "/video", "/videoMain", "/videoSub",
    "/onvif1", "/onvif2", "/av0_0", "/av0_1", "/ch0_0.h264", "/media/video1",
    "/profile1", "/profile2", "/mpeg4", "/0/av0",
    "/cam/realmonitor?channel=1&subtype=0",   # Dahua
    "/Streaming/Channels/101",                # Hikvision
]

ONVIF_SERVICE_PATHS = ["/onvif/device_service", "/onvif/services", "/onvif/device"]

WS_DISCOVERY_ADDR = ("239.255.255.250", 3702)

USER_AGENT = "vigia-probe/1.0"


# ---------------------------------------------------------------------------
# Funcoes puras (testadas em test_probe_camera.py)
# ---------------------------------------------------------------------------

def redact(text, password):
    """Remove a senha de qualquer texto que va para o relatorio.

    SPEC-001/AC-7: credencial nunca aparece na saida.
    """
    if not text:
        return text
    out = str(text)
    if password:
        out = out.replace(password, "***")
    # usuario:senha@host em qualquer URL
    out = re.sub(r"(\w+://)[^/\s@]+:[^/\s@]+@", r"\1***:***@", out)
    return out


def decide_verdict(findings):
    """Traduz os achados no veredito A/B/C. Funcao pura, sem rede.

    findings: dict com as chaves rtsp_ok (bool), onvif_ok (bool),
              onvif_ptz (bool), open_ports (list[int]), vendor_hints (list[str]).
    Retorna (verdict, reason).
    """
    rtsp_ok = findings.get("rtsp_ok", False)
    onvif_ok = findings.get("onvif_ok", False)
    onvif_ptz = findings.get("onvif_ptz", False)
    hints = findings.get("vendor_hints") or []

    if rtsp_ok and onvif_ok and onvif_ptz:
        return "A", ("a camera fala RTSP e ONVIF com servico de PTZ. "
                     "O app pode falar direto com ela: video por RTSP, rotacao por SOAP ONVIF.")
    if rtsp_ok and onvif_ok:
        return "B", ("a camera fala RTSP e ONVIF, mas o ONVIF nao anuncia servico de PTZ. "
                     "Video resolvido; a rotacao precisa de outra via (ver AYD-003).")
    if rtsp_ok:
        return "B", ("a camera entrega stream RTSP, mas nao responde ONVIF. "
                     "Video resolvido; a rotacao precisa de engenharia reversa ou ponte (ver AYD-003).")
    if onvif_ok:
        return "B", ("a camera responde ONVIF mas nenhum caminho RTSP respondeu. "
                     "Consulte os perfis via GetProfiles/GetStreamUri para achar a URL correta.")
    reason = ("nenhuma porta de midia ou ONVIF respondeu. A camera provavelmente so fala "
              "P2P com a cloud do fabricante.")
    if hints:
        reason += " Indicios de fabricante: " + "; ".join(hints) + "."
    return "C", reason


def is_reachable(port_states):
    """O host reagiu? Funcao pura.

    So conta como vivo se alguma porta conectou (aberta) ou recusou com RST
    (fechada). Timeout em tudo, ou rota inexistente, significa que nao ha
    ninguem naquele endereco. SPEC-001/AC-1.
    """
    return any(v in ("aberta", "fechada") for v in port_states.values())


def classify_rtsp_status(status):
    """Traduz o status de um DESCRIBE em existencia do caminho. Funcao pura.

    SPEC-001/AC-6: 401 prova que o caminho EXISTE e esta protegido - nao pode
    ser confundido com 404 (nao existe).
    """
    if status == 200:
        return "ok"
    if status in (401, 403):
        return "auth"
    return "absent"


def parse_digest_challenge(header):
    """Extrai os campos de um desafio 'WWW-Authenticate: Digest ...'."""
    return dict(re.findall(r'(\w+)="([^"]*)"', header or ""))


def build_digest_response(user, password, method, uri, challenge):
    """Monta o header Authorization de um digest MD5 (RFC 2617)."""
    realm = challenge.get("realm", "")
    nonce = challenge.get("nonce", "")
    ha1 = hashlib.md5(f"{user}:{realm}:{password}".encode()).hexdigest()
    ha2 = hashlib.md5(f"{method}:{uri}".encode()).hexdigest()
    resp = hashlib.md5(f"{ha1}:{nonce}:{ha2}".encode()).hexdigest()
    return (f'Digest username="{user}", realm="{realm}", nonce="{nonce}", '
            f'uri="{uri}", response="{resp}"')


def ws_username_token(user, password):
    """Cabecalho WS-Security UsernameToken com PasswordDigest (ONVIF)."""
    nonce = os.urandom(16)
    created = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    digest = base64.b64encode(
        hashlib.sha1(nonce + created.encode() + password.encode()).digest()
    ).decode()
    return f'''<s:Header>
    <Security s:mustUnderstand="1" xmlns="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
      <UsernameToken>
        <Username>{user}</Username>
        <Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordDigest">{digest}</Password>
        <Nonce EncodingType="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary">{base64.b64encode(nonce).decode()}</Nonce>
        <Created xmlns="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">{created}</Created>
      </UsernameToken>
    </Security>
  </s:Header>'''


# ---------------------------------------------------------------------------
# Rede
# ---------------------------------------------------------------------------

def scan_port(host, port, timeout):
    """Estado de uma porta TCP.

    Distingue os tres casos que significam coisas diferentes:
      aberta       -> conectou
      fechada      -> RST (host VIVO, porta fechada)
      filtrada     -> timeout (firewall descartando)
      inalcancavel -> host/rede sem rota (host provavelmente ausente)
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        return "aberta"
    except socket.timeout:
        return "filtrada"
    except OSError as e:
        if e.errno in (errno.EHOSTUNREACH, errno.ENETUNREACH, errno.EHOSTDOWN):
            return "inalcancavel"
        return "fechada"
    finally:
        s.close()


def scan_ports(host, timeout):
    with ThreadPoolExecutor(max_workers=16) as pool:
        futures = {p: pool.submit(scan_port, host, p, timeout) for p, _, _ in PORTS}
        return {p: f.result() for p, f in futures.items()}


def rtsp_request(host, port, path, method, user, password, timeout):
    """Faz uma requisicao RTSP crua. Retorna (status_code, headers_texto, corpo)."""
    url = f"rtsp://{host}:{port}{path}"

    def send(auth_header=None):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        try:
            s.connect((host, port))
            lines = [f"{method} {url} RTSP/1.0",
                     "CSeq: 1",
                     f"User-Agent: {USER_AGENT}"]
            if method == "DESCRIBE":
                lines.append("Accept: application/sdp")
            if auth_header:
                lines.append(f"Authorization: {auth_header}")
            s.sendall(("\r\n".join(lines) + "\r\n\r\n").encode())
            data = b""
            while len(data) < 8192:
                chunk = s.recv(4096)
                if not chunk:
                    break
                data += chunk
                if b"\r\n\r\n" in data and method != "DESCRIBE":
                    break
            return data.decode("utf-8", "replace")
        finally:
            s.close()

    try:
        raw = send()
    except OSError:
        return None, "", ""

    m = re.match(r"RTSP/1\.\d (\d{3})", raw)
    status = int(m.group(1)) if m else None

    # 401 com credencial disponivel -> tenta autenticar
    if status == 401 and user:
        challenge = ""
        for line in raw.splitlines():
            if line.lower().startswith("www-authenticate:"):
                challenge = line.split(":", 1)[1].strip()
                break
        try:
            if challenge.lower().startswith("digest"):
                auth = build_digest_response(
                    user, password, method, url, parse_digest_challenge(challenge))
            else:
                token = base64.b64encode(f"{user}:{password}".encode()).decode()
                auth = f"Basic {token}"
            raw = send(auth)
            m = re.match(r"RTSP/1\.\d (\d{3})", raw)
            status = int(m.group(1)) if m else None
        except OSError:
            pass

    head, _, body = raw.partition("\r\n\r\n")
    return status, head, body


def ws_discovery(timeout):
    """Descoberta ONVIF por multicast (WS-Discovery). Retorna lista de XAddrs."""
    msg = f'''<?xml version="1.0" encoding="UTF-8"?>
<e:Envelope xmlns:e="http://www.w3.org/2003/05/soap-envelope"
            xmlns:w="http://schemas.xmlsoap.org/ws/2004/08/addressing"
            xmlns:d="http://schemas.xmlsoap.org/ws/2005/04/discovery"
            xmlns:dn="http://www.onvif.org/ver10/network/wsdl">
  <e:Header>
    <w:MessageID>uuid:{uuid.uuid4()}</w:MessageID>
    <w:To e:mustUnderstand="1">urn:schemas-xmlsoap-org:ws:2005:04:discovery</w:To>
    <w:Action e:mustUnderstand="1">http://schemas.xmlsoap.org/ws/2005/04/discovery/Probe</w:Action>
  </e:Header>
  <e:Body><d:Probe><d:Types>dn:NetworkVideoTransmitter</d:Types></d:Probe></e:Body>
</e:Envelope>'''
    addrs = []
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    s.settimeout(timeout)
    try:
        s.sendto(msg.encode(), WS_DISCOVERY_ADDR)
        while True:
            try:
                data, _ = s.recvfrom(65535)
            except socket.timeout:
                break
            for x in re.findall(r"<[^>]*XAddrs>([^<]+)<", data.decode("utf-8", "replace")):
                addrs.extend(x.split())
    except OSError:
        pass
    finally:
        s.close()
    return sorted(set(addrs))


def listen_tuya_broadcast(timeout):
    """Escuta o broadcast periodico da familia Tuya (UDP 6666/6667)."""
    found = []
    for port in (6667, 6666):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.settimeout(timeout)
        try:
            s.bind(("", port))
            data, addr = s.recvfrom(4096)
            if data:
                found.append(f"broadcast UDP {port} de {addr[0]} (assinatura Tuya)")
        except OSError:
            pass
        finally:
            s.close()
    return found


def http_soap(url, body, timeout):
    """POST SOAP cru sobre HTTP/HTTPS, sem dependencia externa."""
    import urllib.request
    req = urllib.request.Request(
        url, data=body.encode(),
        headers={"Content-Type": "application/soap+xml; charset=utf-8",
                 "User-Agent": USER_AGENT},
        method="POST")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except Exception as e:  # HTTPError inclusive: o corpo do erro tambem informa
        body = getattr(e, "read", lambda: b"")()
        return getattr(e, "code", None), body.decode("utf-8", "replace")


def onvif_call(url, action_body, user, password, timeout):
    header = ws_username_token(user, password) if user else ""
    envelope = f'''<?xml version="1.0" encoding="UTF-8"?>
<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope">
  {header}
  <s:Body>{action_body}</s:Body>
</s:Envelope>'''
    return http_soap(url, envelope, timeout)


# ---------------------------------------------------------------------------
# Orquestracao
# ---------------------------------------------------------------------------

def run_probe(host, user, password, timeout):
    result = {
        "host": host,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "reachable": False,
        "open_ports": [],
        "port_states": {},
        "onvif": {"discovered": False, "endpoints": [], "device_info": {}, "has_ptz": False},
        "rtsp": {"paths_ok": [], "paths_auth": [], "auth_required": False, "sdp": ""},
        "vendor_hints": [],
        "verdict": None,
        "reason": "",
    }

    print(f"  Alvo: {host}")
    print(f"  Varrendo {len(PORTS)} portas tipicas de camera...")
    states = scan_ports(host, timeout)
    result["port_states"] = {str(p): s for p, s in states.items()}

    meta = {p: (svc, note) for p, svc, note in PORTS}
    for port, state in sorted(states.items()):
        svc, note = meta[port]
        if state == "aberta":
            result["open_ports"].append({"port": port, "service": svc, "note": note})
            print(f"    [ABERTA]   {port:>5}/tcp  {svc:<14} {note}")
            if port in VENDOR_PORT_HINTS:
                result["vendor_hints"].append(VENDOR_PORT_HINTS[port])

    if not result["open_ports"]:
        # Nenhuma porta aberta ainda nao prova que o host morreu: pode estar
        # com tudo filtrado. "filtrada" em toda porta = ha algo la respondendo devagar.
        vals = list(states.values())
        if all(v == "fechada" for v in vals):
            print("    nenhuma porta aberta - o host respondeu, mas recusou tudo")
        elif any(v == "inalcancavel" for v in vals):
            print("    sem rota ate o host - ele nao esta nesta rede")
        else:
            print("    tudo filtrado - firewall descartando, ou host ausente")
    result["reachable"] = is_reachable(states)

    if not result["reachable"]:
        return result

    # --- ONVIF -------------------------------------------------------------
    print("\n  Descoberta ONVIF (WS-Discovery, multicast UDP 3702)...")
    addrs = [a for a in ws_discovery(max(timeout, 3)) if host in a]
    if addrs:
        result["onvif"]["discovered"] = True
        result["onvif"]["endpoints"] = addrs
        print(f"    respondeu: {', '.join(addrs)}")
    else:
        print("    sem resposta ao multicast")

    # Mesmo sem WS-Discovery, muitas cameras servem ONVIF no caminho padrao.
    candidates = list(addrs)
    for port, svc, _ in PORTS:
        if states.get(port) == "aberta" and svc.startswith(("http", "onvif")):
            scheme = "https" if "https" in svc else "http"
            for path in ONVIF_SERVICE_PATHS:
                candidates.append(f"{scheme}://{host}:{port}{path}")

    if candidates:
        print("  Consultando GetDeviceInformation / GetCapabilities...")
    for url in dict.fromkeys(candidates):
        status, body = onvif_call(
            url, '<GetDeviceInformation xmlns="http://www.onvif.org/ver10/device/wsdl"/>',
            user, password, timeout)
        if status == 200 and "DeviceInformation" in body:
            info = {}
            for tag in ("Manufacturer", "Model", "FirmwareVersion", "SerialNumber", "HardwareId"):
                m = re.search(rf"<[^>]*{tag}>([^<]*)<", body)
                if m:
                    info[tag] = m.group(1)
            result["onvif"]["discovered"] = True
            result["onvif"]["device_info"] = info
            if url not in result["onvif"]["endpoints"]:
                result["onvif"]["endpoints"].append(url)
            print(f"    ONVIF respondeu em {url}")
            for k, v in info.items():
                print(f"      {k}: {v}")

            _, caps = onvif_call(
                url, '<GetCapabilities xmlns="http://www.onvif.org/ver10/device/wsdl">'
                     '<Category>All</Category></GetCapabilities>',
                user, password, timeout)
            if re.search(r"<[^>]*PTZ>", caps or ""):
                result["onvif"]["has_ptz"] = True
                print("      servico de PTZ: ANUNCIADO")
            else:
                print("      servico de PTZ: nao anunciado")
            break
        elif status in (401, 403):
            print(f"    {url} pediu autenticacao "
                  f"({'credencial recusada' if user else 'rode com --user/--password'})")

    # --- RTSP --------------------------------------------------------------
    rtsp_ports = [p for p, svc, _ in PORTS
                  if svc.startswith("rtsp") and states.get(p) == "aberta"]
    if rtsp_ports:
        print(f"\n  Testando {len(RTSP_PATHS)} caminhos RTSP em {rtsp_ports}...")
    for port in rtsp_ports:
        status, _, _ = rtsp_request(host, port, "/", "OPTIONS", user, password, timeout)
        if status is None:
            continue
        for path in RTSP_PATHS:
            status, head, body = rtsp_request(host, port, path, "DESCRIBE",
                                              user, password, timeout)
            url = f"rtsp://{host}:{port}{path}"
            kind = classify_rtsp_status(status)
            if kind == "ok":
                result["rtsp"]["paths_ok"].append(url)
                if not result["rtsp"]["sdp"] and body:
                    result["rtsp"]["sdp"] = body[:2000]
                print(f"    [OK 200]   {url}")
            elif kind == "auth":
                result["rtsp"]["paths_auth"].append(url)
                result["rtsp"]["auth_required"] = True
                print(f"    [{status}]      {url}  (existe, pede senha)")

    if result["rtsp"]["paths_auth"] and not user:
        print("\n    Ha caminhos protegidos por senha. Rode de novo com "
              "--user/--password para confirmar o stream.")

    # --- Pistas de fabricante ---------------------------------------------
    tuya = listen_tuya_broadcast(2)
    result["vendor_hints"].extend(tuya)
    for hint in tuya:
        print(f"\n  Pista de fabricante: {hint}")

    findings = {
        "rtsp_ok": bool(result["rtsp"]["paths_ok"] or result["rtsp"]["paths_auth"]),
        "onvif_ok": result["onvif"]["discovered"],
        "onvif_ptz": result["onvif"]["has_ptz"],
        "open_ports": [p["port"] for p in result["open_ports"]],
        "vendor_hints": result["vendor_hints"],
    }
    result["verdict"], result["reason"] = decide_verdict(findings)
    return result


NEXT_STEPS = {
    "A": ["Marque AYD-001 como resolvido e registre o resultado nele.",
          "Feche ADR-003 escolhendo VLCKit + ONVIF SOAP.",
          "Comece a F1 do roadmap: app minimo com o stream que respondeu 200.",
          "Guarde a URL RTSP que funcionou - ela vai para a config da Camera."],
    "B": ["Marque AYD-001 como resolvido e registre o resultado nele.",
          "Video esta resolvido: siga a F1 do roadmap com a URL que respondeu.",
          "PTZ vira problema separado - releia AYD-003, secao 'Caminhos B e C'.",
          "Teste se o Home Assistant reconhece a camera: e a via mais barata de PTZ."],
    "C": ["Confirme que a maquina do teste esta na MESMA rede/VLAN da camera.",
          "Procure no app de fabrica por 'ONVIF' ou 'RTSP' nas configuracoes avancadas - "
          "em muitos firmwares isso vem desligado de fabrica.",
          "Consulte o OUI do MAC (34:A6:EF) para identificar o fabricante real.",
          "Se confirmar C: releia AYD-004 e ADR-003 antes de aceitar depender da cloud."],
}


def print_report(result, password):
    print("\n" + "=" * 72)
    v = result["verdict"]
    print(f"VEREDITO: CAMINHO {v} - {result['reason']}")
    print("=" * 72)
    if result["rtsp"]["paths_ok"]:
        print("\nStreams que responderam:")
        for u in result["rtsp"]["paths_ok"]:
            print(f"  {redact(u, password)}")
    if result["onvif"]["endpoints"]:
        print("\nEndpoints ONVIF:")
        for u in result["onvif"]["endpoints"]:
            print(f"  {redact(u, password)}")
    print("\nProximos passos:")
    for step in NEXT_STEPS[v]:
        print(f"  - {step}")
    print()


def main():
    ap = argparse.ArgumentParser(
        description="Descobre o protocolo de uma IP camera na rede local (SPEC-001).")
    ap.add_argument("host", help="IP da camera na LAN (ex.: 192.168.15.16)")
    ap.add_argument("--user", default="", help="usuario da camera (ex.: admin)")
    ap.add_argument("--password", default="", help="senha da camera")
    ap.add_argument("--timeout", type=float, default=2.0,
                    help="timeout por operacao, em segundos (padrao: 2)")
    ap.add_argument("--json", metavar="ARQUIVO",
                    help="grava o resultado completo como JSON")
    args = ap.parse_args()

    try:
        socket.inet_aton(args.host)
    except OSError:
        try:
            args.host = socket.gethostbyname(args.host)
        except OSError:
            print(f"ERRO: nao consegui resolver '{args.host}'.", file=sys.stderr)
            return 1

    print("=" * 72)
    print("  PROBE DO PROTOCOLO DA CAMERA - SPEC-001 / AYD-001")
    print("=" * 72)

    result = run_probe(args.host, args.user, args.password, args.timeout)

    if not result["reachable"]:
        print(f"\nERRO: host {args.host} inalcancavel.")
        print("  Verifique se esta na mesma rede da camera (Wi-Fi de casa),")
        print("  se o IP mudou (DHCP) e se nao ha VPN corporativa ativa.")
        return 1

    print_report(result, args.password)

    if args.json:
        os.makedirs(os.path.dirname(os.path.abspath(args.json)), exist_ok=True)
        safe = json.loads(redact(json.dumps(result), args.password))
        with open(args.json, "w") as f:
            json.dump(safe, f, indent=2, ensure_ascii=False)
        print(f"JSON gravado em {args.json}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
