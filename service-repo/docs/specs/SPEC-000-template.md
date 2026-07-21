---
id: SPEC-NNN
type: spec
title: 
status: draft               # draft → review → approved (congela) — ver docs/shared/CLAUDE.md, Lifecycle
updated: 2025-01-01
parents: [AYD-NNN@context]   # obrigatório: o AYD que originou esta spec
children: []                # PLAN correspondente
related: [GLO]              # ADR/TDR relevantes
---

# Spec: <feature> (parte deste repo)

> Detalha O QUÊ este repo faz para cumprir o AYD. Congela ao virar `approved`.

## Objetivo
_O papel deste repo nesta feature (conforme o AYD)._

## Critérios de aceite
> Cada Cenário tem um id `AC-N` (comentário `# AC-N` na linha acima do Cenário). Todo teste
> que cobrir um cenário referencia `SPEC-NNN/AC-N` (ex.: `SPEC-012/AC-1`) no nome, tag ou
> comentário — legível por humano e por grep. Esta SPEC só vira `approved` quando todo `AC-N`
> tiver ≥1 teste referenciando-o (regra `AC_WITHOUT_TEST` do validador — ver
> `docs/shared/CLAUDE.md`, Lifecycle).
```gherkin
# AC-1
Cenário: <nome>
  Dado <contexto>
  Quando <ação>
  Então <resultado observável>
```

## Contratos consumidos/expostos
_Referencie os contratos do AYD. Este repo NÃO os redefine._

## Modelo de dados / componentes afetados
- 

## Casos de borda & fora de escopo
- Borda:
- Fora:
