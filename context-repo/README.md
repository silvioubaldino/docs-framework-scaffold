# Repo de Contexto

Camada compartilhada da documentação do produto (requisitos, design cross-repo, roadmap
e decisões). É a **fonte única da verdade** consumida pelos repos de serviço.

- Como escrever/evoluir docs, IDs e frontmatter: ver `CLAUDE.md`.
- Regras de cada tipo de documento (glossário, changelog, ciclo de vida) vivem no próprio
  arquivo — `requirements.md`, `changelog.md`, `architecture.md` e cada template.

Os repos de serviço (api, web, mobile) espelham este repo em `docs/shared/` (read-only)
via o `sync-context.sh` de cada um. Contratos mudam **apenas aqui**, nos AYD/ADR.

`scripts/validate.py` checa a integridade do grafo (frontmatter, simetria parents/children,
refs quebradas) — requer Python 3, sem dependências além da biblioteca padrão.
