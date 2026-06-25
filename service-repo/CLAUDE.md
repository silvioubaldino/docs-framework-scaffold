# <SERVIÇO> — Guia do repo

> Copie este arquivo para a raiz de cada repo de serviço (api, web, mobile) e
> preencha as seções marcadas com **PREENCHA**.

Repo de serviço do produto (conjunto api · web · mobile), que compartilha o mesmo
contexto via o repo de contexto. Este guia orienta o trabalho **no projeto** (não só nas
docs): as seções abaixo dão ao Claude o contexto de engenharia; a última resume como o
repo se conecta ao framework de docs.

## Papel deste repo  <!-- PREENCHA -->
<!-- Ex. (api):    Dono dos contratos de API. Implemento o que o AYD define; mudança
                   de contrato é PR no repo de contexto, nunca local.
     Ex. (web/mobile): Consumo os contratos do AYD (fonte da verdade). Se o backend
                   divergir do AYD, sinalizo — não adapto silenciosamente. -->
- 

## Especificidades do projeto  <!-- PREENCHA -->
> Orientação de engenharia que **não** vem do framework de docs: o que o Claude precisa
> para rodar, testar e escrever código neste repo.
- **Stack / runtime:** _<linguagem, framework, versão>_
- **Como rodar:** _<setup e comandos de dev>_
- **Build / teste / lint:** _<comandos>_
- **Arquitetura:** _<camadas, organização do `src/`, padrões — ou aponte para um TDR/ADR>_
- **Integrações externas:** _<auth, pagamentos, observabilidade… o que este repo consome>_

## Convenções de engenharia (locais)
@docs/conventions/testing.md
@docs/conventions/code-style.md
@docs/conventions/git.md
<!-- Adicione convenções específicas do repo conforme a necessidade (ex.: openapi.md,
     observability.md) e referencie-as aqui. -->

## Framework de docs (resumo)
Como este repo se liga ao contexto compartilhado. As **regras completas** estão nos
arquivos linkados — aqui fica só o essencial.

- **Contexto READ-ONLY:** rode `docs/scripts/sync-context.sh` para popular `docs/shared/`
  (espelho **gitignored** do repo de contexto — **não edite aqui**). Mapa e regras:
  @docs/shared/manifest.md · @docs/shared/_meta/glossary.md (use SEMPRE estes termos) ·
  @docs/shared/_meta/conventions.md (IDs, frontmatter, refs `ID@repo`).
- **O que mora neste repo:** `docs/specs/` (SPEC), `docs/plans/` (PLAN),
  `docs/technical_decisions/` (TDR local), `docs/conventions/` (CONV), `docs/changelog.md`.
- **Contrato só muda no contexto** (AYD/ADR). Se a `api`/backend divergir do AYD,
  **sinalize** — não adapte localmente (ver `conventions.md` §5).
- **Fluxo de uma feature:** leio o AYD em `docs/shared/design/` → crio/atualizo a SPEC
  (`parents: [AYD-NNN@context]`) → escrevo o PLAN e implemento → mudou contrato? volto ao
  AYD no repo de contexto antes de prosseguir.
