#!/usr/bin/env python3
"""Testes da logica pura do probe (SPEC-001).

Cobre a logica de decisao de todos os criterios de aceite. O que NAO da para
testar aqui e o comportamento contra hardware real - a camera pode responder de
um jeito que nenhum destes testes preve. Por isso SPEC-001 so vira 'approved'
depois de o probe rodar contra a camera de verdade.

    python3 tools/test_probe_camera.py
"""
import unittest

from probe_camera import (
    PORTS,
    build_digest_response,
    classify_rtsp_status,
    decide_verdict,
    is_reachable,
    parse_digest_challenge,
    redact,
)


class TestVerdict(unittest.TestCase):
    def test_rtsp_e_onvif_com_ptz_dao_caminho_a(self):
        """SPEC-001/AC-3: ONVIF completo com PTZ -> CAMINHO A."""
        verdict, reason = decide_verdict({
            "rtsp_ok": True, "onvif_ok": True, "onvif_ptz": True,
        })
        self.assertEqual(verdict, "A")
        self.assertIn("PTZ", reason)

    def test_onvif_sem_ptz_cai_para_caminho_b(self):
        """SPEC-001/AC-3: ONVIF que nao anuncia PTZ nao e caminho A."""
        verdict, _ = decide_verdict({
            "rtsp_ok": True, "onvif_ok": True, "onvif_ptz": False,
        })
        self.assertEqual(verdict, "B")

    def test_rtsp_sem_onvif_da_caminho_b(self):
        """SPEC-001/AC-4: stream sim, ONVIF nao -> CAMINHO B."""
        verdict, reason = decide_verdict({
            "rtsp_ok": True, "onvif_ok": False, "onvif_ptz": False,
        })
        self.assertEqual(verdict, "B")
        self.assertIn("AYD-003", reason)

    def test_nada_aberto_da_caminho_c(self):
        """SPEC-001/AC-5: camera fechada -> CAMINHO C."""
        verdict, _ = decide_verdict({
            "rtsp_ok": False, "onvif_ok": False, "onvif_ptz": False,
        })
        self.assertEqual(verdict, "C")

    def test_caminho_c_reporta_indicios_de_fabricante(self):
        """SPEC-001/AC-5: os indicios encontrados entram na justificativa."""
        _, reason = decide_verdict({
            "rtsp_ok": False, "onvif_ok": False, "onvif_ptz": False,
            "vendor_hints": ["familia Tuya (protocolo local na 6668)"],
        })
        self.assertIn("Tuya", reason)

    def test_findings_incompleto_nao_quebra(self):
        """Dict sem chaves opcionais nao deve levantar excecao."""
        verdict, _ = decide_verdict({})
        self.assertEqual(verdict, "C")


class TestRedacao(unittest.TestCase):
    def test_senha_nunca_aparece_na_saida(self):
        """SPEC-001/AC-7: a senha e removida de qualquer texto do relatorio."""
        out = redact("rtsp://admin:hunter2@192.168.15.16/live", "hunter2")
        self.assertNotIn("hunter2", out)

    def test_credencial_em_url_e_mascarada_mesmo_sem_senha_conhecida(self):
        """SPEC-001/AC-7: user:pass@host vira ***:***@host."""
        out = redact("rtsp://admin:segredo@192.168.15.16/live", "")
        self.assertNotIn("segredo", out)
        self.assertIn("***:***@192.168.15.16", out)

    def test_texto_sem_credencial_passa_intacto(self):
        self.assertEqual(redact("rtsp://192.168.15.16/live", "x"),
                         "rtsp://192.168.15.16/live")

    def test_entrada_vazia(self):
        self.assertEqual(redact("", "senha"), "")
        self.assertIsNone(redact(None, "senha"))


