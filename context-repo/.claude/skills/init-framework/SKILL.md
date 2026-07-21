---
name: init-framework
description: >-
  Entrevista guiada de onboarding do framework (SPEC-007 de AYD-002): perguntas mínimas
  (nome do produto, repos de serviço e seus caminhos, provedores) preenchem
  requirements.md/architecture.md, configuram o sync (sync-context.sh) e a detecção
  multi-repo da skill `cascade`, gravam `.framework-version` (C3) e removem os
  exemplos/meta-docs do scaffold. É o **primeiro passo** ao adotar o framework num projeto
  novo — use quando o repo ainda tem os placeholders `AYD-NNN`/`SPEC-NNN`, os arquivos
  `*-example.*` e/ou `_framework/`. Não use para o dia a dia de escrever REQ/AYD/SPEC (isso
  é a skill `cascade`) nem num projeto que já rodou esta entrevista (ver §1, Idempotência).
---

# Init Framework — entrevista guiada de onboarding (SPEC-007 de AYD-002)

Você conduz a **entrevista de adoção**: substitui "clone, leia os READMEs, edite à mão,
apague os exemplos" por perguntas mínimas cujas respostas preenchem o scaffold. Esta skill
roda **uma vez** por produto, no repo de contexto recém-clonado (e, se os repos de serviço já
existirem no workspace, também neles). Depois disso, o dia a dia de documentação é a skill
`cascade`.

## 0. Pré-condição — isto é um scaffold do framework?

Antes de qualquer pergunta, confirme os marcadores do framework no diretório atual:
- `CLAUDE.md` existe e contém o cabeçalho `Product Context (SINGLE SOURCE)` (ou equivalente
  claramente do scaffold); e
- existe `_framework/` **ou** `requirements.md` ainda traz o placeholder `<que dor o produto
  resolve...>`.

Se nenhum marcador aparecer, **aborte** com uma mensagem clara: "este diretório não parece um
scaffold do framework (docs-framework-scaffold) — rode a partir do repo de contexto clonado".
Não adivinhe nem tente "consertar" um repo não relacionado.

## 1. Idempotência — instalação já existe? (AC-6)

Verifique o sinal combinado de instalação já concluída:
- `_framework/` **não existe** (já foi removido por uma init anterior); **e**
- `requirements.md` **não** traz mais o placeholder `<que dor o produto resolve...>` (foi
  preenchido com conteúdo real).

Se **ambos** forem verdade, este produto já passou pela entrevista. **Não** sobrescreva nada
por padrão — informe o estado atual (nome do produto encontrado em `requirements.md`, repos
de serviço configurados em `.claude/skills/cascade/SKILL.md` §6) e pergunte explicitamente se
o humano quer entrar em **modo de reconfiguração**. Só em modo de reconfiguração, e só para o
que for pedido (ex.: "adicionar um novo repo de serviço", "corrigir o caminho do repo X",
"trocar um provedor"), edite os arquivos afetados — nunca o conteúdo de REQ/AYD/PDR/ADR reais
já escrito pelo usuário.

Se só um dos dois sinais aparecer (estado ambíguo — ex.: `_framework/` foi apagado manualmente
mas `requirements.md` ainda é o placeholder), **pare e pergunte** ao humano antes de decidir se
trata como instalação nova ou existente.

## 2. Entrevista (perguntas mínimas)

Faça estas perguntas, nesta ordem, aceitando respostas parciais (ver §5, Bordas):

1. **Produto:** nome e uma frase (que dor resolve, para quem, resultado esperado) — vira a
   "Produto em uma frase" de `requirements.md`.
2. **Repos de serviço:** para cada um, nome (ex. `api`, `web`, `mobile`) e caminho relativo a
   partir de onde está o repo de contexto (ex. `../<produto>-api`). Aceite "nenhum ainda, só o
   repo de contexto por enquanto" — não trave a entrevista por isso (ver Borda, SPEC-007).
3. **Provedores:** para cada container (o repo de contexto e cada repo de serviço informado),
   que provedor/infra roda (ex.: Cloud Run, Vercel, Firebase Auth, Neon/Postgres).

## 3. Preenchimento (nesta ordem)

a. **`requirements.md`** — substitua o bloco "Produto em uma frase" pela resposta da pergunta 1.
   Não toque no resto do arquivo (RF/RNF/Glossário ficam vazios para o usuário preencher depois).

