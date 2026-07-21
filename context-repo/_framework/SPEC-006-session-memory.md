---
id: SPEC-006
type: spec
title: Memória de sessão leve (journal + state)
status: review              # draft → review → approved (congela) — ver CLAUDE.md, Lifecycle
updated: 2026-07-21
parents: [AYD-002]
children: []
related: []                 # sem dependência — paralelizável com SPEC-001/003/004
---

# Spec: Memória de sessão leve (SPEC-006 de AYD-002)

> Detalha O QUÊ este PR entrega para cumprir o AYD-002. Congela ao virar `approved`.
> **Meta-SPEC temporária** — removida junto com AYD-002 ao fim do ciclo.

## Objetivo

Dar continuidade entre sessões sem inchar o contexto: um **journal append-only** com uma linha
por sessão (o que foi feito, pendências, IDs tocados) e um **state sobrescrito** com o que está
em andamento (AYD/SPEC ativos, reviews pendentes). São importados no `CLAUDE.md` para carregar
no início de cada sessão e escritos ao **fim da cascade**. Barato por construção: budget de
linhas no journal com auto-arquivamento. Materializa C5.

## Critérios de aceite

```gherkin
# AC-1
Cenário: estrutura de memória existe no template
  Dado o template context-repo
  Quando inspeciono `_meta-session/`
  Então existe `journal.md` (append-only) e `state.md` (sobrescrito)
  E ambos têm cabeçalho explicando sua própria política (como os outros docs)

# AC-2
Cenário: entrada de journal no fecho da cascade
  Dado o fim de um passe da cascade que alterou docs
  Quando a cascade fecha
  Então acrescenta ao journal `## <yyyy-MM-dd HH:mm> — <1 linha> / pendências / IDs tocados`
  E a entrada nova vai no topo/fim conforme a política do cabeçalho (append-only, sem reescrever antigas)

# AC-3
Cenário: state reflete o que está em andamento
  Dado trabalho em andamento (AYD/SPEC ativos, reviews pendentes)
  Quando a cascade fecha
  Então `state.md` é SOBRESCRITO com o retrato atual (não acumula histórico)

# AC-4
Cenário: budget de linhas com auto-arquivamento
  Dado um `journal.md` que passa de 200 linhas
  Quando a cascade vai escrever
  Então as entradas antigas são movidas para `_meta-session/journal-archive/`
  E `journal.md` volta abaixo do budget

# AC-5
Cenário: memória carrega no início da sessão
  Dado o `CLAUDE.md` do context-repo
  Quando inspeciono seus imports/instruções
  Então `journal.md` e `state.md` são referenciados como leitura inicial de contexto
```

## Contratos consumidos/expostos

- **Implementa C5 — Session journal contract** (AYD-002): `_meta-session/journal.md`
  (append-only, budget 200 → `journal-archive/`) e `_meta-session/state.md` (sobrescrito), com
  o formato de entrada definido. Este PR define C5; não redefine.
- Sem dependência de outras SPECs (paralelizável com SPEC-001/003/004).
- Sinergia com SPEC-004: o registro de ALIGN (AC-4 da SPEC-004) usa este journal quando existir.

## Modelo de dados / componentes afetados

- `context-repo/_meta-session/journal.md` (novo): append-only, budget 200 linhas, cabeçalho com
  a política no próprio arquivo.
- `context-repo/_meta-session/state.md` (novo): sobrescrito a cada fecho.
- `context-repo/_meta-session/journal-archive/` (novo, criado sob demanda): destino do
  auto-arquivamento.
- `context-repo/.claude/skills/cascade/SKILL.md` (editado): passo de fecho escreve journal+state.
- `CLAUDE.md` (editado): `_meta-session/*` entram como leitura inicial de contexto.
- `.gitignore` — decidir no PR se a memória é versionada (rastreável entre sessões/máquinas) ou
  local; preferência por **versionada** (o valor é a continuidade compartilhada).

## Casos de borda & fora de escopo

- **Borda:** sessão que não alterou nada → não escreve entrada de journal vazia (evita ruído).
- **Borda:** journal cresce muito num único fecho → o arquivamento roda por budget de linhas,
  não por tempo; garante que o corte acontece antes de estourar o contexto na próxima leitura.
- **Borda:** conflito de merge no journal entre branches → append-only minimiza; o cabeçalho
  deve orientar resolução (manter ambas as entradas por timestamp).
- **Fora:** memória semântica / embeddings / recall por similaridade — aqui é um log textual
  simples lido no boot. Memória rica é evolução futura.
- **Fora:** sincronizar a memória para os service-repos — o journal é do context-repo (onde a
  cascade orquestra); serviços não herdam este estado.
