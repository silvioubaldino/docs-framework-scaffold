# Vigia

App iOS nativo para assistir e controlar uma IP camera doméstica — **sem anúncios**,
sem telemetria, sem conta em cloud de terceiro.

> **Status: análise.** Ainda não há código. Este repo carrega hoje a documentação que
> decide *o que* construir e *como*, e a ferramenta que responde à única pergunta que
> trava tudo (ver abaixo).

## O problema
Os apps que acompanham câmeras IP baratas funcionam, mas são hostis: anúncios em tela
cheia entre você e a imagem ao vivo, upsell de "cloud storage", telemetria opaca e uma
conta obrigatória no servidor do fabricante. A câmera é sua, está na sua rede — o
software entre você e ela deveria ser seu também.

## O bloqueio: qual protocolo a câmera fala?
Toda a arquitetura depende disto, e a etiqueta do fabricante não responde. O modelo
reportado é literalmente `CloudCam` — um rótulo genérico de firmware white-label.
São três mundos possíveis, com custos de engenharia muito diferentes:

| Caminho | Se a câmera… | Consequência |
|---------|--------------|--------------|
| **A** | fala ONVIF **e** RTSP | Melhor caso: vídeo por RTSP, PTZ por SOAP ONVIF. App fala direto com a câmera. |
| **B** | fala RTSP, mas não ONVIF | Vídeo resolvido; PTZ exige engenharia reversa ou ponte. |
| **C** | só fala a cloud P2P do fabricante | Sem acesso direto: ou a API oficial da cloud, ou uma ponte (Home Assistant), ou firmware alternativo. |

**Descubra rodando isto numa máquina na mesma rede da câmera:**

```bash
python3 tools/probe_camera.py 192.168.15.16
```

Sem dependências além do Python 3. O script varre as portas típicas de câmera, faz
descoberta ONVIF (WS-Discovery), tenta `RTSP OPTIONS/DESCRIBE` nos caminhos de URL mais
comuns e imprime o veredito **A / B / C**. Ver `specs/SPEC-001` para o procedimento
completo, incluindo o que fazer com o resultado.

## Como ler esta documentação
Do *porquê* ao *como* — cada doc aponta para o de cima e para os de baixo:

```
requirements.md (REQ-001) ── por que o app existe, o que ele precisa fazer
   ├── design/AYD-001  Descoberta do protocolo da câmera  ──> specs/SPEC-001
   ├── design/AYD-002  Streaming ao vivo
   ├── design/AYD-003  Controle PTZ
   └── design/AYD-004  Acesso remoto (fora da rede de casa)

architecture.md (ARCH)          topologia vigente + as três topologias candidatas
architecture_decisions/         por que cada escolha foi feita (append-only)
roadmap.md (ROAD-001)           fases, do probe ao app funcionando fora de casa
```

As convenções (IDs, frontmatter, ciclo de vida) estão em `CLAUDE.md`.

## Validar a documentação
```bash
python3 scripts/validate.py
```
Checa frontmatter, simetria `parents`/`children` e referências quebradas. Requer só
Python 3 (biblioteca padrão).
