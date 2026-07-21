---
id: EVAL-003
title: AYD cross-repo com fan-out (nível 3)
expected_level: 3
expected_align_contrato: true
expected_align_fanout: true
expected_fanout: true
expected_docs_touched: [AYD-novo, SPEC-novo@api, SPEC-novo@web]
---

## Pedido

> "Cria o AYD de login social (Google): a API precisa de um novo endpoint de callback e o Web
> precisa de um novo botão e fluxo de redirect."

## Contexto mínimo

- Os repos-irmãos `api` e `web` existem no workspace (§6 da skill `cascade`).
- A tabela "Repos afetados e papéis" do AYD listaria os dois repos.

## Comportamento esperado

Nível 3 (§1): AYD cross-repo, mais de um repo na tabela "Repos afetados e papéis". Protocolo
completo (§4): CONTRATO → **ALIGN-Contrato** (obrigatório, antes de gravar o AYD) → MAPA DE
IMPACTO → **ALIGN-FanOut** (obrigatório, antes de despachar) → FAN-OUT com 2 `spec-author` em
paralelo (um por repo: `api`, `web`) → RECONCILIAÇÃO → PROPAGAÇÃO. Os dois checkpoints de
ALIGN (SPEC-004/AC-2) ocorrem nesta cascata.

## Observado

<!-- Preenchido pelo replay: peça à cascade para SÓ triar este pedido (sem executar) e
     reporte os campos abaixo. Deixe em branco até o replay acontecer — o runner reporta
     PENDING nesse caso, sem falhar o build. -->

---
observed_level: 3
observed_align_contrato: true
observed_align_fanout: true
observed_fanout: true
observed_docs_touched: [AYD-novo, SPEC-novo@api, SPEC-novo@web]
---
