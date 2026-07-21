# Session Journal

> **Política:** log **append-only** de sessões da `cascade` que alteraram algum doc (sessões
> sem alteração não escrevem entrada — evita ruído). Novas entradas vão **no fim do arquivo**;
> nunca reescreva, reordene ou apague entradas antigas.
>
> **Formato da entrada:**
> ```
> ## <yyyy-MM-dd HH:mm> — <1 linha do que foi feito>
> Pendências: <o que ficou em aberto, ou "nenhuma">
> IDs tocados: <lista de IDs, ex. AYD-002, SPEC-006>
> ```
>
> **Budget:** 200 linhas. Ao ultrapassar, as entradas mais antigas (do topo) são movidas para
> `journal-archive/journal-<yyyy-MM-dd>.md` (nome pela data da entrada mais antiga movida) até
> este arquivo voltar abaixo do budget. `journal-archive/` é criado sob demanda, no primeiro
> arquivamento.
>
> **Conflito de merge:** por ser append-only, resolva mantendo **ambas** as entradas, ordenadas
> cronologicamente pelo timestamp — nunca descarte uma em favor da outra.

---

## 2026-07-21 10:58 — Implementa SPEC-006 (journal + state de sessão)
Pendências: nenhuma
IDs tocados: AYD-002, SPEC-006

## 2026-07-21 12:00 — Implementa SPEC-007 (skill de onboarding /init-framework)
Pendências: nenhuma
IDs tocados: AYD-002, SPEC-007
