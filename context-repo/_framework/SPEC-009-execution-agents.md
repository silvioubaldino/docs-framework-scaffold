---
id: SPEC-009
type: spec
title: Agentes de execução (implementer + qa-reviewer)
status: draft               # draft → review → approved (congela) — ver CLAUDE.md, Lifecycle
updated: 2026-07-19
parents: [AYD-002]
children: []
related: [SPEC-005]         # o qa-reviewer valida código contra os AC-N (C4)
---

# Spec: Agentes de execução (SPEC-009 de AYD-002)

> Detalha O QUÊ este PR entrega para cumprir o AYD-002. Congela ao virar `approved`.
> **Meta-SPEC temporária** — removida junto com AYD-002 ao fim do ciclo.

## Objetivo

Fechar o ciclo do requisito ao **código verificado**: hoje o framework vai bem do REQ à SPEC,
mas a ponta "SPEC → implementação → conferência" fica solta. Este PR entrega dois agentes no
service-repo: um **`implementer`** que executa um PLAN (lê a stack do repo, escreve código,
**nunca** muda contrato) e um **`qa-reviewer`** (read-only) que valida o código contra os
`AC-N` da SPEC (C4/SPEC-005). Para os dois lerem a stack de um ponto único, este PR **formaliza
a seção de stack no `CLAUDE.md` do service-repo** como a fonte canônica (linguagem, framework,
comandos de build/test, convenções). Materializa a separação de papéis: contrato só muda no
context-repo; o serviço implementa e confere.

## Critérios de aceite

```gherkin
# AC-1
Cenário: agente implementer existe com escopo claro
  Dado o template service-repo
  Quando inspeciono `.claude/agents/`
  Então existe `implementer` que implementa um PLAN, lê a stack do CLAUDE.md do repo
  E sua descrição PROÍBE alterar contrato (AYD/ADR/SPEC) — só implementa

# AC-2
Cenário: agente qa-reviewer é read-only e ancorado nos AC
  Dado o template service-repo
  Quando inspeciono `.claude/agents/`
  Então existe `qa-reviewer` read-only (não escreve código)
  E ele valida o código contra os `AC-N` da SPEC, referenciando `SPEC-NNN/AC-N` (C4)

# AC-3
Cenário: seção de stack canônica no CLAUDE.md do serviço
  Dado o `CLAUDE.md` do template service-repo
  Quando inspeciono suas seções
  Então há uma seção de stack única (linguagem, framework, build/test, convenções)
  E implementer e qa-reviewer apontam para ela como fonte (não duplicam a stack)

# AC-4
Cenário: qa-reviewer acusa AC não coberto pelo código
  Dado uma SPEC com `AC-3` e código que não o satisfaz
  Quando o qa-reviewer roda
  Então reporta `AC-3` como não atendido, citando `SPEC-NNN/AC-3`
  E não altera nenhum arquivo (read-only)

# AC-5
Cenário: implementer não redefine contrato
  Dado um PLAN cuja execução "exigiria" mudar um contrato
  Quando o implementer detecta isso
  Então PARA e devolve a necessidade de mudança de contrato para o context-repo (AYD/ADR)
  E não escreve a mudança de contrato ele mesmo
```

## Contratos consumidos/expostos

- **Não define contrato-letra.** Entrega dois agentes + formaliza a seção de stack do serviço.
- **Consome SPEC-005 (C4):** o `qa-reviewer` usa os `AC-N` e a referência `SPEC-NNN/AC-N` como
  base da conferência — o mesmo namespace que o validador cruza em SPEC-005.
- **Respeita a regra core do framework:** contrato só muda no context-repo; o `implementer`
  implementa e o `qa-reviewer` confere, nenhum redefine contrato.

## Modelo de dados / componentes afetados

- `service-repo/.claude/agents/implementer.md` (novo): modelo forte o suficiente para código;
  lê PLAN + stack do CLAUDE.md; proíbe edição de contrato.
- `service-repo/.claude/agents/qa-reviewer.md` (novo): read-only; entrada = SPEC + código;
  saída = relatório AC-a-AC (`SPEC-NNN/AC-N` atendido/não).
- `service-repo/CLAUDE.md` (editado): seção de stack canônica (ponto único de verdade de stack).
- `service-repo/docs/conventions/` (se necessário): apontar os agentes para as convenções
  existentes em vez de reescrevê-las.

## Casos de borda & fora de escopo

- **Borda:** SPEC ainda em `draft` sem AC estável → o qa-reviewer avisa que a base de aceite
  não está congelada (revisar contra alvo móvel gera ruído); conferência dura só faz sentido
  com a SPEC `approved`.
- **Borda:** stack não declarada no CLAUDE.md → o implementer deve pedir/inferir com cautela e
  registrar a lacuna, não chutar silenciosamente.
- **Borda:** qa-reviewer encontra AC atendido só parcialmente → reportar como não atendido
  (binário por AC), com a evidência do que falta.
- **Fora:** o implementer abrir PR / rodar o CI / fazer deploy — ele produz o código; o
  pipeline do serviço cuida do resto.
- **Fora:** qa-reviewer **rodar** os testes (isso é CI) — ele confere se o código satisfaz os
  AC e se há teste declarando cobrir cada AC; execução é responsabilidade do CI (ver SPEC-005).
