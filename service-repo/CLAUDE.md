# <SERVIÇO> — Contexto do repo

> Copie este arquivo para a raiz de cada repo de serviço (api, web, mobile) e
> preencha o nome e o PAPEL abaixo.

Repo de serviço do produto. Faz parte de um conjunto (api, web, mobile) que
compartilha o mesmo contexto via o repo de contexto.

## Papel deste repo  <!-- PREENCHA -->
<!-- Ex. (api):    Dono dos contratos de API. Implemento o que o AYD define; mudança
                   de contrato é PR no repo de contexto, nunca local.
     Ex. (web/mobile): Consumo os contratos do AYD (fonte da verdade). Se o backend
                   divergir do AYD, sinalizo — não adapto silenciosamente. -->
- 

## Contexto compartilhado (READ-ONLY)
Antes de trabalhar, sincronize: `docs/scripts/sync-context.sh`
(popula `docs/shared/` a partir do repo de contexto).
- @docs/shared/manifest.md — mapa do produto
- @docs/shared/_meta/glossary.md — linguagem ubíqua (use SEMPRE estes termos)
- @docs/shared/_meta/conventions.md — IDs, frontmatter, referências `ID@repo`

> `docs/shared/` é um espelho **gitignored** do repo de contexto. **NÃO edite aqui.**
> Mudou produto / REQ / AYD / contrato? Abra PR no repo de contexto.

## O que mora neste repo
- `docs/specs/` — **SPEC-NNN**: a parte deste repo de cada AYD. Frontmatter: `parents: [AYD-NNN@context]`.
- `docs/plans/` — **PLAN-NNN**: passos de implementação de cada spec.
- `docs/technical_decisions/` — **TDR-NNN**: decisões técnicas locais (sem efeito cross-repo).
- `docs/conventions/` — padrões de engenharia deste repo (teste, estilo, git).
- `docs/changelog.md` — mudanças deste serviço.

## Fluxo de uma feature
1. Leio o AYD em `docs/shared/design/` (papel deste repo + contratos).
2. Crio/atualizo a SPEC local conforme o AYD (`parents: [AYD-NNN@context]`).
3. Escrevo o PLAN e implemento. Testes seguem as convenções abaixo.
4. Surgiu mudança de contrato → volto ao AYD no repo de contexto antes de prosseguir.

## Convenções de engenharia (locais)
@docs/conventions/testing.md
@docs/conventions/code-style.md
@docs/conventions/git.md
