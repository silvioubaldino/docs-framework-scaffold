# 📐 Specs-Driven Docs Framework — Scaffolding

Estrutura de documentação **cronológica + hierárquica** para construir produtos com
**múltiplos repos** (api, web, mobile…), do conceito ao código, projetada para ser lida
por humanos e **consumida por IAs** (Claude Code, Claude Projects, NotebookLM, Gemini).

Este pacote é um **scaffolding**: você clona as pastas para iniciar o framework em repos
de verdade. Os arquivos `*-example.*` são demonstrações — apague ao começar.

## Ideia central
> Todo artefato tem **ID estável**, **status** e declara seus **relacionamentos**
> (`parents`/`children`/`related`). A doc vira um **grafo** que a IA percorre — do *porquê* ao *como*.
> Um produto, vários repos, **uma língua só** (glossário + convenções compartilhados).

## Como as peças se conectam
- Um **repo de contexto** guarda a camada compartilhada (requisitos + glossário, design
  cross-repo, roadmap, arquitetura, decisões de produto/arquitetura). É a **fonte única da verdade**.
- Cada **repo de serviço** (api, web, mobile) espelha o contexto em `docs/shared/` (read-only,
  gitignored) e guarda só o seu: specs, plans, decisões técnicas, convenções, changelog.
- **1 AYD (design cross-repo) → N SPECs** (uma por repo). Contratos mudam **só no repo de contexto**.
- Rastreabilidade por IDs globais: `AYD-001@context → SPEC-001@api, SPEC-001@web, SPEC-001@mobile`.

## Tipos de documento
| Prefixo | Documento | Onde | Vivo/Imutável |
|---------|-----------|------|---------------|
| REQ  | Requisitos (+ visão em uma frase) | contexto `requirements.md` | vivo |
| GLO  | Glossário | contexto `requirements.md` (seção Glossário) | vivo |
| AYD  | Análise & Design (cross-repo) | contexto `design/` | vivo |
| ROAD | Roadmap | contexto | vivo |
| ARCH | Visão de arquitetura (C4 vivo) | contexto `architecture.md` | vivo |
| PDR  | Decisão de produto | contexto `product_decisions/` | append-only |
| ADR  | Decisão de arquitetura (cross-repo) | contexto `architecture_decisions/` | append-only |
| SPEC | Especificação (parte de um repo) | serviço `docs/specs/` | congela ao aprovar |
| PLAN | Plano de implementação | serviço `docs/plans/` | efêmero |
| TDR  | Decisão técnica local | serviço `docs/technical_decisions/` | append-only |

## O que tem neste scaffolding
```
context-repo/     → vira o seu REPO DE CONTEXTO (1 por produto)
service-repo/     → copie para CADA repo de serviço (api, web, mobile)
```

## Pré-requisitos
- **Python 3** (só biblioteca padrão, sem `pip install`) para rodar `scripts/validate.py`
  (validador de integridade do grafo — ver `context-repo/_framework/SPEC-001-graph-validator.md`),
  presente em ambos os templates. Já vem instalado no macOS e na maioria das distros Linux e
  dos runners de CI padrão; em Windows sem WSL, confirme que o comando `python3` existe no PATH
  (senão ajuste o shebang ou invoque como `python scripts/validate.py`).

## Como configurar

### 1. Repo de contexto (uma vez por produto)
1. Copie o conteúdo de `context-repo/` para um repo novo (ex.: `meuproduto-context`).
2. Preencha `requirements.md` (visão em uma frase + requisitos + glossário), `roadmap.md`
   e `architecture.md`.
3. As regras do framework (IDs, frontmatter, ciclo de vida) vivem no `CLAUDE.md` do repo;
   as regras de cada tipo de doc, no header do próprio arquivo/template.
4. Apague os arquivos `*-example.*`.
5. (Recomendado) rode `scripts/validate.py` antes de abrir PR — valida o grafo de docs
   (frontmatter, simetria parents/children, refs quebradas); requer Python 3 (ver Pré-requisitos).

### 2. Cada repo de serviço (api, web, mobile)
1. Copie o conteúdo de `service-repo/` para a raiz do repo do serviço
   (`CLAUDE.md` e `.gitignore` na raiz; o resto dentro de `docs/`).
2. No `CLAUDE.md`, preencha o **nome** e o **papel** do serviço
   (api = dono dos contratos; web/mobile = consumidores).
3. Em `docs/scripts/sync-context.sh`, ajuste `CONTEXT_REPO` com a URL do repo de contexto.
4. Rode `docs/scripts/sync-context.sh` para popular `docs/shared/`.
5. (Recomendado) adicione um atalho no seu gerenciador de pacotes, ex.:
   `"sync:context": "docs/scripts/sync-context.sh"`.
6. Apague os arquivos `*-example.*` e preencha `docs/conventions/`.
7. (Recomendado) rode `docs/scripts/validate.py` antes de abrir PR — mesmo validador do
   repo de contexto, escopado a este repo; requer Python 3 (ver Pré-requisitos).

### 3. Uso em outras ferramentas
- **Claude Code:** já funciona — os `@imports` do `CLAUDE.md` carregam contexto + convenções.
- **Claude Projects:** conecte o repo de contexto via integração GitHub (botão **Sync**).
- **NotebookLM / Gemini Gems:** rode `scripts/bundle.sh` no repo de contexto → suba o `CONTEXT.md`.

## Regras de ouro
- Contrato muda **só** no AYD/ADR (repo de contexto). Serviços implementam, não redefinem.
- `docs/shared/` é espelho read-only — nunca edite ali.
- Decisão que cruza repos → ADR/PDR (contexto). Decisão local → TDR (serviço).
- Ao mudar um doc vivo: registre no changelog e marque os `children` afetados como `review`.
