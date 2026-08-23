---
id: ROAD-001
type: roadmap
title: Roadmap
status: draft
updated: 2026-08-23
parents: []
children: []
related: [REQ-001, AYD-001, AYD-002, AYD-003, AYD-004]
---

# Roadmap & Planejamento

Princípio: **cada fase entrega algo usável sozinha.** Se o projeto parar na F1, o dono já
ganhou um app sem anúncios para ver a câmera em casa — o que já resolve boa parte da dor.

## Now / Next / Later
| Horizonte | Tema | Entregáveis | Requisitos (RF) | Depende de |
|-----------|------|-------------|-----------------|------------|
| **Now** | **F0 · Descoberta** | Rodar o `Probe` na LAN, registrar o resultado, fechar ADR-003 e escolher o caminho A/B/C | — | nada (só estar em casa) |
| **Next** | **F1 · Ver a câmera em casa** | App iOS mínimo: uma tela, o `Stream` ao vivo, credenciais no Keychain | RF-01, RF-04, RF-05 | F0 |
| **Next** | **F2 · Girar a câmera** | Controles `PTZ` na tela: `ContinuousMove` ao pressionar, `Stop` ao soltar | RF-02 | F1 |
| **Next** | **F3 · Fora de casa** | `Home Node` + `Mesh VPN` configurados; app funcionando em 4G/5G | RF-03 | F2, hardware do `Home Node` |
| **Later** | **F4 · Conforto** | `Preset`, snapshot, reconexão mais esperta, paisagem/tela cheia refinada | RF-06, RF-07 | F3 |
| **Later** | **F5 · Extras** | Áudio, múltiplas câmeras, Picture in Picture, widget | RF-08, RF-09 | F4 |

## Marcos
| Marco | Critério de "pronto" | Dependências |
|-------|----------------------|--------------|
| **M0 — Protocolo conhecido** | `tools/probe_camera.py` rodado; veredito A/B/C registrado em AYD-001; ADR-003 sai de `draft` | Estar na mesma rede da câmera |
| **M1 — Primeira imagem** | O vídeo da câmera aparece no iPhone, em casa, num app instalado pelo Xcode | M0 |
| **M2 — Primeiro movimento** | Segurar o botão gira a câmera; soltar para | M1 |
| **M3 — Adeus app de fábrica** | Vídeo + PTZ funcionam com o iPhone em 4G, longe de casa; o app antigo pode ser desinstalado | M2, `Home Node` ligado |
| **M4 — Convivência** | App assinado com a conta paga, sobrevive ≥ 1 ano sem reinstalar | M3 |

## Custos & riscos (resumo)
| Item | Tipo | Estimativa / Mitigação |
|------|------|------------------------|
| Câmera não fala RTSP nem ONVIF (caminho C) | **Risco alto** | É o risco que mata o projeto na forma desejada. Mitigação: o `Probe` (F0) responde isso **antes** de escrever qualquer linha de Swift. Plano B em AYD-004. |
| Não existe `Home Node` sempre ligado em casa | **Risco alto** | Bloqueia F3 nos caminhos A e B. Mitigação: um Raspberry Pi Zero 2 W ou qualquer mini PC/NAS resolve; decidir cedo, na F0. |
| `Home Node` (se precisar comprar) | Custo | ~R$ 200–500 uma vez (Raspberry Pi). R$ 0 se já houver NAS, mini PC ou Mac ligado. |
| Conta Apple Developer | Custo | US$ 99/ano — **já paga** |
| Mesh VPN | Custo | R$ 0 (Tailscale grátis para uso pessoal, ou WireGuard puro) |
| PTZ proprietário exigindo engenharia reversa | **Risco médio** | Caminho B. Mitigação: F1 e F2 são independentes — dá para ter vídeo sem PTZ e seguir. |
| Latência ruim com RTSP+VLCKit | Risco baixo | Aceitável no MVP (RNF-01/02). Se incomodar, a `Bridge` WebRTC do caminho B derruba para < 500 ms. |
| Firmware white-label sem documentação | Risco médio | Nenhuma garantia de estabilidade entre atualizações de firmware. Mitigação: não atualizar o firmware sem necessidade. |
| Tempo de hobby / desenvolvedor solo | Risco médio | Fases curtas e úteis isoladamente; nada de big bang. |
