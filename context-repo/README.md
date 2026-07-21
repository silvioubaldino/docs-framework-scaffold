# Repo de Contexto

Camada compartilhada da documentação do produto (requisitos, design cross-repo, roadmap
e decisões). É a **fonte única da verdade** consumida pelos repos de serviço.

## Comece por aqui

Acabou de clonar este scaffold para um produto novo? Rode `/init-framework` no Claude Code —
é uma entrevista guiada (nome do produto, repos de serviço, provedores) que preenche
`requirements.md`/`architecture.md`, configura o sync e a detecção multi-repo, grava
`.framework-version` e remove os exemplos/meta-docs. Ver
`.claude/skills/init-framework/SKILL.md`.

- Como escrever/evoluir docs, IDs e frontmatter: ver `CLAUDE.md`.
- Regras de cada tipo de documento (glossário, changelog, ciclo de vida) vivem no próprio
  arquivo — `requirements.md`, `changelog.md`, `architecture.md` e cada template.

Os repos de serviço (api, web, mobile) espelham este repo em `docs/shared/` (read-only)
via o `sync-context.sh` de cada um. Contratos mudam **apenas aqui**, nos AYD/ADR.

`scripts/validate.py` checa a integridade do grafo (frontmatter, simetria parents/children,
refs quebradas) — requer Python 3, sem dependências além da biblioteca padrão.
