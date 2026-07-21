# Session State

> **Política:** retrato do que está **em andamento agora** — não acumula histórico (isso é
> papel do `journal.md`). **Sobrescrito por completo** ao fim de cada cascade que altera este
> estado; nunca faça append aqui. Se nada está em andamento, as seções ficam vazias (não
> apague os cabeçalhos).

## AYD/SPEC ativos
- AYD-002 (`draft`) — meta-AYD de robustez do framework; será removido ao fim do ciclo.
- SPEC-006 (`review`) — memória de sessão (journal + state).
- SPEC-007 (`review`) — skill de onboarding `/init-framework`.
- SPEC-009 (`review`) — agentes `implementer`/`qa-reviewer` + seção de stack canônica no
  `CLAUDE.md` do service-repo, implementada nesta sessão (branch
  `feature/spec-009-execution-agents`, ainda não mergeada).
- SPEC-001, SPEC-008 (`draft`) — ainda não implementadas.

## Reviews pendentes
- SPEC-002, SPEC-003, SPEC-004, SPEC-005, SPEC-006, SPEC-007, SPEC-009 aguardando revisão
  humana para `approved`.

## Próximos passos
- Implementar SPEC-001 (validador) e SPEC-008 (evals) — são as SPECs restantes de AYD-002.
- Abrir/mergear o PR de SPEC-009 (branch `feature/spec-009-execution-agents`).
