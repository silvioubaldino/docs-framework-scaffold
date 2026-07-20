---
id: REQ-001
type: requirements
title: Requisitos e Glossário
status: draft
updated: 2025-01-01
parents: []
children: [AYD-001]
related: [ROAD-001, GLO]
---

# Requisitos

> **Produto em uma frase:** _<que dor o produto resolve, para quem, e o resultado
> esperado. A "visão" do produto mora aqui — se precisar de mais detalhe estratégico
> (personas, posicionamento, anti-escopo), acrescente subseções neste bloco>_.

## Funcionais (RF)
| ID | Requisito | Prioridade (MoSCoW) | Critério de aceite |
|----|-----------|---------------------|--------------------|
| RF-01 |  | Must |  |

## Não-funcionais (RNF)
| ID | Categoria | Requisito | Alvo |
|----|-----------|-----------|------|
| RNF-01 | Performance |  |  |
| RNF-02 | Segurança |  |  |

## Regras de negócio
- RN-01:

## Restrições
_Técnicas, legais, orçamentárias, de prazo._

## Escopo do MVP
- **Dentro:**
- **Fora (por enquanto):**

---

# Glossário (Linguagem Ubíqua) — GLO

<!--
id: GLO / type: glossary
Definições canônicas dos termos do domínio. Toda a documentação e o código — em
todos os repos — usam estes termos com este significado. É isto que faz api, web e
mobile "falarem a mesma língua": um termo, uma definição.

Regra: adicione o termo aqui ANTES de usá-lo em outros docs ou no código.
Inclua sinônimos a evitar — é onde a ambiguidade costuma virar bug ou contrato confuso.

Idioma: termos canônicos em INGLÊS (atravessam para o código: variáveis, rotas,
entidades canônicas, enums); prosa das definições e dos docs em português. Em
contratos (AYD/ADR), payloads/campos/enums em inglês
(ex.: `SubscriptionStatus: active | past_due | canceled`).
Exceção: `changelog.md` é em inglês (padrão Keep a Changelog — política no header
do próprio arquivo).
-->

| Termo (canônico · EN) | Definição | Sinônimos a evitar |
|-----------------------|-----------|--------------------|
| _<Entidade principal>_ | _Conceito de negócio, sem ambiguidade._ | _ex.: "objeto", "item", "registro"_ |
| _<Ação/estado chave>_ | _O que significa exatamente, e quando se aplica._ | _..._ |