class TestDigest(unittest.TestCase):
    def test_parse_do_desafio(self):
        c = parse_digest_challenge('Digest realm="IP Camera", nonce="abc123", qop="auth"')
        self.assertEqual(c["realm"], "IP Camera")
        self.assertEqual(c["nonce"], "abc123")

    def test_resposta_digest_bate_com_o_rfc_2617(self):
        # Valores fixos: HA1=md5(user:realm:pass), HA2=md5(method:uri),
        # response=md5(HA1:nonce:HA2). Confere o encadeamento, nao a lib de hash.
        import hashlib
        user, pwd, realm, nonce = "admin", "1234", "IP Camera", "deadbeef"
        uri, method = "rtsp://cam/live", "DESCRIBE"
        ha1 = hashlib.md5(f"{user}:{realm}:{pwd}".encode()).hexdigest()
        ha2 = hashlib.md5(f"{method}:{uri}".encode()).hexdigest()
        esperado = hashlib.md5(f"{ha1}:{nonce}:{ha2}".encode()).hexdigest()

        header = build_digest_response(
            user, pwd, method, uri, {"realm": realm, "nonce": nonce})
        self.assertIn(f'response="{esperado}"', header)
        self.assertIn(f'username="{user}"', header)
        self.assertNotIn(pwd, header)


class TestAlcance(unittest.TestCase):
    def test_host_que_recusa_conexao_esta_vivo(self):
        """SPEC-001/AC-1: RST significa host vivo com porta fechada."""
        self.assertTrue(is_reachable({80: "fechada", 554: "fechada"}))

    def test_host_com_porta_aberta_esta_vivo(self):
        """SPEC-001/AC-1: qualquer porta aberta prova que o host existe."""
        self.assertTrue(is_reachable({80: "filtrada", 554: "aberta"}))

    def test_tudo_filtrado_conta_como_inalcancavel(self):
        """SPEC-001/AC-1: timeout em tudo -> host ausente, exit 1."""
        self.assertFalse(is_reachable({80: "filtrada", 554: "filtrada"}))

    def test_sem_rota_conta_como_inalcancavel(self):
        """SPEC-001/AC-1: EHOSTUNREACH em tudo -> host ausente, exit 1."""
        self.assertFalse(is_reachable({80: "inalcancavel", 554: "inalcancavel"}))


class TestMapaDePortas(unittest.TestCase):
    def test_toda_porta_tem_servico_e_explicacao(self):
        """SPEC-001/AC-2: o relatorio identifica o servico provavel de cada porta."""
        for port, service, note in PORTS:
            self.assertIsInstance(port, int)
            self.assertTrue(service, f"porta {port} sem servico")
            self.assertTrue(note, f"porta {port} sem explicacao")

    def test_nao_ha_porta_duplicada(self):
        portas = [p for p, _, _ in PORTS]
        self.assertEqual(len(portas), len(set(portas)))

    def test_as_portas_de_midia_essenciais_estao_cobertas(self):
        """SPEC-001/AC-2: 554 e 8554 sao o que decide entre caminho A/B e C."""
        portas = {p for p, _, _ in PORTS}
        for essencial in (80, 554, 8554, 8899):
            self.assertIn(essencial, portas)


class TestClassificacaoRTSP(unittest.TestCase):
    def test_200_e_caminho_valido(self):
        """SPEC-001/AC-6: 200 -> o stream existe e abriu."""
        self.assertEqual(classify_rtsp_status(200), "ok")

    def test_401_e_caminho_existente_protegido(self):
        """SPEC-001/AC-6: 401 nao pode ser confundido com caminho inexistente."""
        self.assertEqual(classify_rtsp_status(401), "auth")

    def test_403_tambem_prova_existencia(self):
        """SPEC-001/AC-6: 403 e o mesmo caso - existe, mas nao liberou."""
        self.assertEqual(classify_rtsp_status(403), "auth")

    def test_404_e_ausencia(self):
        """SPEC-001/AC-6: 404 -> o caminho nao existe."""
        self.assertEqual(classify_rtsp_status(404), "absent")

    def test_sem_resposta_e_ausencia(self):
        """SPEC-001/AC-6: conexao morta nao vira caminho valido."""
        self.assertEqual(classify_rtsp_status(None), "absent")


if __name__ == "__main__":
    unittest.main(verbosity=2)
