# Product Context (SINGLE SOURCE)

Canonical repository for the product's **shared layer**.
Consumed **read-only** by the service repos (api, web, mobile),
which mirror it under `docs/shared/`.

## Start here
- @requirements.md — requirements **and glossary** (ALWAYS use these terms)
- @architecture.md — living architecture (C4)

## What lives here (shared)
- **REQ** (`requirements.md`) — requirements + glossary (GLO)
- **AYD** (`design/`) — Analysis & Design per feature (cross-repo: affected repos + contracts)
- **ROAD** (`roadmap.md`) — roadmap / planning
- **PDR** (`product_decisions/`) — product decisions
- **ADR** (`architecture_decisions/`) — cross-repo architecture decisions (contracts, protocols)
- **ARCH** (`architecture.md`) — living high-level architecture (C4 context + container) with provider names; updated whenever a service/integration is added or removed

## What does NOT live here
Each service's specs (SPEC), implementation plans (PLAN), local technical decisions (TDR),
code conventions, and changelog.

## Document IDs and frontmatter
ID = `PREFIX-NNN`, stable (never changes even if the file is renamed/moved). To reference a
doc from another repo, use `ID@repo` (e.g. `AYD-007@context`, `SPEC-012@api`); no suffix =
this repo. Every doc's frontmatter:

```yaml
---
id: AYD-007
type: design            # requirements | design | roadmap | pdr | adr | architecture | spec | plan | tdr
title: Upload de mídia
status: draft            # draft | review | approved | superseded | deprecated
updated: 2025-01-01
parents: [REQ-003]                 # what this doc refines (layer above)
children: [SPEC-012@api]           # what refines this doc (can be cross-repo)
related: [ADR-002, GLO]            # cross-cutting context
superseded_by: null                 # only PDR/ADR/TDR (append-only); omit otherwise
---
```

Repos affected by a feature (AYD) or decision (ADR) go in that doc's own body (e.g. the
AYD's "Repos afetados e papéis" table) — don't duplicate in frontmatter.

## Core rule (cross-repo)
**Contracts only change here** (in the AYD/ADR). Services implement; they do not redefine.
Every `SPEC` has an `AYD` in `parents`; **1 AYD → N SPECs**, one per affected repo.

## Lifecycle
- A contract is only created/altered in an AYD/ADR/PDR after explicit human approval (the
  ALIGN gate — see the `cascade` skill, §2); this holds even outside the skill.
- REQ / AYD / ROAD / ARCH = living (edit in-place, update `updated`; log in `changelog.md`).
- PDR / ADR = append-only (a new decision supersedes the old one via `superseded_by`).
- SPEC / PLAN / TDR live in the service repos; each template's header carries its own rules
  (SPEC freezes when `approved`; PLAN is ephemeral; TDR is append-only).
- A SPEC only becomes `approved` once every `AC-N` in its acceptance criteria has ≥1 test
  referencing it (`SPEC-NNN/AC-N`) — the validator's `AC_WITHOUT_TEST` rule enforces this
  (WARN while `draft`/`review`, ERROR once `approved`).
- When you change something, mark the affected `children` (including in other repos) as `status: review`.
- Topology changed (a service/integration was added or removed)? Update `architecture.md`
  in the same edit.

## Other tools
- Claude Projects: connect this repo via the GitHub integration and use **Sync**.
- NotebookLM / Gemini Gems: run `scripts/bundle.sh` → `CONTEXT.md` for upload.
