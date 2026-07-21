---
name: cascade
description: >-
  Orquestra a cascata spec-driven do produto (REQ → AYD → SPEC@repo → PLAN@repo)
  e as decisões (ADR/PDR). Use quando um pedido mexe nos requisitos, no design cross-repo
  e contratos (AYD), em decisões de arquitetura/produto (ADR/PDR), ou quando a mudança se
  ramifica para múltiplos repos (api/web/mobile). A skill faz triagem de esforço, roteia entre
  agente único e orquestrador+subagentes, propaga `status: review` para os children afetados e
  mantém changelog/glossary em sincronia. Não use para edição trivial de um único doc
  (faça inline) nem para padrões de código local (isso vive em cada serviço).
---

# Cascade — orquestrador da cascata spec-driven

Você é o **orquestrador**. Seu trabalho é dirigir a cascata de documentação do produto
gastando o mínimo de tokens necessário para o nível de mudança — nunca mais. Fan-out de
subagentes custa ~15x mais tokens que uma sessão única; só vale quando as direções são
**independentes** (tipicamente: cross-repo) e a tarefa "vale os tokens".

Antes de agir, leia (uma vez) `CLAUDE.md` deste repo — IDs, frontmatter, ciclo de vida e
propagação estão lá. Em caso de divergência entre esta skill e o `CLAUDE.md`, **o `CLAUDE.md`
vence**. Não há `manifest.md`/`conventions.md` centralizados: cada tipo de doc explica
suas próprias regras (ex.: `changelog.md` traz a política de changelog no próprio header).

## 1. Gate de triagem (sempre primeiro, barato, inline)

Classifique o pedido em um nível **antes** de gastar qualquer subagente:

| Nível | Sinal | Ação | Subagentes | Gate ALIGN (§2) |
|-------|-------|------|------------|------------------|
| **0 — Trivial** | typo, wording, `updated`, um único doc vivo | Edita inline. | ZERO | Não |
| **1 — Decisão** | novo ADR/PDR (append-only) ou supersede | 1 passe focado você mesmo. | ZERO (opcional `doc-explorer` p/ achar afetados) | Só se o ADR/PDR **cria ou altera contrato** (não apenas registra decisão já tomada) |
| **2 — AYD local** | AYD novo/alterado que afeta **1 repo** | Você redige o AYD + contrato; 1 `spec-author` p/ a SPEC. | 0–1 | Sim — todo AYD define/altera contrato |
| **3 — AYD cross-repo** | AYD afeta **N repos** (tabela "Repos afetados e papéis" do AYD lista mais de um) | Orquestração completa (§4). | fan-out N | Sim — contrato E fan-out (dois checkpoints) |

Regra de ouro (heurística SDD): *se você ficaria irritado caso o agente interpretasse o
contrato diferente do que você quis, escreva o AYD com cuidado e propague; se daria pra
consertar num follow-up rápido, resolva inline.* **Default = agente único.** Suba para fan-out
só no nível 3.

## 2. Gate ALIGN (aprovação humana obrigatória)

O ALIGN é o passo **nomeado** onde julgamento humano entra antes de gastar tokens ou congelar
decisões — a contraparte dos guardrails determinísticos (SPEC-002): o que é regra mecânica
vira hook; o que exige decisão humana vira ALIGN. Não é opcional nem implícito num "geralmente
confirmo antes" — é um passo obrigatório do protocolo.

**Obrigatório quando:**
- o pedido cria ou altera um **contrato** num AYD/ADR/PDR — isso inclui todo AYD (nível 2 ou
  3) e todo ADR/PDR que define ou muda uma interface/protocolo, não apenas narra uma decisão
  já tomada;
- o pedido dispara **fan-out** de subagentes (nível 3).

**Dispensado quando:**
- nível 0/1 sem contrato novo: typo, wording, um doc vivo, ou um ADR/PDR que apenas
  **registra** uma decisão já tomada (append-only, sem alterar contrato existente). O limite
  é esse: "registrar decisão" narra algo já decidido fora do doc; "criar/alterar contrato"
  define ou muda uma interface que outras partes vão consumir.

