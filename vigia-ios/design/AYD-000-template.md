---
id: AYD-NNN
type: design
title: 
status: draft
updated: 2026-01-01
parents: [REQ-001]
children: []               # SPECs geradas, ex.: [SPEC-NNN]
related: [GLO]
---

# AYD-NNN: <feature>

> Análise & Design de uma feature. Decide QUAIS componentes ela toca, o PAPEL de cada um
> e os CONTRATOS entre eles. Daqui nascem as SPECs. Documento **vivo**.

## Objetivo
_Que requisito (RF/RNF) esta feature atende e qual o resultado esperado para o dono._

## Componentes afetados e papéis
| Componente | Papel nesta feature | SPEC gerada |
|------------|---------------------|-------------|
| Vigia (app iOS) | _exibe/comanda…_ | SPEC-NNN |
| Camera | _fornece…_ | — |
| Home Node | _intermedia…_ | — |

## Contratos (fonte da verdade)
_Chamadas, payloads, formatos. Quem muda isto muda AQUI, não na SPEC._
```
<protocolo/endpoint>
req:  { ... }
res:  { ... }
erros: [ ... ]
```

## Modelo de domínio afetado
_Entidades/campos, usando os termos do GLO._

## Fluxo
```mermaid
sequenceDiagram
```

## Decisões relacionadas
_ADR citados (em `related`). Decisão nova de contrato → cria um ADR._

## Fora de escopo / questões em aberto
- 
