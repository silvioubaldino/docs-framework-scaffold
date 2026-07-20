---
id: SPEC-001
type: spec
title: Validador de integridade do grafo de documentos
status: draft               # draft → review → approved (congela) — ver CLAUDE.md, Lifecycle
updated: 2026-07-19
parents: [AYD-002]           # meta-SPEC: parent no mesmo repo (o framework é o produto)
children: []                # PLAN correspondente (opcional neste ciclo)
related: []
---

# Spec: Validador de integridade do grafo (SPEC-001 de AYD-002)

> Detalha O QUÊ este PR entrega para cumprir o AYD-002. Congela ao virar `approved`.
> **Meta-SPEC temporária** — removida junto com AYD-002 ao fim do ciclo.

## Objetivo

Transformar a regra "o grafo de docs deve ser consistente" de prosa em **código
determinístico**: um script sem LLM que varre os docs (frontmatter + links) e falha quando o
grafo está quebrado. É a fundação das outras SPECs — os hooks (SPEC-002) reusam seus checks e
o critério `AC↔teste` (SPEC-005) adiciona uma regra a ele. Rodável local (pré-PR) e em CI.

## Critérios de aceite

```gherkin
# AC-1
Cenário: doc sem frontmatter obrigatório
  Dado um doc de tipo governado (design/spec/decision/...) sem os campos
        id/type/title/status/updated
  Quando o validador roda
  Então emite `ERROR | FRONTMATTER_MISSING | <file>:1 | <campo ausente>`
  E termina com exit 1

# AC-2
Cenário: assimetria parent/child
  Dado um doc A que lista B em `children`
  E o doc B que NÃO lista A em `parents`
  Quando o validador roda
  Então emite `ERROR | PARENT_CHILD_ASYMMETRY | <file de B>:<linha> | falta parent A`
  E termina com exit 1

# AC-3
Cenário: SPEC sem AYD de origem
  Dado um doc `type: spec` cujo `parents` não referencia nenhum `type: design`
  Quando o validador roda
  Então emite `ERROR | SPEC_WITHOUT_AYD | <file>:<linha> | spec sem AYD parent`
  E termina com exit 1

# AC-4
Cenário: status inválido
  Dado um doc cujo `status` não está no enum permitido
        (draft|review|approved|superseded|deprecated)
  Quando o validador roda
  Então emite `ERROR | INVALID_STATUS | <file>:<linha> | status <valor>`
  E termina com exit 1

# AC-5
Cenário: referência quebrada
  Dado um doc que referencia um ID (parents/children/related ou `ID@repo` no corpo)
        que não existe no grafo
  Quando o validador roda
  Então emite `ERROR | BROKEN_REF | <file>:<linha> | <ID> inexistente`
  E termina com exit 1

# AC-6
Cenário: grafo íntegro
  Dado um conjunto de docs sem violações
  Quando o validador roda
  Então não emite nenhuma linha em stdout
  E termina com exit 0

# AC-7
Cenário: formato de saída estável (contrato C1)
  Dado qualquer violação
  Quando o validador roda
  Então cada violação é UMA linha `SEVERITY | RULE_ID | file:line | message`
  E SEVERITY é ERROR ou WARN
  E a presença de ao menos um ERROR força exit 1 (WARN sozinho mantém exit 0)

# AC-8
Cenário: escopo por --repo-root
  Dado `--repo-root PATH`
  Quando o validador roda
  Então varre apenas os docs sob PATH (default: cwd)
```

## Contratos consumidos/expostos

- **Expõe C1 — Validator exit contract** (AYD-002): assinatura
  `scripts/validate.(sh|py) [--repo-root PATH]`, exit 0/1, linha
  `SEVERITY | RULE_ID | file:line | message`, RULE_IDs enumerados. Este PR **define** C1;
  não o redefine — futuras SPECs consomem como está.
- `AC_WITHOUT_TEST` faz parte do enum de RULE_IDs mas fica **desativado** (ou emitido só como
  WARN) até SPEC-005 introduzir os `AC-N`; documentar essa flag.

## Modelo de dados / componentes afetados

- `scripts/validate.*` (novo) — nos dois templates: `context-repo/scripts/` e
  `service-repo/docs/scripts/`. Decidir no PR se é um script único parametrizável ou um por
  template; preferência por **um só**, reusado (menos divergência).
- Parser de frontmatter YAML + índice de IDs em memória → detecção de assimetria e refs.
- Integração CI opcional: um passo que roda o validador e falha o build em exit 1.

## Casos de borda & fora de escopo

- **Borda:** doc com frontmatter malformado (YAML inválido) → tratar como
  `FRONTMATTER_MISSING`, nunca crashar. Templates com placeholders (`AYD-NNN`, `SPEC-NNN`)
  → ignorados por serem exemplos, não nós reais do grafo.
- **Borda:** `related` pode apontar para GLO/termos que não são docs — não tratar como
  `BROKEN_REF` se o alvo for um termo de glossário conhecido.
- **Fora:** validação semântica de conteúdo (se o texto "faz sentido") — só estrutura/grafo.
- **Fora:** auto-fix. O validador só reporta; correção é humana/IA num passo separado.
