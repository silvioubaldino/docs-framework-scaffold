---
id: TDR-001
type: tdr
title: Validação com biblioteca de schema (EXEMPLO)
status: accepted
updated: 2025-01-01
parents: []
related: [PLAN-001]
superseded_by: null
---

# TDR-001: Validação com biblioteca de schema (EXEMPLO)

## Contexto
Precisamos validar payloads de entrada de forma consistente neste serviço.

## Decisão
Adotar uma biblioteca de schema para validar requests na borda dos endpoints.

## Alternativas & trade-offs
- Validação manual: menos dependência, mais código repetitivo e propenso a erro.
- Decisão é **local**: não muda contrato, então é TDR (não ADR).
