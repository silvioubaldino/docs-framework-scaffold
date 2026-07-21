---
id: CONV-testing
type: convention
title: Padrões de teste
status: approved
updated: 2025-01-01
---

# Padrões de teste (deste repo)

> Padrão de engenharia (vivo). Decisão pontual sobre testes que mude a abordagem → vira TDR.

- **Estrutura:** AAA (Arrange, Act, Assert).
- **Localização:** _<ex.: arquivo `*.test.*` ao lado do código>_.
- **Cobertura:** todo critério de aceite (`AC-N`) de uma SPEC tem ao menos um teste que o
  referencia — formato `SPEC-NNN/AC-N` (ex.: `SPEC-012/AC-1`) no nome, tag ou comentário do
  teste, legível por humano e por grep (o teste pode cobrir vários AC-N). O validador
  (`docs/scripts/validate.py`) cruza SPECs × testes por conteúdo (não por caminho fixo) e
  acusa `AC_WITHOUT_TEST`: WARN se a SPEC está `draft`/`review`, ERROR (bloqueia) se `approved`.
- **Mocks:** mockar só na fronteira (rede, storage, relógio); não mockar a unidade testada.
- **Mínimo por feature:** _<ex.: unit + 1 teste de aceite por cenário Gherkin da SPEC>_.
- **Comando:** _<ex.: `npm test`>_.
