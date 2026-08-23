---
id: SPEC-001
type: spec
title: Probe do protocolo da câmera
status: review
updated: 2026-08-23
parents: [AYD-001]
children: []
related: [ARCH, ADR-003, GLO]
---

# SPEC-001: Probe do protocolo da câmera

> Forma executável do AYD-001. Entrega: `tools/probe_camera.py`.
> É a primeira coisa a rodar no projeto, e a que destrava tudo o mais.

## Objetivo
Uma ferramenta que, executada numa máquina da rede de casa, responde em menos de um
minuto: **a `Camera` fala RTSP? fala ONVIF? nenhum dos dois?** — e traduz a resposta no
veredito A / B / C que ADR-003 está esperando.

## Como rodar
```bash
# mínimo
python3 tools/probe_camera.py 192.168.15.16

# com credenciais (muitas câmeras só respondem DESCRIBE autenticado)
python3 tools/probe_camera.py 192.168.15.16 --user admin --password SENHA

# guardando o resultado para anexar ao AYD-001
python3 tools/probe_camera.py 192.168.15.16 --json tools/out/probe.json
```

Requisitos: Python 3.8+, biblioteca padrão apenas. Precisa estar **na mesma rede** da
câmera (Wi-Fi de casa serve; VPN corporativa atrapalha).

## Critérios de aceite

```gherkin
# AC-1
Cenário: Host inalcançável
  Dado um IP que não responde na rede
  Quando o probe é executado contra ele
  Então o relatório informa que o host está inalcançável
  E o processo termina com código de saída 1

# AC-2
Cenário: Mapeamento de portas
  Dado uma Camera alcançável
  Quando o probe é executado
  Então o relatório lista cada porta típica de câmera testada com seu estado
  E identifica o serviço provável de cada porta aberta

# AC-3
Cenário: Câmera ONVIF completa
  Dado que a Camera responde à descoberta WS-Discovery
  E que GetCapabilities anuncia o serviço de PTZ
  E que RTSP responde a OPTIONS
  Quando o probe conclui
  Então o veredito é "CAMINHO A"
  E o relatório traz fabricante e modelo real vindos de GetDeviceInformation

# AC-4
Cenário: RTSP sem ONVIF
  Dado que a Camera responde a RTSP OPTIONS
  E que não há resposta a WS-Discovery nem a SOAP ONVIF
  Quando o probe conclui
  Então o veredito é "CAMINHO B"
  E o relatório lista os caminhos de Stream que responderam

# AC-5
Cenário: Câmera fechada, só cloud
  Dado que nenhuma porta de mídia ou ONVIF está aberta
  Quando o probe conclui
  Então o veredito é "CAMINHO C"
  E o relatório aponta os indícios de fabricante encontrados, se houver

# AC-6
Cenário: Distinguir ausência de proteção
  Dado que um caminho RTSP responde 401 Unauthorized
  Quando o probe conclui
  Então esse caminho é reportado como existente e protegido por senha
  E não é confundido com um caminho inexistente (404)

# AC-7
Cenário: Credenciais nunca vazam para o relatório
  Dado que o probe foi executado com --user e --password
  Quando o relatório e o JSON são gerados
  Então a senha não aparece em nenhuma parte da saída
  E as URLs exibidas têm a credencial substituída por marcador
```

## Contratos consumidos/expostos
Expõe o contrato de saída definido em **AYD-001 § Contratos** (código de saída, linha
`VEREDITO:`, esquema do JSON). Esta spec não o redefine.

## Componentes afetados
- `tools/probe_camera.py` — a ferramenta.
- `tools/test_probe_camera.py` — testes da lógica de decisão de todos os `AC-N` acima
  (veredito, alcance do host, classificação 401/404, mapa de portas, redação de senha).
  O que **não** dá para testar aqui é o comportamento contra hardware real: a câmera pode
  responder de um jeito que nenhum teste prevê. Por isso esta spec só vira `approved`
  depois de o probe rodar contra a câmera de verdade.
- `design/AYD-001-descoberta-do-protocolo.md` — recebe o resultado numa seção
  "Resultado do Probe" quando ele existir.

## Casos de borda & fora de escopo
- **Borda:** porta filtrada (firewall descarta) versus fechada (RST) — a primeira aparece
  como timeout. O relatório distingue os dois.
- **Borda:** câmera responde ONVIF mas **sem** serviço de PTZ (existem). Veredito B, não A —
  vídeo resolvido, rotação não.
- **Borda:** a máquina do teste está numa VLAN/rede de convidados isolada da câmera. O
  probe não consegue detectar isso; o relatório avisa quando nada responde.
- **Fora:** captura de tráfego do app de fábrica, análise de firmware, força bruta de
  credenciais. Se o veredito for C e a engenharia reversa virar necessária, ela ganha
  AYD e SPEC próprios.
- **Fora:** varrer a rede inteira em busca de câmeras. O alvo é um IP conhecido.
