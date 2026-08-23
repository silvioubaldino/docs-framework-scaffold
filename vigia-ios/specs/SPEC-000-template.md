---
id: SPEC-NNN
type: spec
title: 
status: draft               # draft → review → approved (congela) — ver CLAUDE.md
updated: 2026-01-01
parents: [AYD-NNN]          # obrigatório: o AYD que originou esta spec
children: []
related: [GLO]
---

# SPEC-NNN: <o que será construído>

> Detalha O QUÊ construir para cumprir o AYD. **Congela** ao virar `approved`.

## Objetivo
_O recorte desta spec dentro do AYD._

## Critérios de aceite
> Cada cenário tem um id `AC-N` (comentário `# AC-N` na linha acima). Todo teste que
> cobrir um cenário cita `SPEC-NNN/AC-N` no nome ou num comentário — legível por humano
> e por `grep`. A spec só vira `approved` quando todo `AC-N` tiver ≥1 teste citando-o.

```gherkin
# AC-1
Cenário: <nome>
  Dado <contexto>
  Quando <ação>
  Então <resultado observável>
```

## Contratos consumidos/expostos
_Referencie os contratos do AYD. Esta spec NÃO os redefine._

## Componentes afetados
- 

## Casos de borda & fora de escopo
- Borda:
- Fora:
