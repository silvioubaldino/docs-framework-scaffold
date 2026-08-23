# Vigia — contexto do produto (FONTE ÚNICA)

App iOS nativo para assistir e controlar uma IP camera doméstica, **sem anúncios**,
sem telemetria e sem intermediário desnecessário entre o dono e a própria câmera.

## Comece por aqui
- @requirements.md — requisitos **e glossário** (SEMPRE use estes termos)
- @architecture.md — arquitetura vigente (C4)
- @roadmap.md — o que vem agora / depois

## Framework de documentação (versão simplificada, repo único)

Este repo usa uma versão enxuta do
[specs-driven docs framework](https://github.com/silvioubaldino/docs-framework-scaffold):
**um produto, um repo**. Não existe separação contexto/serviço — o app iOS é o único
"serviço", então requisitos, design e specs convivem aqui.

| Prefixo | Documento | Onde | Ciclo de vida |
|---------|-----------|------|---------------|
| REQ  | Requisitos (+ visão em uma frase) | `requirements.md` | vivo |
| GLO  | Glossário | `requirements.md` (seção Glossário) | vivo |
| ARCH | Arquitetura viva (C4) | `architecture.md` | vivo |
| ROAD | Roadmap | `roadmap.md` | vivo |
| AYD  | Análise & Design de uma feature | `design/` | vivo |
| ADR  | Decisão de arquitetura | `architecture_decisions/` | append-only |
| SPEC | Especificação executável | `specs/` | congela ao virar `approved` |

**Removido do framework completo** (não faz sentido em repo único): PDR, TDR, PLAN,
`docs/shared/`, sync-context, bundle, evals, `_meta-session/`.

## IDs e frontmatter
ID = `PREFIX-NNN`, estável (não muda nem se o arquivo for renomeado). Todo doc:

```yaml
---
id: AYD-002
type: design            # requirements | design | roadmap | adr | architecture | spec
title: Streaming ao vivo
status: draft           # draft | review | approved | superseded | deprecated
updated: 2026-08-23
parents: [REQ-001]      # o que este doc refina (camada acima)
children: [SPEC-002]    # o que refina este doc
related: [ADR-003, GLO] # contexto transversal
superseded_by: null     # só em ADR (append-only); omita nos demais
---
```

## Ciclo de vida
- REQ / ARCH / ROAD / AYD = **vivos** (edite no lugar, atualize `updated`, registre em
  `changelog.md`).
- ADR = **append-only**: nunca reescreva. Decisão nova = ADR novo apontando
  `superseded_by` no antigo.
- SPEC **congela** ao virar `approved`. Toda SPEC tem um AYD em `parents`.
- Uma SPEC só vira `approved` quando **todo `AC-N`** dos critérios de aceite tiver ≥1 teste
  citando `SPEC-NNN/AC-N` (regra `AC_WITHOUT_TEST` do validador — WARN em `draft`/`review`,
  ERROR em `approved`).
- Mudou um doc vivo? Marque os `children` afetados como `status: review`.
- Mudou a topologia (entrou/saiu um componente)? Atualize `architecture.md` na mesma edição.

## Antes de abrir PR
```bash
python3 scripts/validate.py     # frontmatter, simetria parents/children, refs quebradas
```

## Regras do produto (não negociáveis)
Estas nascem do próprio motivo de existir do app — ver `requirements.md`, RNF-04/RNF-05:
- **Zero anúncios, zero SDK de analytics, zero rastreamento.** Nenhuma dependência que
  fale com servidor que não seja o do próprio usuário.
- **Credencial de câmera nunca em `UserDefaults`, plist ou log.** Só Keychain.
- Nenhum vídeo, snapshot ou metadado sai do controle do usuário.
