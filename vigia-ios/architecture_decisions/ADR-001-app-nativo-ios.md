---
id: ADR-001
type: adr
title: App nativo iOS em Swift/SwiftUI
status: review
updated: 2026-08-23
parents: []
related: [REQ-001, ARCH, AYD-002]
superseded_by: null
---

# ADR-001: App nativo iOS em Swift/SwiftUI

## Contexto
O produto tem uma superfície só — o iPhone do dono (RN-01) — e duas exigências técnicas
que pesam mais que qualquer preferência de linguagem:

1. **Vídeo ao vivo com engine de terceiro.** Nos caminhos A e B, é preciso hospedar uma
   camada de vídeo nativa (VLCKit, WebRTC) e conectá-la a uma view. Toda camada de
   framework cross-platform entre a UI e essa engine vira um ponto de atrito.
2. **Zero dependência que faça rede por conta própria** (RNF-04). O ecossistema JS/npm é
   justamente onde SDKs de analytics entram sem convite, por dependência transitiva.

Some-se que o dono tem conta Apple Developer paga e não pretende publicar na loja: não há
argumento de alcance multiplataforma para pagar o preço da abstração.

## Decisão
O Vigia é um app **nativo iOS**, escrito em **Swift 6 com SwiftUI**, alvo **iOS 17+**,
distribuído por assinatura de desenvolvedor para o dispositivo do dono.

A regra de dependências é restritiva: entram no projeto apenas bibliotecas de mídia e
criptografia sem back-end próprio. Rede, autenticação, `PTZ` e persistência usam a
biblioteca padrão (`URLSession`, Keychain, `SwiftData`/`UserDefaults`). Zero SDK de
analytics, publicidade ou crash reporting de terceiro.

## Alternativas consideradas
| Opção | Prós | Contras | Por que (não) escolhida |
|-------|------|---------|-------------------------|
| **Swift + SwiftUI (nativo)** | Acesso direto a `AVFoundation`, `VideoToolbox`, Keychain, `NetworkExtension`; menos camadas entre UI e vídeo; superfície de dependência mínima | Só iOS | **Escolhida** — a única plataforma alvo é iOS, então "só iOS" não é custo |
| React Native / Expo | Ecossistema grande; reaproveitável para Android | Player RTSP exige módulo nativo de qualquer jeito — a abstração não abstrai nada aqui; árvore npm difícil de auditar contra RNF-04 | Rejeitada: paga complexidade por portabilidade que ninguém pediu |
| Flutter | Boa performance de UI; multiplataforma | Mesmo problema de vídeo, com uma camada a mais (platform channels) entre a view e a engine | Rejeitada |
| PWA / app web | Nenhuma assinatura, nenhum Xcode | Sem RTSP no navegador; sem tela cheia decente; sem Keychain; sem background bem resolvido | Rejeitada: não atende RF-01 |
| Só usar o app do Home Assistant | Custo zero de desenvolvimento; PTZ pronto para muitas câmeras | Não é um app de câmera, é um painel; a experiência de "abrir e ver" some; instala um servidor inteiro para uma tela | Rejeitada como produto — mas segue viva como **ponte** técnica no caminho B (AYD-003) |

## Consequências / trade-offs
- **Positivas:** menos camadas, acesso direto ao que importa (Keychain, mídia, rede local),
  auditoria de dependências trivial, e o app fica pequeno e rápido.
- **Negativas:** nasce preso ao iOS — um Android futuro é reescrita, não port. Aceitável:
  o produto é para um dono, com um telefone.
- **Negativas:** build e teste exigem macOS + Xcode + iPhone físico. Nenhum ambiente de CI
  genérico substitui isso, e o ciclo de feedback fica mais lento que um projeto web.
- **Impacto:** ARCH (container "Vigia"), AYD-002 (a camada `StreamSource` é Swift),
  AYD-003 (o `PTZController` é Swift).
