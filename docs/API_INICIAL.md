# API Inicial

## Endpoints ativos

### Infra e observabilidade

- `GET /api/health/`
- `GET /api/schema/`
- `GET /api/docs/`
- `GET /api/redoc/`

### Core

- `GET|POST /api/v1/core/institutions/`
- `GET|POST /api/v1/core/campuses/`
- `GET|POST /api/v1/core/branches/`
- `GET /api/v1/core/dashboard/overview/`

### Autenticacao

- `POST /api/v1/users/auth/login/`
- `GET /api/v1/users/auth/me/`
- `POST /api/v1/users/auth/logout/`

### Catalogo

- `GET|POST /api/v1/catalog/authors/`
- `GET|POST /api/v1/catalog/subjects/`
- `GET|POST /api/v1/catalog/records/`
- `GET|POST /api/v1/catalog/copies/`

### Usuarios

- `GET|POST /api/v1/users/operators/`
- `GET|POST /api/v1/users/patrons/`
- `GET|POST /api/v1/users/patron-blocks/`

### Circulacao

- `GET|POST /api/v1/circulation/loans/`
- `POST /api/v1/circulation/loans/{id}/renew/`
- `GET|POST /api/v1/circulation/reservations/`
- `GET|POST /api/v1/circulation/return-receipts/`
- `GET /api/v1/circulation/return-token/{token}/`

### Inventario e scanner

- `GET|POST /api/v1/inventory/campaigns/`
- `GET /api/v1/inventory/campaigns/{id}/export-reads/`
- `GET|POST /api/v1/inventory/scan-sessions/`
- `GET /api/v1/inventory/reads/`
- `GET /api/v1/inventory/reads/{id}/`
- `POST /api/v1/inventory/scan-reads/`

## Dashboard operacional

O endpoint `GET /api/v1/core/dashboard/overview/` entrega um snapshot resumido da operacao para o backoffice, incluindo:

- quantidade de registros e exemplares
- exemplares disponiveis
- emprestimos ativos e atrasados
- bloqueios ativos
- reservas em fila
- campanhas de inventario ativas
- leituras conciliadas e nao conciliadas
- taxa de conciliacao do inventario

## Regras de negocio ja implementadas

- catalogo e referencias institucionais aceitam leitura publica e exigem operador autenticado para escrita
- operadores autenticam por token e podem consultar `auth/me`
- criar emprestimo marca o exemplar como `loaned`
- criar emprestimo dispara email automatico quando o leitor tem email
- criar comprovante de devolucao marca o emprestimo como `returned`
- criar comprovante de devolucao devolve o exemplar para `available`
- criar comprovante de devolucao dispara email com token de devolucao quando o leitor tem email
- criar reserva calcula a posicao na fila
- renovacao simples de emprestimo bloqueia quando ha reserva pendente de outro leitor
- processamento de atrasos marca emprestimos como `overdue`
- processamento de atrasos recalcula multa por dia
- processamento de atrasos bloqueia leitor automaticamente por atraso
- devolucao de emprestimo atrasado pode liberar o bloqueio automatico
- leitura de inventario tenta localizar exemplar por patrimonio, barcode ou RFID
- campanha de inventario pode exportar leituras em CSV
- emails enviados ficam registrados em `EmailNotificationLog`

## Scanner de patrimonio

O endpoint `POST /api/v1/inventory/scan-reads/` ja registra leituras de inventario e tenta localizar o exemplar por:

1. patrimonio
2. barcode
3. RFID

### Payload base

```json
{
  "campaign_id": "uuid",
  "session_id": "uuid",
  "scanned_code": "PAT-001",
  "scan_source": "patrimony",
  "device_label": "camera-android"
}
```

### Valores aceitos em `scan_source`

- `patrimony`
- `barcode`
- `rfid`
- `camera`
- `manual`

### Resultado esperado

O retorno inclui se a leitura foi `matched` ou `unmatched`, alem do item correspondente quando houver.

## Demo pronta

Carga de dados:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\seed_demo_data.ps1
```

Credenciais:

- `admin@ifms.local` / `Biblioteca!2026`
- `bibliotecario@ifms.local` / `Biblioteca!2026`

Token publico:

- `IFMS-DEV-RETORNO-0001`

## Rotinas operacionais prontas

Para rodar os testes a partir da raiz do projeto:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\test_backend.ps1
```

Para processar atrasos e bloqueios automaticos:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\process_overdue_loans.ps1
```

Para validar o frontend com o Node portatil:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\frontend.ps1 -Target lint
powershell -ExecutionPolicy Bypass -File .\scripts\frontend.ps1 -Target build
```