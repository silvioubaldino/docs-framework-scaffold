---
id: SPEC-002
type: spec
title: Guardrails determinísticos (hooks PreToolUse)
status: draft               # draft → review → approved (congela) — ver CLAUDE.md, Lifecycle
updated: 2026-07-19
parents: [AYD-002]
children: []
related: [SPEC-001]         # reusa os checks do validador
---

# Spec: Guardrails determinísticos (SPEC-002 de AYD-002)

> Detalha O QUÊ este PR entrega para cumprir o AYD-002. Congela ao virar `approved`.
> **Meta-SPEC temporária** — removida junto com AYD-002 ao fim do ciclo.

## Objetivo

Impedir, de forma **determinística** (sem depender de a IA "lembrar" da regra), as três
violações que mais custam caro no framework: editar o espelho read-only, alterar um doc
congelado, e rodar git destrutivo sem aprovação humana. Isso vira **hooks PreToolUse** do
Claude Code nos dois templates. Materializa o princípio "regra crítica vira código, não
prosa" — e por isso **abre um ADR** justificando a decisão.

## Critérios de aceite

```gherkin
# AC-1
Cenário: bloquear escrita no espelho read-only
  Dado uma chamada Edit ou Write cujo file_path casa `*/docs/shared/**`
  Quando o hook PreToolUse roda
  Então termina com exit 2
  E o stderr explica SHARED_READONLY (o contexto só muda no context-repo)

# AC-2
Cenário: bloquear edição de doc congelado
  Dado uma chamada Edit cujo alvo tem frontmatter `status: approved` ou `status: superseded`
  Quando o hook PreToolUse roda
  Então termina com exit 2
  E o stderr explica FROZEN_DOC e como reabrir (novo PR / supersede)

# AC-3
Cenário: exigir aprovação humana para git destrutivo
  Dado uma chamada Bash contendo `git push`, `git reset --hard` ou `--force`/`-f`
  Quando o hook PreToolUse roda
  Então termina com exit 2
  E o stderr explica GIT_SAFETY (pedir confirmação humana explícita)

# AC-4
Cenário: operação legítima passa
  Dado uma Edit/Write fora de docs/shared e em doc não-congelado,
        ou um Bash git não-destrutivo
  Quando o hook PreToolUse roda
  Então termina com exit 0 sem mensagem

# AC-5
Cenário: fiação nos dois templates
  Dado os templates context-repo e service-repo
  Quando inspeciono `.claude/settings.json`
  Então há um matcher PreToolUse "Edit|Write" e um "Bash" apontando para os hooks
```

## Contratos consumidos/expostos

- **Expõe/implementa C2 — Hook decision contract** (AYD-002): `.claude/hooks/*.sh`
  (PreToolUse), stdin = JSON do evento, `exit 0` allow / `exit 2` block com razão no stderr;
  regras mínimas SHARED_READONLY, FROZEN_DOC, GIT_SAFETY. Não redefine C2.
- **Consome SPEC-001 (C1):** a detecção de `status` congelado (AC-2) reusa o parser de
  frontmatter do validador — extrair como função/lib compartilhada, não duplicar YAML parsing.

## Modelo de dados / componentes afetados

- `.claude/hooks/block-shared-edit.sh`, `block-frozen-doc.sh`, `git-safety.sh` (novos) nos
  dois templates — ou um dispatcher único por evento. Usam `jq` sobre `.tool_input.file_path`
  / `.tool_input.command`.
- `.claude/settings.json` (novo/editado): matchers `PreToolUse` para `Edit|Write` e `Bash`.
- Lib compartilhada de leitura de frontmatter (origem: SPEC-001).

## Casos de borda & fora de escopo

- **Borda:** `jq` ausente no ambiente → o hook deve falhar **aberto** (exit 0) com aviso, para
  não travar o trabalho por falta de dependência; documentar essa escolha no ADR.
- **Borda:** caminho relativo vs absoluto no `file_path` — normalizar antes de casar o glob.
- **Borda:** `git push` legítimo — o bloqueio é intencional; o humano aprova e reexecuta. Não
  criar bypass silencioso.
- **Fora:** hooks PostToolUse, secret-scan, command-safety amplo — este PR cobre só as 3
  regras mínimas de C2. Demais guardrails são evolução futura.
- **Fora:** portar os hooks para Cursor/Copilot (adapters) — fora de escopo do AYD-002.

## Decisão a registrar (ADR neste PR)

"Regras críticas de segurança do grafo viram hooks determinísticos, não prosa nas
convenções." Registrar como ADR no context-repo, incluindo a política de *fail-open* quando
falta dependência (jq).
