---
id: AYD-NNN
type: design
title: 
status: draft
updated: 2025-01-01
parents: [REQ-NNN]
children: []               # SPECs geradas, ex.: [SPEC-NNN@api, SPEC-NNN@web]
related: [GLO]
---

# AYD-NNN: <feature>

> Análise & Design cross-repo. Decide QUAIS repos a feature toca, o PAPEL de cada um
> e os CONTRATOS entre eles. Daqui nascem N SPECs (uma por repo afetado).

## Objetivo
_Que requisito (REQ) esta feature atende e qual o resultado esperado._

## Repos afetados e papéis
| Repo | Papel nesta feature | SPEC gerada |
|------|---------------------|-------------|
| api    | _expõe/serve…_ | SPEC-NNN@api |
| web    | _consome/exibe…_ | SPEC-NNN@web |
| mobile | _consome/…_ | SPEC-NNN@mobile |

## Contratos (fonte da verdade)
_Endpoints, payloads, eventos, modelos compartilhados. Quem muda isto muda AQUI._
```
POST /recurso
req:  { ... }
res:  { ... }
erros: [ ... ]
```

## Modelo de domínio afetado
_Entidades/campos (usar termos do GLO)._

## Fluxo cross-repo
_Sequência ponta a ponta envolvendo os repos (ex.: mobile → api → web)._

```mermaid
sequenceDiagram

```

## Decisões relacionadas
_ADR/PDR citados (em `related`). Decisão nova de contrato → cria um ADR._

## Fora de escopo / questões em aberto
- 
