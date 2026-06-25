# <SERVICE> — Repo guide

> Copy this file to the root of each service repo (api, web, mobile) and
> fill in the sections marked **FILL IN**.

Service repo of the product (api · web · mobile set), sharing the same context via the
context repo. This guide orients work **on the project** (not just the docs): the sections
below give Claude the engineering context; the last one summarizes how the repo connects to
the docs framework.

## This repo's role  <!-- FILL IN -->
<!-- E.g. (api):    Owner of the API contracts. I implement what the AYD defines; a contract
                    change is a PR in the context repo, never local.
     E.g. (web/mobile): I consume the AYD contracts (source of truth). If the backend
                    diverges from the AYD, I flag it — I do not adapt silently. -->
- 

## Project specifics  <!-- FILL IN -->
> Engineering guidance that does **not** come from the docs framework: what Claude needs to
> run, test, and write code in this repo.
- **Stack / runtime:** _<language, framework, version>_
- **How to run:** _<setup and dev commands>_
- **Build / test / lint:** _<commands>_
- **Architecture:** _<layers, `src/` layout, patterns — or point to a TDR/ADR>_
- **External integrations:** _<auth, payments, observability… what this repo consumes>_

## Engineering conventions (local)
@docs/conventions/testing.md
@docs/conventions/code-style.md
@docs/conventions/git.md
<!-- Add repo-specific conventions as needed (e.g. openapi.md, observability.md) and
     reference them here. -->

## Docs framework (summary)
How this repo connects to the shared context. The **full rules** live in the linked files —
this is just the essentials.

- **READ-ONLY context:** run `docs/scripts/sync-context.sh` to populate `docs/shared/`
  (a **gitignored** mirror of the context repo — **do not edit here**). Map and rules:
  @docs/shared/manifest.md · @docs/shared/_meta/glossary.md (ALWAYS use these terms) ·
  @docs/shared/_meta/conventions.md (IDs, frontmatter, `ID@repo` refs).
- **What lives in this repo:** `docs/specs/` (SPEC), `docs/plans/` (PLAN),
  `docs/technical_decisions/` (local TDR), `docs/conventions/` (CONV), `docs/changelog.md`.
- **Contracts only change in the context** (AYD/ADR). If the `api`/backend diverges from the
  AYD, **flag it** — do not adapt locally (see `conventions.md` §5).
- **Feature flow:** read the AYD in `docs/shared/design/` → create/update the SPEC
  (`parents: [AYD-NNN@context]`) → write the PLAN and implement → contract changed? go back
  to the AYD in the context repo before proceeding.
