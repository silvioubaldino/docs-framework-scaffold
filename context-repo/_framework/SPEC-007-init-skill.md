---
id: SPEC-007
type: spec
title: Skill de onboarding /init-framework
status: draft               # draft → review → approved (congela) — ver CLAUDE.md, Lifecycle
updated: 2026-07-19
parents: [AYD-002]
children: []
related: [SPEC-003]         # grava o .framework-version definido por C3
---

# Spec: Skill de onboarding /init-framework (SPEC-007 de AYD-002)

> Detalha O QUÊ este PR entrega para cumprir o AYD-002. Congela ao virar `approved`.
> **Meta-SPEC temporária** — removida junto com AYD-002 ao fim do ciclo.

## Objetivo

Transformar a adoção do framework de "clone, leia os READMEs, edite à mão, apague os exemplos"
para uma **entrevista guiada**: uma skill `/init-framework` faz as perguntas mínimas (nome do
produto, repos de serviço e seus caminhos, provedores) e com as respostas **preenche os
templates**, **configura o sync** (paths de `sync-context.sh`, detecção multi-repo da cascade),
**grava o `.framework-version`** (C3) e **remove os exemplos** (placeholders, docs meta como
este AYD/SPEC). Fecha a ponta "fácil de adotar" do AYD. É a contraparte de **julgamento** do
versionamento determinístico (SPEC-003): a instalação inicial exige decisões humanas guiadas;
o update posterior é script.

## Critérios de aceite

```gherkin
# AC-1
Cenário: skill de init existe e é invocável
  Dado um scaffold recém-clonado
  Quando inspeciono `.claude/skills/`
  Então existe a skill `init-framework` com SKILL.md descrevendo a entrevista guiada
  E o README aponta `/init-framework` como primeiro passo de adoção

# AC-2
Cenário: entrevista preenche os templates
  Dado que rodo `/init-framework`
  Quando respondo nome do produto, repos de serviço (nomes/caminhos) e provedores
  Então a skill preenche `requirements.md` (frase do produto), `architecture.md` (containers
        e provedores) e a detecção multi-repo da cascade com os caminhos informados

# AC-3
Cenário: sync configurado com os caminhos reais
  Dado os repos de serviço informados na entrevista
  Quando a init conclui
  Então `sync-context.sh` (ou seu config) aponta para os caminhos reais
  E a seção §5 (detecção multi-repo) da cascade reflete o padrão de nomenclatura do produto

# AC-4
Cenário: grava .framework-version
  Dado o fim da entrevista
  Quando a init conclui
  Então cria `.framework-version` (C3) com framework, version (tag atual), installed (hoje)
        e a lista `files:` de arquivos de framework

# AC-5
Cenário: remove exemplos e meta-docs
  Dado o scaffold traz exemplos (placeholders) e meta-docs (AYD-002 + `_framework/SPEC-*`)
  Quando a init conclui
  Então os exemplos/meta-docs são removidos (ou movidos para fora do projeto instalado)
  E o grafo resultante passa no validador (SPEC-001) sem `BROKEN_REF`

# AC-6
Cenário: init é idempotente / não destrói produto existente
  Dado um projeto que JÁ rodou `/init-framework` (tem produto real)
  Quando rodo `/init-framework` de novo
  Então a skill detecta a instalação existente e NÃO sobrescreve conteúdo de produto
        (aborta ou entra em modo de reconfiguração explícito)
```

## Contratos consumidos/expostos

- **Não define contrato-letra.** É uma skill de orquestração (prompt) que consome C3.
- **Consome SPEC-003 (C3):** grava o `.framework-version` no formato definido, incluindo o
  `files:` de arquivos de framework. Não redefine C3.
- **Consome SPEC-001 (C1):** ao final, roda o validador para garantir que a remoção dos
  exemplos não deixou refs quebradas.

## Modelo de dados / componentes afetados

- `.claude/skills/init-framework/SKILL.md` (novo): roteiro da entrevista (perguntas mínimas),
  ordem de preenchimento, checklist de remoção de exemplos, chamada final ao validador.
- Templates preenchidos: `requirements.md`, `architecture.md`, config do `sync-context.sh`,
  §5 da skill `cascade` (caminhos multi-repo).
- `.framework-version` (novo): materializado pela init (formato de C3).
- README (editado): "Comece por `/init-framework`" como primeiro passo de adoção.

## Casos de borda & fora de escopo

- **Borda:** usuário não sabe ainda os repos de serviço → a init deve permitir "só o
  context-repo por enquanto" e configurar o resto depois (não travar a adoção).
- **Borda:** remoção de meta-docs vs. conteúdo real → a skill remove **apenas** os exemplos
  conhecidos (placeholders `AYD-NNN`/`SPEC-NNN`, `_framework/`, este AYD-002); nunca apaga um
  doc que o usuário já editou com conteúdo real.
- **Borda:** rodar init num repo que não é o scaffold → detectar ausência dos marcadores de
  framework e abortar com mensagem clara.
- **Fora:** instalador CLI (`npx create-...`) — a skill cobre o ciclo atual dentro do Claude
  Code; distribuição via CLI é evolução futura (fora do AYD-002).
- **Fora:** migração de projetos legados (docs pré-existentes fora do padrão) para o
  framework — a init assume começo a partir do scaffold.
