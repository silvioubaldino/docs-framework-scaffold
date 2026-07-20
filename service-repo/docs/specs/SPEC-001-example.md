---
id: SPEC-001
type: spec
title: Upload de mídia — API (EXEMPLO)
status: draft
updated: 2025-01-01
parents: [AYD-001@context]
children: [PLAN-001]
related: [GLO]
---

# Spec: Upload de mídia — API (EXEMPLO)

> Exemplo da parte de um repo (api) referente ao AYD-001@context.

## Objetivo
Emitir URL assinada, validar tipo/tamanho e persistir metadados da mídia.

## Critérios de aceite
```gherkin
Cenário: Emitir URL de upload
  Dado um usuário autenticado
  Quando solicita upload de um arquivo válido
  Então recebe uploadUrl e mediaId, e a mídia fica com status "uploading"
```

## Contratos consumidos/expostos
Expõe `POST /media/upload-url` conforme definido em AYD-001@context.

## Modelo de dados / componentes afetados
Entidade `Mídia`; serviço de storage; validação de contentType/sizeBytes.

## Casos de borda & fora de escopo
- Borda: arquivo acima do limite (413); tipo não suportado (415).
- Fora: edição de mídia pós-upload.
