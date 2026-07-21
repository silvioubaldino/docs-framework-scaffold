# Evals comportamentais (SPEC-008 de AYD-002)

> Impede regressão silenciosa de **julgamento** da cascade/agentes quando `.claude/skills/**`
> ou `.claude/agents/**` mudam. Complementa o validador (SPEC-001, estrutura determinística)
> cobrindo o que exige julgamento: nível de triagem certo, gate ALIGN (SPEC-004) disparado
> quando devia, fan-out só cross-repo.

## O que um caso afirma (e o que não afirma)

Um caso é um **replay declarativo**: pedido + contexto mínimo → decisões estruturais
esperadas (nível de triagem, se dispara ALIGN-Contrato, se dispara ALIGN-Fanout, se faz
fan-out, quais docs seriam tocados). **Não** afirma texto literal — comportamento de LLM
varia na redação; afirmar prosa geraria falso-negativo por variação de estilo, não por
regressão real. Também não exige pagar um fan-out de verdade: o caso checa a **decisão**
de fazer fan-out, não a execução completa dos subagentes.

Fora de escopo (ver SPEC-008): qualidade de prosa gerada, e qual framework de eval de
terceiros usar — aqui o eval é binário de processo (fez a coisa certa), não juiz de conteúdo.

## Formato do caso (`cases/EVAL-NNN-slug.md`)

Cada arquivo tem **dois blocos `---`-fenced** (mesmo parser de frontmatter do
`scripts/validate.py` — reusado, não reimplementado):

1. **Frontmatter do topo** — id do caso e o comportamento **esperado**:
   ```yaml
   ---
   id: EVAL-NNN
   title: <descrição curta>
   expected_level: 0|1|2|3          # nível de triagem (cascade §1)
   expected_align_contrato: true|false
   expected_align_fanout: true|false
   expected_fanout: true|false
   expected_docs_touched: [a.md, AYD-novo, SPEC-novo@repo]
   ---
   ```
2. **Bloco sob `## Observado`** — o que um replay realmente produziu, no mesmo formato
   (`observed_*`). Fica **vazio até o replay acontecer**; o runner reporta `PENDING` nesse
   caso (não falha o build sem `--strict`).

Entre os dois blocos, prosa livre com `## Pedido` (o texto que seria dado à cascade),
`## Contexto mínimo` (estado do repo assumido — ex.: quais repos-irmãos existem) e
`## Comportamento esperado` (o racional — por que aquele nível/ALIGN/fan-out, citando a
seção da skill `cascade` ou da SPEC-004 que decide).

## Como replayar um caso

Pedir à cascade para **só triar** o `## Pedido` do caso — sem executar, sem escrever
arquivo, sem despachar subagente de verdade — e reportar de volta os 5 campos
(`level`, `align_contrato`, `align_fanout`, `fanout`, `docs_touched`). Colar a resposta no
bloco `## Observado` do caso, no formato `observed_*` acima. Repita para os casos afetados
sempre que `.claude/skills/**` ou `.claude/agents/**` mudar (o hook
`.claude/hooks/remind-run-evals.sh` lembra disso automaticamente — ver AC-6).

## Rodar o runner

```
python3 evals/run_evals.py [--cases-dir PATH] [--strict]
```

- Uma linha por caso em stdout: `SEVERITY | CASE_ID | message`.
- `SEVERITY`: `PASS` (bate com o esperado) | `FAIL` (diverge em ≥1 campo) | `PENDING`
  (bloco `## Observado` ainda vazio).
- Exit 0 se não há `FAIL` (e, sem `--strict`, `PENDING` não conta). Exit 1 se há `FAIL`, ou
  (com `--strict`) se há `PENDING` — use `--strict` em CI, onde todo caso precisa estar
  replayado e passando antes de aprovar a mudança (AC-6); localmente, o modo default permite
  casos ainda não replayados sem travar o dia a dia.

## Fiação com o review (AC-6)

`.claude/hooks/remind-run-evals.sh` (PostToolUse em `Edit|Write`) dispara um lembrete
(stderr, não bloqueia) quando o alvo é `.claude/skills/**` ou `.claude/agents/**`: replayar
os casos afetados e rodar `evals/run_evals.py` antes de aprovar a mudança. Rodar de verdade
depende de julgamento (LLM) — por isso o hook lembra em vez de bloquear a cada edição; quem
efetivamente **verifica e falha o build** é `run_evals.py --strict`, que um passo de CI pode
chamar do mesmo jeito que chamaria `scripts/validate.py`.