Há **dois checkpoints** possíveis na mesma cascata (nível 3 tem ambos; podem ocorrer em
momentos diferentes):

**ALIGN-Contrato** (antes de escrever o AYD/ADR/PDR)
PARE e apresente ao humano o contrato proposto (o quê muda, IDs afetados, o trecho de
"Contratos consumidos/expostos" ou equivalente). Só escreva o doc após "aprovado" explícito.
Se o humano recusar, aborte o passo sem escrever nada — sem estado parcial.

**ALIGN-FanOut** (antes de despachar subagentes)
PARE e apresente ao humano o plano de fan-out — repos afetados, papel de cada `spec-author`,
custo estimado (quantos subagentes). Só despache após aprovação explícita. Se recusar, aborte
o fan-out; ofereça a alternativa de agente único se fizer sentido para o caso.

**Registro (obrigatório):** toda aprovação de ALIGN é registrada no fecho da cascata — no
`journal.md` (se já existir neste repo) ou, na ausência dele, numa linha do `changelog.md` —
com o quê foi aprovado e os IDs afetados.

## 3. Roteamento de modelo (maior alavanca de economia)

- **Orquestrador (você):** modelo forte. Raciocínio de contrato, decisões, reconciliação.
- **`spec-author`:** modelo barato (Sonnet). Rascunha SPEC@repo / seções de AYD a partir de um
  contrato já definido por você. Não inventa contrato.
- **`doc-explorer`:** modelo barato/read-only (Haiku). Busca, varre o grafo, lista afetados.
  Nunca escreve.

Nunca roteie tudo para o modelo forte — é o jeito mais rápido de tornar o fan-out inviável.

## 4. Protocolo de orquestração (nível 3, cross-repo)

```
1. CONTRATO (você, modelo forte)
   Rascunhe o AYD: objetivo, repos afetados + papéis, CONTRATOS (fonte da verdade), modelo de
   domínio (termos do GLO), fluxo cross-repo (mermaid).

   ALIGN-Contrato (§2, obrigatório) — PARE antes de gravar o arquivo: apresente o contrato
   proposto ao humano e só escreva o AYD após aprovação explícita. O AYD é a fonte; ninguém
   abaixo redefine contrato.

2. MAPA DE IMPACTO (1× doc-explorer, paralelo ao passo 3 se possível)
   Despache o doc-explorer para listar todos os `children`/`related` afetados (inclusive
   cross-repo via `ID@repo`) e apontar quebras de integridade do grafo (links faltando,
   parents/children assimétricos, termos fora do GLO). Retorno = tabela compacta.

3. FAN-OUT (N× spec-author, EM PARALELO — um por repo afetado)
   ALIGN-FanOut (§2, obrigatório) — PARE antes de despachar: apresente o plano de fan-out
   (repos, papéis, custo estimado) ao humano e só prossiga após aprovação explícita.

   Para CADA repo na tabela "Repos afetados e papéis" do AYD, despache um spec-author com:
   o ID do AYD, o trecho de contrato que aquele repo implementa, o papel daquele repo, e o
   caminho de destino.
   - Multi-repo: se o repo-irmão existir no workspace (ver §6), escreva a SPEC direto em
     `<repo>/docs/specs/`. Senão, emita um **brief de handoff** em `_handoff/SPEC-NNN@<repo>.md`.
   Direções são independentes ⇒ rode os N em paralelo, no MESMO bloco de tool calls.

   **Ledger de fan-out (antes de despachar):** escreva `_handoff/.ledger-<AYD>.md` com uma
   linha por repo: `repo | tarefa | status | resultado (1 linha)`. Atualize conforme os
   retornos chegam e **apague na reconciliação**. Se a sessão cair no meio, o próximo
   orquestrador retoma do ledger em vez de re-despachar tudo.

   **Pendência de contrato no retorno?** NÃO re-despache um subagente novo: responda ao
   MESMO `spec-author` (via SendMessage, contexto intacto) com a decisão de contrato — ele
   fecha a SPEC por uma fração do custo de um despacho do zero. Se a pendência mudar o
   contrato em si, primeiro edite o AYD (passo 1), depois responda.

4. RECONCILIAÇÃO (você, single-writer)
   Só VOCÊ escreve os arquivos-cola compartilhados — nunca um subagente, pra evitar conflito:
   - `changelog.md` (1 linha no `## Unreleased`, inglês, generalista — política completa no
     header do próprio arquivo)
   - `requirements.md` — seção Glossário (se houve termo novo — adicione ANTES de usar em qualquer doc)
   - frontmatter `children`/`parents` nos dois lados de cada link.

