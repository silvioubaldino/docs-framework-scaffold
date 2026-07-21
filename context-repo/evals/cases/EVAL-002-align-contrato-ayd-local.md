---
id: EVAL-002
title: Criar contrato num AYD (nível 2, 1 repo)
expected_level: 2
expected_align_contrato: true
expected_align_fanout: false
expected_fanout: false
expected_docs_touched: [AYD-novo, SPEC-novo@api]
---

## Pedido

> "Cria o AYD do fluxo de upload de mídia: define o contrato de payload entre o app e a API
> (endpoint, campos, limites de tamanho)."

## Contexto mínimo

- Só um repo de serviço é afetado (`api`).
- Nenhum AYD existente cobre upload de mídia — o contrato é novo.

## Comportamento esperado

Nível 2 (§1): AYD novo que afeta 1 repo. A cascade redige o AYD (contrato) e despacha 1
`spec-author` para a SPEC. Por criar contrato, o gate **ALIGN-Contrato** (§2) é obrigatório
**antes** de escrever o arquivo do AYD — só grava após aprovação humana explícita. Sem
fan-out: um único repo afetado não dispara o passo FAN-OUT (§4).

## Observado

<!-- Preenchido pelo replay: peça à cascade para SÓ triar este pedido (sem executar) e
     reporte os campos abaixo. Deixe em branco até o replay acontecer — o runner reporta
     PENDING nesse caso, sem falhar o build. -->

---
observed_level: 2
observed_align_contrato: true
observed_align_fanout: false
observed_fanout: false
observed_docs_touched: [AYD-novo, SPEC-novo@api]
---
