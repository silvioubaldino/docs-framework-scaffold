---
id: ADR-002
type: adr
title: Regras críticas do grafo viram hooks determinísticos, não prosa
status: approved
updated: 2026-07-20
parents: []
related: [AYD-002, SPEC-002]
superseded_by: null
---

# ADR-002: Regras críticas do grafo viram hooks determinísticos

## Contexto

O framework depende de convenções descritas em prosa (`CLAUDE.md`, headers dos
templates). Três violações são caras demais para ficarem só na prosa, na esperança
de que a IA "lembre" da regra a cada ação:

- editar o **espelho read-only** (`docs/shared/**`), cujo conteúdo só deveria mudar
  no context-repo e ser re-sincronizado;
- alterar um **doc congelado** (`status: approved`/`superseded`), quebrando a garantia
  de imutabilidade do lifecycle;
- rodar **git destrutivo** (`push`, `reset --hard`, `--force`/`-f`) sem aprovação humana.

O princípio diretor do AYD-002 é *regra que importa vira código; prompt é só para o
que exige julgamento*. O Claude Code oferece **hooks PreToolUse** (contrato C2 do
AYD-002): recebem o evento em JSON no stdin e decidem por exit code — `0` libera,
`2` bloqueia com a razão no stderr, que volta para o modelo.

## Decisão

Essas três regras passam a ser **hooks PreToolUse determinísticos** (`.claude/hooks/*.sh`),
fiados via `.claude/settings.json` nos dois templates (context-repo e service-repo):

- `block-shared-edit.sh` — SHARED_READONLY em `Edit|Write` sob `docs/shared/**`.
- `block-frozen-doc.sh` — FROZEN_DOC em `Edit|Write` de doc `approved`/`superseded`.
- `git-safety.sh` — GIT_SAFETY em `Bash` com git destrutivo.

A detecção de doc congelado **reusa** o parser de frontmatter do validador (SPEC-001),
extraído para `scripts/frontmatter.py`; o hook não reimplementa parsing de YAML.

**Política de _fail-open_:** quando falta uma dependência do ambiente (`jq`, e para o
hook de frozen também `python3`/o parser), o hook **libera** a ação (exit 0) emitindo
um aviso no stderr, em vez de travar o trabalho. A escolha prioriza não bloquear o
desenvolvedor por um ambiente incompleto; o guardrail é uma rede de segurança contra
o erro comum, não um controle de segurança contra um agente adversário (que poderia,
afinal, desabilitar o hook). O bloqueio de git destrutivo **não** tem bypass silencioso:
o humano confirma e reexecuta o comando.

## Alternativas consideradas

| Opção | Prós | Contras | Por que (não) escolhida |
|-------|------|---------|-------------------------|
| Hooks PreToolUse determinísticos | independe da IA lembrar; bloqueio real antes da ação | específico do Claude Code; exige `jq` | **Escolhida** |
| Só prosa nas convenções | zero código; portável | não-determinístico — a regra falha exatamente quando mais importa | descartada (é o problema que o AYD-002 ataca) |
| _Fail-closed_ (bloquear sem `jq`) | guardrail sempre ativo | trava quem não tem `jq`; hook é rede de segurança, não controle adversarial | descartada |

## Consequências / trade-offs

- **Positivas:** as três violações mais caras passam a ser barradas de forma
  determinística; a razão do bloqueio volta ao modelo, que se corrige sozinho; a
  regra de frozen fica em sincronia com o validador por reuso do mesmo parser.
- **Negativas:** os hooks são específicos do Claude Code (portar para Cursor/Copilot
  fica fora de escopo); dependem de `jq` no ambiente; _fail-open_ significa que um
  ambiente sem `jq` fica sem a rede de segurança (mitigado pelo aviso no stderr).
- **Impacto (IDs/repos afetados):** materializa o contrato C2 de `AYD-002`; entregue
  por `SPEC-002`. Afeta os dois templates (`context-repo/`, `service-repo/`) com novos
  `.claude/hooks/*` e `.claude/settings.json`. Não altera a topologia — `architecture.md`
  não muda.
