---
id: SPEC-004
type: spec
title: Gate ALIGN obrigatório na cascade
status: review               # draft → review → approved (congela) — ver CLAUDE.md, Lifecycle
updated: 2026-07-21
parents: [AYD-002]
children: []
related: []                 # sem dependência — paralelizável com SPEC-001/003/006
---

# Spec: Gate ALIGN na cascade (SPEC-004 de AYD-002)

> Detalha O QUÊ este PR entrega para cumprir o AYD-002. Congela ao virar `approved`.
> **Meta-SPEC temporária** — removida junto com AYD-002 ao fim do ciclo.

## Objetivo

Impedir que a cascade crie ou altere **contrato** (AYD/ADR/PDR) ou faça **fan-out** de
subagentes sem uma **aprovação humana explícita** registrada. Hoje a skill "geralmente" pede
confirmação; este PR transforma isso em um **passo obrigatório e nomeado** (ALIGN) no protocolo
da cascade — o ponto onde julgamento humano entra antes de gastar tokens ou congelar decisões.
É a contraparte de julgamento dos guardrails determinísticos (SPEC-002): o que exige decisão
humana vira gate explícito; o que é regra mecânica vira hook.

## Critérios de aceite

```gherkin
# AC-1
Cenário: contrato novo/alterado exige ALIGN antes de escrever
  Dado um pedido que cria ou altera um Contrato num AYD/ADR/PDR
  Quando a cascade chega ao passo CONTRATO
  Então ela PARA e apresenta o contrato proposto para aprovação humana
  E só escreve o doc após "aprovado" explícito do humano

# AC-2
Cenário: fan-out exige ALIGN antes de despachar subagentes
  Dado uma triagem nível 3 (cross-repo) que dispararia fan-out
  Quando a cascade chega ao passo FAN-OUT
  Então ela PARA e apresenta o plano de fan-out (repos, papéis, custo estimado)
  E só despacha os subagentes após aprovação humana

# AC-3
Cenário: mudança trivial não dispara o gate
  Dado uma triagem nível 0/1 (typo, wording, um doc vivo, ADR append-only simples)
  Quando a cascade processa
  Então NÃO exige o gate ALIGN (não há contrato novo nem fan-out)

# AC-4
Cenário: a decisão de ALIGN fica registrada
  Dado um ALIGN aprovado
  Quando a cascade prossegue
  Então registra no fecho (changelog/journal) que houve aprovação humana do contrato/fan-out
  E o quê foi aprovado (IDs afetados)
```

## Contratos consumidos/expostos

- **Não define contrato-letra** (C1–C5). Altera o **protocolo da skill cascade**: introduz o
  passo nomeado ALIGN entre triagem e escrita de contrato, e entre triagem e fan-out.
- Sem dependência de outras SPECs (paralelizável com SPEC-001/003/006).
- Sinergia com SPEC-006 (C5): o registro do AC-4 usa o journal quando ele existir; enquanto
  não existir, registra no changelog. Não cria dependência dura.

## Modelo de dados / componentes afetados

- `context-repo/.claude/skills/cascade/SKILL.md` (editado): o gate de triagem (§1) e o
  protocolo (§3) ganham o passo **ALIGN** explícito, com critério de quando é obrigatório
  (contrato novo/alterado OU fan-out) e quando é dispensado (nível 0/1 sem contrato).
- `CLAUDE.md` (editado, se necessário): uma linha no Lifecycle apontando que contrato só nasce
  após ALIGN — para a regra valer mesmo fora da skill.

## Casos de borda & fora de escopo

- **Borda:** ADR/PDR que apenas **registra** uma decisão já tomada (append-only, sem alterar
  contrato existente) — é nível 1; não exige o gate, mas o texto deve deixar claro o limite
  entre "registrar decisão" e "criar/alterar contrato".
- **Borda:** o humano recusa no ALIGN → a cascade aborta o passo sem escrever nada, sem estado
  parcial.
- **Fora:** aprovação assíncrona / múltiplos aprovadores / trilha de auditoria formal — aqui o
  ALIGN é uma confirmação síncrona na sessão. Workflow de aprovação robusto é evolução futura.
- **Fora:** transformar o ALIGN em hook determinístico — é julgamento humano por natureza;
  vive na skill, não em `.claude/hooks/`.
