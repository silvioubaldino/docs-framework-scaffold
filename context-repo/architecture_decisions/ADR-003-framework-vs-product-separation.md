---
id: ADR-003
type: adr
title: Separação arquivos de framework × conteúdo de produto via .framework-version
status: approved
updated: 2026-07-21
parents: []
related: [AYD-002, SPEC-003]
superseded_by: null
---

# ADR-003: Separação arquivos de framework × conteúdo de produto

## Contexto

Um repo instalado a partir do scaffold mistura, no mesmo working tree, duas naturezas
de arquivo:

- **arquivos de framework** — a "engine" do método (regras do `CLAUDE.md`, hooks e
  `settings.json` em `.claude/`, scripts de `scripts/`, templates `*-000-*.md`). São
  autorados pelo scaffold e evoluem com ele;
- **conteúdo de produto** — o que o time escreve (REQ/AYD/PDR/ADR reais, `requirements.md`,
  `roadmap.md`, `architecture.md`, SPEC/PLAN/TDR nos serviços). É a razão de o repo existir
  e **nunca** deve ser tocado por uma atualização do framework.

Sem uma fronteira explícita, atualizar o framework de um projeto em andamento vira cópia
manual e diff a olho — arriscado, porque um deslize sobrescreve documentação de produto.
O AYD-002 escolheu a **opção A** (arquivo de versão + diff) em vez de um instalador CLI
(fora de escopo neste ciclo) e a materializa como o contrato **C3**.

## Decisão

Cada template instalável carrega um **manifesto `.framework-version`** que declara
`framework/source/template/root/version/installed` e uma lista `files:` de **globs de
arquivos de framework** (formas suportadas: caminho literal ou `dir/**`, sempre relativos à
**raiz real do repo**, não ao arquivo do manifesto). Esse manifesto é a **fonte da verdade do
que é atualizável**: o `update-framework.sh` busca a tag-alvo do scaffold e computa o diff
**exclusivamente** nos paths cobertos por `files:`.

O manifesto normalmente mora na raiz do repo (`root: .`). O `service-repo`, porém, concentra
tudo sob `docs/` (só `CLAUDE.md`/`.gitignore` ficam de fato na raiz) — nele o manifesto mora
em `docs/.framework-version` com `root: ..`, apontando de volta para a raiz real. O script
localiza o manifesto subindo a partir de si mesmo (uso normal) ou descendo até 1 nível a
partir de `--repo-root` (uso explícito); `root:` resolve a raiz a partir do diretório do
manifesto nos dois casos, então `files:` nunca precisa de paths relativos ao manifesto.

Consequências de projeto que decorrem da separação:

- **Produto nunca entra em `files:`.** Docs vivos que guardam dados de produto
  (`requirements.md`, `roadmap.md`, `architecture.md`) e docs reais (AYD/PDR/ADR/SPEC/…)
  ficam de fora; só templates `*-000-*.md` (id com `NNN`) e a engine entram. Um guardrail
  (AC-5 / `--check`) reusa o parser de frontmatter da SPEC-001 e **recusa** qualquer glob que
  case um doc de produto real (tipo de produto + id sem `NNN`).
- **A tag-alvo é a referência.** O `files:` que vale é o da versão de destino (não só o local),
  de modo que um arquivo de framework novo entre versões é trazido automaticamente.
- **Nunca sobrescrever silenciosamente.** Um arquivo de framework editado localmente (diverge
  da versão-base) e também mudado no upstream vira **conflito**: a versão nova é gravada como
  `<arquivo>.framework-new`, o working tree fica intocado e a versão **não** é promovida até o
  humano resolver. Arquivos mistos (ex.: `CLAUDE.md` do serviço, com seções de framework e um
  papel preenchido pelo time) são protegidos por esse mesmo mecanismo.

## Alternativas consideradas

| Opção | Prós | Contras | Por que (não) escolhida |
|-------|------|---------|-------------------------|
| Manifesto `.framework-version` + diff por `files:` | separa framework de produto de forma explícita e versionável; roda com git puro | específico deste layout (mapeia `template/` no scaffold) | **Escolhida** (opção A do AYD-002) |
| Instalador CLI (npx) que reaplica o template | um comando; distribuível | peso de manter um pacote; escopo maior que o ciclo atual | adiada (evolução futura se houver multi-time) |
| Cópia manual + diff a olho | zero ferramenta | não-determinístico; um deslize sobrescreve produto | descartada (é o problema que a SPEC-003 ataca) |
| `files:` por diretório amplo (ex.: `design/**`) | manifesto curto | casaria AYD/PDR reais → risco de tocar produto | descartada (viola a fronteira; barrada pelo `--check`) |

## Consequências / trade-offs

- **Positivas:** atualizar o framework de um projeto vivo vira um comando auditável, com
  `--dry-run` para preview; produto fica garantidamente fora do diff; a fronteira
  "framework × produto" passa a ser um artefato versionado (o manifesto), não convenção tácita.
- **Negativas:** o manifesto precisa ser mantido quando arquivos de framework nascem/morrem;
  a mecânica assume o layout do scaffold (subdir `template/` mapeado por `template:`, e
  `root:` limitado a `.`/`..`) e git no PATH; a checagem de produto (AC-5) depende de
  `python3`/`frontmatter.py` e é _fail-open_ (pula com aviso se ausentes), coerente com ADR-002.
- **Impacto (IDs/repos afetados):** materializa o contrato **C3** de `AYD-002`; entregue por
  `SPEC-003`. Adiciona `.framework-version` e `update-framework.sh` aos dois templates
  (`context-repo/`, `service-repo/`). Não altera a topologia — `architecture.md` não muda.
