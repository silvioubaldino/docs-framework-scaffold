# Comparativo: docs-framework-scaffold × Berserqir

> Análise comparativa entre **este scaffold** (docs-framework-scaffold) e o
> [Berserqir](https://github.com/Berserq-cloud/berserquir), lida contra as práticas
> atuais da Anthropic para agentes/harness.
>
> **Método:** a leitura do Berserqir vem do `README` e da árvore de arquivos do repo
> (não de uma leitura completa do código-fonte). A intenção declarada é tratada como fiel;
> detalhes internos podem variar. Data: 2026-07-21.

## TL;DR

- **Este scaffold** é uma **arquitetura de conhecimento**: docs-como-grafo, *spec-driven*,
  para um **produto multi-repo** (`context-repo` como fonte única → `service-repos` que
  espelham e implementam), com uma camada de orquestração fina e barata (`cascade`) por cima.
- **Berserqir** é um **sistema operacional de agentes**: um "esquadrão" instalável (`npx`)
  de 18 agentes + 36 skills, multi-harness (Copilot/Claude/Cursor), com SDD sendo apenas
  **um dos três pilares** (junto de ICL e KAG-lite).

Um é um **grafo de documentação**; o outro é uma **força de trabalho de agentes**. Sobrepõem-se
bastante na *engine*, mas otimizam para coisas diferentes.

## Onde convergem (o "cânone Anthropic" que ambos seguem)

Os dois, de forma independente, aterrissaram nos mesmos padrões — justamente os que a
Anthropic recomenda hoje:

| Padrão | Neste scaffold | No Berserqir |
|---|---|---|
| Spec-Driven Development | REQ→AYD→SPEC→PLAN + ADR/PDR | PRD/SPECS/TESTS + ADR registry |
| Grafo tipado em vez de RAG vetorial | `parents/children/related` + validador | `graph.json` + âncoras canônicas (grep O(1)) |
| Hooks determinísticos (zero-LLM) | 3 hooks (git-safety, frozen-doc, shared-edit) | 12 hooks (git/cmd safety, secret-scan, config) |
| Evals comportamentais com "anti-check" | SPEC-008 (nível, ALIGN, fan-out; ainda `draft`) | 15 evals e01–e15, cada um com anti-check |
| Memória de sessão com TTL + auto-arquivo | 2 camadas (journal append-only + state) | 3 camadas (constitution/sprint/session) |
| Orquestrador + subagentes em modelo barato | opus orquestra, sonnet/haiku executam | orchestrator + squads hierárquicos |
| Subagente devolve **resumo**, não transcript | contrato de retorno §5 do `cascade` | protocolo `sub-agent-report` + `context-budget` |
| Gate de aprovação humana | **ALIGN** (contrato + fan-out) | bounded-autonomy (humano aprova arquitetura) |

Essa convergência é, por si só, o sinal mais forte de que ambos rastreiam a orientação atual
da Anthropic. A diferença está no **quanto** de máquina cada um coloca em volta disso.

## As diferenças que importam

### 1. Escopo e centro de gravidade
- **Scaffold:** o coração é o **modelo multi-repo** — `context-repo` (camada compartilhada:
  REQ/GLO/AYD/ROAD/ARCH/PDR/ADR, fonte única) e N `service-repos` que espelham `docs/shared/`
  read-only e guardam só o seu (SPEC/PLAN/TDR). Regra-mãe: **"contrato só muda no contexto"**,
  `1 AYD → N SPECs`. Modela topologias reais de produto (api/web/mobile) e a disciplina de
  contrato entre elas.
- **Berserqir:** parece **mono-repo / por área** (`profiles/front,back,infra,ops`). A separação
  dele é "o que é invariante (`core/`) × o que varia por área (`profiles/`) × o que varia por
  harness (`adapters/`)". Não centra no problema de **contrato cross-repo** — centra em
  disciplina por especialidade.

### 2. Distribuição e onboarding
- **Scaffold:** você **copia pastas** e roda `/init-framework`. Atualização via
  `update-framework.sh`, que mexe **só nos arquivos de engine** sem tocar no conteúdo de produto.
  Transparente, Python stdlib, zero install.
- **Berserqir:** `npx berserqir install/update/doctor/verify`, tudo *vendored* no install,
  verificável em supply-chain. Turnkey de verdade, mas é mais maquinário e cria dependência do
  ciclo de vida da CLI.

### 3. Portabilidade de harness
- **Scaffold:** a orquestração viva é **Claude Code-first** (`.claude/` agents/hooks/skills).
  Mas os *docs* são portáteis para fora (Claude Projects, e `bundle.sh` → NotebookLM/Gemini).
- **Berserqir:** **multi-harness nativo** via `adapters/` (um compilador por harness). Ganho
  grande para times mistos.

### 4. Amplitude vs minimalismo
- **Scaffold:** **2 skills, ~4 agentes, 3 hooks**. Deliberadamente enxuto — você escreve suas
  próprias `conventions/`.
- **Berserqir:** **36 discipline skills** (API design, observability, caching, k8s, FinOps…),
  **18 agentes** com senioridade (senior/pleno/junior/qa/security) e regras de escalonamento
  para auth/payments/migrations. Muito mais "fora da caixa".

### 5. Auto-melhoria
- **Berserqir** tem **ICL**: gera skills a partir de padrões repetidos nos journals (`/learn`,
  `/evolve`) e `instincts.json`/`human-profile.md`.
- **Scaffold** **não** se auto-modifica — a memória é descritiva (journal/state), não gera
  engine nova.

## Lendo cada um contra as práticas modernas da Anthropic

### "Building Effective Agents" — comece simples; só adicione complexidade quando ela se paga; fan-out só para subtarefas independentes.
- **Scaffold:** alinhamento quase literal. A triagem do `cascade` tem *default = agente único*
  e só faz fan-out no nível 3 (cross-repo, direções independentes), com roteamento a modelo
  barato. É textbook.
- **Berserqir:** 18 agentes + 36 skills é bastante cerimônia *a priori* — exatamente o que a
  Anthropic pede cautela ("case a complexidade ao valor"). Ele **mitiga** com `profiles`
  ("instale só o que precisa") e com **anti-checks contra over-ceremony** nos evals. Mas a
  própria necessidade desses anti-checks é o sintoma de que o risco existe.

### Agent Skills best practices — conciso, progressive disclosure, `description` é o mecanismo de descoberta, evals primeiro.
- **Scaffold:** poucas skills = pouca pressão de descoberta; consistente com "não ofereça opções
  demais". Risco oposto: **pode servir de menos** (sem skills de observability/security/etc.).
- **Berserqir:** 36 skills é viável (a Anthropic suporta 100+ com metadata pré-carregada), mas
  aí **qualidade/sobreposição de `description` viram o modo de falha** e o custo de metadata
  sobe. O "gerar skill a partir de padrão repetido" é *exatamente* o fluxo iterativo que a
  Anthropic recomenda — bom alinhamento.

### Subagents & context engineering — isolar contexto, devolver resumo, single-writer, memória externa.
- Os dois acertam. O "subagente devolve resumo compacto + só o orquestrador escreve os
  arquivos-cola" do `cascade` é precisamente o aprendizado do sistema multi-agente de pesquisa
  da Anthropic. Berserqir espelha com `context-budget` + `sub-agent-report`.

## Prós e contras

### Scaffold — prós
- Mínimo, baixo overhead de token/cognição; fácil de auditar (markdown + Python stdlib).
- Modelo **multi-repo com disciplina de contrato** é a contribuição distinta e bem-resolvida.
- Portável para fora do Claude Code (bundle p/ NotebookLM/Gemini/Projects); baixo lock-in.
- Versionamento de framework que separa engine de conteúdo de produto.

### Scaffold — contras
- Orquestração viva é Claude Code-only (sem adapters p/ Copilot/Cursor).
- Install manual; superfície pequena de skills/agentes/hooks; **evals ainda em `draft`**
  (SPEC-008/SPEC-001 não implementadas).
- Detecção multi-repo é heurística por caminho; ainda carrega meta-scaffolding (AYD-002,
  `_framework/`, exemplos) a limpar na adoção.

### Berserqir — prós
- Turnkey e reproduzível (`install/doctor/verify`), supply-chain verificável.
- **Multi-harness** real; disciplina rica fora da caixa; escalonamento p/ operações de alto risco.
- Auto-melhora (ICL); memória 3-camadas com self-healing; auto-verificação forte
  (67-check smoke + LLM-judge).

### Berserqir — contras
- Peso e cerimônia altos; mais difícil de auditar/confiar por inteiro; a própria existência de
  anti-over-ceremony denuncia o risco.
- Mais maquinário (CLI + vendoring) e lock-in ao ciclo da ferramenta.
- Aparentemente **não** modela o problema cross-repo de contrato que é o centro do scaffold
  (foco por área, não por repo de serviço).

## Recomendação prática

Eles são mais **complementares que concorrentes**. Para evoluir *este* scaffold sem trair seu
minimalismo, puxaria de forma seletiva do Berserqir:

1. **Fechar os evals (SPEC-008) com "anti-checks"** — hoje é o maior gap: existe a filosofia
   certa (`cascade` cost-aware) mas sem a rede que impede regressão de julgamento. Maior ROI.
2. **Adapters leves de harness** — um compilador simples `.claude/` → Copilot/Cursor amplia
   alcance sem inflar a engine.
3. **NÃO** adotar 18 agentes/36 skills. Isso contraria o eixo que faz este scaffold estar mais
   alinhado à Anthropic ("simplicidade primeiro"). O valor do scaffold é ser enxuto — a
   disciplina por especialidade deve nascer como `conventions/` sob demanda, não como catálogo
   *a priori*.

## Fontes (Anthropic)

- [Building Effective AI Agents](https://www.anthropic.com/engineering/building-effective-agents)
- [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Agent Skills — authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Claude Code — subagents](https://code.claude.com/docs/en/sub-agents)
