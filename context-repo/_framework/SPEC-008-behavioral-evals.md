---
id: SPEC-008
type: spec
title: Evals comportamentais da cascade e dos agentes
status: review               # draft → review → approved (congela) — ver CLAUDE.md, Lifecycle
updated: 2026-07-21
parents: [AYD-002]
children: []
related: [SPEC-004]         # os evals exercitam o gate ALIGN e a triagem da cascade
---

# Spec: Evals comportamentais (SPEC-008 de AYD-002)

> Detalha O QUÊ este PR entrega para cumprir o AYD-002. Congela ao virar `approved`.
> **Meta-SPEC temporária** — removida junto com AYD-002 ao fim do ciclo.

## Objetivo

Impedir regressão silenciosa de **comportamento** quando skills/agents mudam. As convenções
determinísticas já têm validador (SPEC-001) e hooks (SPEC-002); falta cobrir o que é
**julgamento** — a cascade classifica o nível certo? Pára no ALIGN quando deve? Só faz fan-out
cross-repo? Este PR entrega uma pasta `evals/` com **casos de replay**: entrada (pedido +
estado do repo) → comportamento esperado (nível de triagem, se dispara ALIGN, se faz fan-out,
quais docs toca). Rodados quando skills ou agentes mudam. Verifica o julgamento sem depender de
um humano reler o prompt a cada edição.

## Critérios de aceite

```gherkin
# AC-1
Cenário: pasta de evals com casos declarativos
  Dado o context-repo
  Quando inspeciono `evals/`
  Então existem casos de replay, cada um com entrada (pedido + contexto mínimo) e
        comportamento esperado (nível de triagem, ALIGN sim/não, fan-out sim/não, docs tocados)
  E o formato do caso está documentado (header/README da pasta)

# AC-2
Cenário: eval do gate de triagem
  Dado um caso "typo num doc vivo"
  Quando o eval roda
  Então o comportamento esperado é nível 0, sem ALIGN e sem fan-out

# AC-3
Cenário: eval do gate ALIGN
  Dado um caso "criar/alterar um Contrato num AYD"
  Quando o eval roda
  Então o comportamento esperado inclui PARAR no ALIGN antes de escrever o contrato (SPEC-004)

# AC-4
Cenário: eval de fan-out cross-repo
  Dado um caso "AYD que afeta 2 repos"
  Quando o eval roda
  Então o comportamento esperado é nível 3 com fan-out (um spec-author por repo) após ALIGN

# AC-5
Cenário: runner reporta pass/fail por caso
  Dado o conjunto de evals
  Quando rodo o runner
  Então cada caso reporta pass/fail com o esperado × observado
  E ao menos uma divergência resulta em exit ≠ 0 (falha o build/o passo)

# AC-6
Cenário: evals rodam quando skills/agents mudam
  Dado uma alteração em `.claude/skills/**` ou `.claude/agents/**`
  Quando o processo de review roda (local ou CI)
  Então os evals são executados antes de aprovar a mudança
```

## Contratos consumidos/expostos

- **Não define contrato-letra.** Entrega um harness de teste de comportamento.
- **Consome SPEC-004:** os casos afirmam o comportamento do gate ALIGN e da triagem — se a
  SPEC-004 mudar o protocolo, os evals são a rede de segurança.
- **Reusa C1 — Validator exit contract** para o padrão de saída do runner: uma linha por caso,
  `SEVERITY | CASE_ID | expected≠observed`, exit ≠ 0 em divergência — consistente com o
  validador, não um formato novo.

## Modelo de dados / componentes afetados

- `context-repo/evals/` (novo): casos de replay + README com o formato do caso.
- Runner (novo): script que lê os casos, executa/replaya e compara esperado × observado,
  reportando no padrão de C1.
- Fiação de review: hook/CI (ver questão aberta abaixo) que dispara os evals quando
  `.claude/skills/**` ou `.claude/agents/**` mudam.

## Casos de borda & fora de escopo

- **Borda:** comportamento de LLM é não-determinístico → o caso afirma **decisões estruturais**
  (nível, ALIGN, fan-out, docs tocados), não texto literal; tolerância definida no formato do
  caso para não gerar falso-negativo por variação de redação.
- **Borda:** eval que exige despachar subagentes de verdade custaria caro → o replay deve poder
  checar a **decisão** de fan-out sem necessariamente pagar o fan-out completo.
- **Fora:** avaliar qualidade de prosa gerada / métricas de "quão boa" é a SPEC — aqui o eval é
  binário de comportamento (fez a coisa certa de processo), não juiz de conteúdo.
- **Fora:** framework de eval de terceiros (promptfoo etc.) — decisão de implementação do PR;
  a SPEC exige o comportamento, não a ferramenta.
- **Aberto (herdado do AYD-002):** rodar manualmente ou em CI — decidir neste PR.