b. **`architecture.md`** — reescreva o diagrama `mermaid flowchart` e a tabela de Containers
   com os repos e provedores informados na entrevista (troque o exemplo mobile/web/API/Auth/DB
   existente). Se nenhum repo de serviço foi informado ainda, deixe só o container do próprio
   produto e uma nota de que os demais entram quando existirem — nunca deixe o exemplo antigo.

c. **`.claude/skills/cascade/SKILL.md`, §6 "Detecção multi-repo"** — troque a linha de exemplo
   genérico (`../<produto>-api`, `../<produto>-web`, `../<produto>-mobile`) pelos caminhos e
   nomes reais informados na entrevista (ou, se nenhum repo de serviço foi informado, deixe o
   padrão de nomenclatura declarado — ex. `../<nome-do-produto>-<repo>` — para quando existirem).

d. **`sync-context.sh` de cada repo de serviço presente no workspace** (no caminho informado em
   2): ajuste `CONTEXT_REPO` para a URL real do repo de contexto (`git remote get-url origin`
   deste repo, se já tiver remoto; senão pergunte) e `CONTEXT_REF` se o usuário quiser fixar
   uma tag. Repo de serviço **ausente** do workspace → não há o que editar agora; isso fica
   para quando o repo existir (parte do "configurar o resto depois" da Borda do SPEC).

e. **`.framework-version`** de cada repo tocado (contexto e cada repo de serviço presente):
   atualize `installed:` para a data de hoje. Tente resolver a versão real via
   `git describe --tags` no repo local do scaffold; se resolver, atualize `version:`; se não
   houver tag (ex. clone raso de `main`), **mantenha** o `version:` que já vinha no arquivo em
   vez de inventar um valor. Nunca edite `files:` aqui — isso é papel do `update-framework.sh`
   (SPEC-003), não da entrevista.

f. **Remoção de exemplos e meta-docs** — ver lista exata em §4. Regra: remova só o que está
   **explicitamente** listado (placeholders `*-NNN-example.md`, `_framework/`,
   `design/AYD-002-framework-improvements.md`); nunca um doc que o usuário já editou com
   conteúdo real (ver Borda, SPEC-007) — se um dos arquivos da lista já foi claramente editado
   (não bate mais com o exemplo original), pare e pergunte antes de apagar.

g. **Validação final** — rode `scripts/validate.py --repo-root .` no repo de contexto e, para
   cada repo de serviço presente, `docs/scripts/validate.py --repo-root docs`. A remoção do
   passo f não pode deixar `BROKEN_REF`: se aparecer (ex. um doc mantido ainda referenciava um
   exemplo removido em `parents`/`children`/`related`), corrija essas referências antes de
   terminar. `AC_WITHOUT_TEST` em WARN é esperado e não bloqueia (SPECs recém-instaladas ainda
   não têm testes).

## 4. Remoção — lista exata (AC-5)

No repo de contexto:
- `design/AYD-001-example.md`
- `product_decisions/PDR-001-example.md`
- `architecture_decisions/ADR-001-example.md`
- `design/AYD-002-framework-improvements.md` (meta-AYD do próprio ciclo de robustez do
  framework — não é conteúdo do produto adotante)
- `_framework/` (todas as `SPEC-NNN-*.md` meta, incluindo esta)

Em cada repo de serviço presente no workspace:
- `docs/specs/SPEC-001-example.md`
- `docs/plans/PLAN-001-example.md`
- `docs/technical_decisions/TDR-001-example.md`

**Nunca remova** os templates (`*-000-template.md`, `SPEC-000-template.md`, etc.) — são
arquivos de framework reutilizáveis, listados em `files:` do `.framework-version`.

## 5. Casos de borda (ver SPEC-007 para o texto normativo)

- Repos de serviço ainda não existem → preencha só o que dá (produto, provedor do próprio
  contexto) e siga; não trave a entrevista.
- Doc de exemplo já editado com conteúdo real → não apague; pare e pergunte.
- Diretório sem os marcadores do framework (§0) → aborte com mensagem clara, não prossiga.
- Instalação já existente (§1) → não sobrescreva; ofereça reconfiguração explícita.

## 6. Fechamento

Depois da validação (passo g), siga o checklist de saída da skill `cascade` (§8/§9) no que se
aplicar: registre a entrevista concluída (produto, repos configurados, o que ficou pendente —
ex. "repos de serviço a configurar depois") em `_meta-session/journal.md`/`state.md`, se esse
diretório existir no repo de contexto.