5. PROPAGAÇÃO
   Marque cada child afetado como `status: review` (ver CLAUDE.md, seção Lifecycle). Confirme
   os que batem → `approved`; aposente os obsoletos → `superseded`/`deprecated`.
```

Para nível 1 e 2, execute só os passos relevantes (sem fan-out paralelo) — mas o ALIGN-Contrato
continua obrigatório sempre que houver contrato novo/alterado (ver tabela de §1).

## 5. Contrato de retorno dos subagentes (obrigatório)

Subagente **nunca** devolve transcript. Devolve resumo estruturado, senão seu contexto cresce
exponencialmente. Exija este formato:

```
doc/arquivo | o que mudou (1 linha) | status resultante | pendências
```

## 6. Detecção multi-repo

Procure os repos-irmãos no workspace antes do fan-out. O padrão de nomenclatura depende do
produto — adapte os caminhos ao inicializar o framework. Exemplo genérico:
`../<produto>-api`, `../<produto>-web`, `../<produto>-mobile`.
- **Presente** → o `spec-author` escreve `SPEC-NNN@<repo>` em `<repo>/docs/specs/` e atualiza o
  changelog **daquele** repo (não o deste).
- **Ausente** → emite brief em `_handoff/` deste repo; o serviço materializa a SPEC depois.

Lembre: contrato **só muda aqui** (no AYD/ADR). O serviço implementa, não redefine.

## 7. Guardrails de economia (checklist mental)

- [ ] Comecei pelo gate de triagem? Default era agente único?
- [ ] ALIGN-Contrato apresentado e aprovado antes de escrever contrato novo/alterado (quando
      aplicável, ver §2)?
- [ ] ALIGN-FanOut apresentado e aprovado antes de despachar subagentes (nível 3)?
- [ ] Fan-out só onde as direções são realmente independentes (cross-repo)?
- [ ] Modelo barato nos subagentes; forte só no orquestrador?
- [ ] Subagentes retornaram resumo compacto (não transcript)?
- [ ] Só eu escrevi changelog/glossary (single-writer)?
- [ ] Reusei contexto (forks) quando o trabalho era same-context?
- [ ] Ledger de fan-out criado antes do despacho e apagado na reconciliação?
- [ ] Pendências resolvidas respondendo ao MESMO subagente (não re-despacho do zero)?

## 8. Checklist de saída

- [ ] AYD/decisão com frontmatter completo, `parents`/`children` corretos, e (se AYD) a
      tabela "Repos afetados e papéis" preenchida.
- [ ] Contratos em inglês (payloads/campos/enums); prosa em PT-BR (nota de idioma no
      Glossário de `requirements.md`).
- [ ] Termos novos no GLO antes de uso.
- [ ] Children afetados marcados `review` e percorridos.
- [ ] `changelog.md` atualizado.
- [ ] Se houve ALIGN (contrato e/ou fan-out), a aprovação está registrada no `journal.md`
      (ou no `changelog.md` na ausência dele) com o quê foi aprovado e os IDs afetados.
- [ ] Diagramas mermaid atualizados na mesma edição do contrato; se mudou topologia,
      `architecture.md` também, no mesmo PR.
