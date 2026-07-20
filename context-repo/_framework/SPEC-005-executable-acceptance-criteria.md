---
id: SPEC-005
type: spec
title: Critérios de aceite executáveis (AC-N ↔ teste)
status: draft               # draft → review → approved (congela) — ver CLAUDE.md, Lifecycle
updated: 2026-07-19
parents: [AYD-002]
children: []
related: [SPEC-001]         # liga a regra AC_WITHOUT_TEST no validador
---

# Spec: Critérios de aceite executáveis (SPEC-005 de AYD-002)

> Detalha O QUÊ este PR entrega para cumprir o AYD-002. Congela ao virar `approved`.
> **Meta-SPEC temporária** — removida junto com AYD-002 ao fim do ciclo.

## Objetivo

Fechar a ponta "spec → teste" do ciclo: cada cenário Gherkin da SPEC recebe um id `AC-N`, cada
teste referencia `SPEC-NNN/AC-N`, e uma SPEC **só vira `approved` quando todo AC-N tem ao menos
um teste**. Isso torna o critério de aceite **verificável por máquina** — a regra
`AC_WITHOUT_TEST` do validador (definida como desativada na SPEC-001) é **ligada** aqui. Sem
isso, "critério de aceite" continua sendo prosa que ninguém confere. Materializa C4.

## Critérios de aceite

```gherkin
# AC-1
Cenário: template de SPEC carrega ids AC-N
  Dado o template `service-repo/docs/specs/SPEC-000-template.md`
  Quando inspeciono a seção de critérios de aceite
  Então cada Cenário Gherkin tem um id `AC-N` (comentário na linha do Cenário)
  E o template explica a convenção de referência `SPEC-NNN/AC-N` no teste

# AC-2
Cenário: teste referencia o AC que cobre
  Dado um teste que cobre um cenário
  Quando inspeciono seu nome/tag/comentário
  Então há uma referência `SPEC-NNN/AC-N` legível por humano e por grep

# AC-3
Cenário: validador acusa AC sem teste
  Dado uma SPEC com `AC-3` que nenhum teste referencia
  Quando o validador (SPEC-001) roda com a regra AC_WITHOUT_TEST ativa
  Então emite `WARN | AC_WITHOUT_TEST | <spec>:<linha> | AC-3 sem teste`
  E, se a SPEC está `approved`, promove para `ERROR` (exit 1)

# AC-4
Cenário: approval exige cobertura total
  Dado uma SPEC prestes a virar `approved`
  Quando algum AC-N não tem teste referenciando-o
  Então a regra de lifecycle bloqueia a promoção a `approved`

# AC-5
Cenário: SPEC em draft/review não é penalizada
  Dado uma SPEC em `draft` ou `review` com ACs ainda sem teste
  Quando o validador roda
  Então emite no máximo WARN (não falha o build) — a cobrança dura só vale no `approved`
```

## Contratos consumidos/expostos

- **Implementa C4 — Acceptance-criteria ID contract** (AYD-002): `AC-N` na SPEC,
  `SPEC-NNN/AC-N` no teste, approval condicionado a cobertura. Este PR define a mecânica de C4;
  não redefine C1.
- **Consome SPEC-001 (C1):** liga a regra `AC_WITHOUT_TEST` já reservada no enum de RULE_IDs.
  A varredura de testes (qual `SPEC-NNN/AC-N` aparece no código) é adicionada ao validador
  como fonte para essa regra — reusando o parser/índice existente, não um script novo.

## Modelo de dados / componentes afetados

- `service-repo/docs/specs/SPEC-000-template.md` (editado): ids `AC-N` nos cenários + nota da
  convenção de referência no teste.
- `service-repo/docs/conventions/testing.md` (editado): formaliza "todo AC-N tem ≥1 teste que o
  referencia" como regra de aceite, com o formato da referência.
- Validador (SPEC-001) estendido: coleta `SPEC-NNN/AC-N` das SPECs e dos testes, cruza, e
  emite `AC_WITHOUT_TEST` (WARN em draft/review, ERROR em approved).
- `CLAUDE.md` (editado): a regra de lifecycle "SPEC só vira approved com todo AC coberto".

## Casos de borda & fora de escopo

- **Borda:** um AC coberto por vários testes → ok (≥1 basta). Um teste cobrindo vários ACs →
  pode referenciar múltiplos `SPEC-NNN/AC-N`.
- **Borda:** AC removido/renumerado numa revisão da SPEC → testes órfãos apontando para AC
  inexistente devem ser sinalizados (reuso de `BROKEN_REF` do C1 no namespace AC).
- **Borda:** onde os testes vivem varia por stack → o validador acha a referência por
  **conteúdo** (`SPEC-NNN/AC-N` como string), não por caminho fixo; documentar.
- **Fora:** rodar os testes / medir cobertura de linha — o check é "existe teste que declara
  cobrir este AC", não "o teste passa". Execução é responsabilidade do CI de cada serviço.
- **Fora:** gerar testes automaticamente a partir do Gherkin — fora do escopo deste ciclo.
