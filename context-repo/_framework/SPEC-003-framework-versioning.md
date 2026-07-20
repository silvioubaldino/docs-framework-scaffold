---
id: SPEC-003
type: spec
title: Versionamento e atualização do framework
status: review              # draft → review → approved (congela) — ver CLAUDE.md, Lifecycle
updated: 2026-07-20
parents: [AYD-002]
children: []
related: []
---

# Spec: Versionamento do framework (SPEC-003 de AYD-002)

> Detalha O QUÊ este PR entrega para cumprir o AYD-002. Congela ao virar `approved`.
> **Meta-SPEC temporária** — removida junto com AYD-002 ao fim do ciclo.

## Objetivo

Permitir que um projeto já em andamento **atualize a versão do framework** sem cópia manual
nem diff a olho: um arquivo `.framework-version` declara a versão instalada e **quais arquivos
são de framework** (elegíveis a update); um script busca a tag-alvo e aplica o diff **apenas
nesses arquivos**, nunca tocando conteúdo de produto (REQ/AYD/SPEC reais). Materializa a
separação "arquivos de framework × conteúdo de produto" — e por isso **abre um ADR**.

## Critérios de aceite

```gherkin
# AC-1
Cenário: arquivo de versão presente e completo
  Dado um projeto instalado
  Quando inspeciono a raiz
  Então existe `.framework-version` com framework, version (semver), installed (yyyy-MM-dd)
        e uma lista `files:` de globs de framework

# AC-2
Cenário: update aplica só arquivos de framework
  Dado `.framework-version` na versão X e uma tag-alvo Y do scaffold
  Quando rodo `update-framework.sh --to Y`
  Então o script busca a tag Y
  E computa e aplica o diff SOMENTE nos paths listados em `files:`
  E atualiza version e installed no `.framework-version`

# AC-3
Cenário: conteúdo de produto é intocável
  Dado docs de produto (REQ/AYD/SPEC/ADR reais) fora de `files:`
  Quando rodo o update
  Então nenhum desses arquivos é modificado

# AC-4
Cenário: preview antes de aplicar
  Dado `update-framework.sh --to Y --dry-run`
  Quando rodo
  Então o diff dos arquivos de framework é exibido
  E nada é escrito no working tree

# AC-5
Cenário: files nunca lista conteúdo de produto
  Dado o `.framework-version` do template
  Quando o validador (SPEC-001) ou o próprio script inspeciona `files:`
  Então nenhum glob casa docs de produto (design/*, specs/SPEC-* reais, decisions/*)
```

## Contratos consumidos/expostos

- **Expõe C3 — Version file contract** (AYD-002): `.framework-version` com
  `framework/version/installed/files:`; produto **nunca** entra em `files:`. Este PR define
  C3; não o redefine.
- Sem dependência de outras SPECs (paralelizável com SPEC-001/004/006).

## Modelo de dados / componentes afetados

- `.framework-version` (novo) na raiz de cada template instalável.
- `update-framework.sh` (novo): resolve tag via git (fetch da origem do scaffold), diff
  restrito por `files:`, `--dry-run`, atualização do próprio `.framework-version`.
- README: seção "Atualizar o framework" apontando o comando.

## Casos de borda & fora de escopo

- **Borda:** arquivo de framework foi **editado localmente** pelo usuário → o update deve
  detectar conflito e parar (ou gerar `.orig`), nunca sobrescrever silenciosamente.
- **Borda:** tag-alvo inexistente / sem rede → erro claro, exit ≠ 0, nada aplicado.
- **Borda:** novo arquivo de framework surgiu entre versões → o update deve trazê-lo (o
  `files:` da tag-alvo é a referência, não só o local).
- **Fora:** instalador CLI (npx) e distribuição multi-time — opção A (version file + diff)
  cobre o ciclo atual; CLI é evolução futura (fora de escopo em AYD-002).

## Decisão a registrar (ADR neste PR)

"Separação arquivos de framework × conteúdo de produto, com `.framework-version` como
manifesto do que é atualizável." Registrar como ADR no context-repo.
