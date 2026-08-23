---
id: ADR-003
type: adr
title: Stack de vídeo do app
status: draft
updated: 2026-08-23
parents: []
related: [REQ-001, ARCH, AYD-001, AYD-002]
superseded_by: null
---

# ADR-003: Stack de vídeo do app

> **Decisão deliberadamente adiada.** Este ADR existe para registrar *por que* ainda não
> foi decidido, e o que exatamente vai decidi-lo. Um ADR que declara a própria incerteza
> vale mais do que um palpite bem escrito.

## Contexto
`AVPlayer` não fala `RTSP`. As opções de engine (AYD-002) diferem em latência, tamanho,
licença e — o que pesa mais — em **quanta infraestrutura exigem fora do app**. A escolha
certa depende de um fato que ainda não temos: qual protocolo a `Camera` aceita (AYD-001).

Decidir agora seria escolher entre três apostas cujo custo de erro é reescrever a camada
de vídeo inteira.

## Decisão
**Pendente.** Este ADR sai de `draft` quando o `Probe` (SPEC-001) tiver rodado. O veredito
mapeia diretamente para uma escolha já analisada:

| Veredito do `Probe` | Stack que passa a valer | Consequência principal |
|---------------------|--------------------------|------------------------|
| **A** — RTSP + ONVIF | VLCKit no app, falando direto com a `Camera`; `PTZ` por SOAP ONVIF | Menos peças; latência 1–3 s; nenhuma `Bridge` necessária |
| **B** — RTSP sem ONVIF | `Bridge` (go2rtc ou MediaMTX) no `Home Node` reempacotando para WebRTC | Latência < 500 ms; `PTZ` vira problema separado (AYD-003) |
| **C** — só cloud P2P | API da `Vendor Cloud`, vídeo via HLS/RTSP temporário em `AVPlayer` | Sem `Home Node`; em troca, dependência de fornecedor — reabrir RN-02 antes de aceitar |

Enquanto isso, o compromisso que **já está tomado** e não depende do veredito: o app
isola o transporte atrás do contrato `StreamSource` (AYD-002). É o que permite adiar esta
decisão sem parar o projeto — e trocar de caminho depois sem reescrever a UI.

## Alternativas consideradas
Ver a tabela de engines em AYD-002 (VLCKit · `Bridge` WebRTC · HLS/`AVPlayer` · FFmpeg
próprio), com latências e trade-offs. Elas não são repetidas aqui porque ainda não foram
descartadas — nenhuma pode ser, antes do `Probe`.

## Consequências / trade-offs
- **Positivas:** nenhuma engine é adotada por engano; a F1 do roadmap começa sabendo o que
  construir.
- **Negativas:** o projeto fica bloqueado até alguém estar fisicamente na rede de casa
  para rodar o `Probe`. É um bloqueio de minutos, não de dias — e barato perto de
  reescrever a camada de vídeo.
- **Impacto:** AYD-002, ROAD-001 (marco M0 → M1).
