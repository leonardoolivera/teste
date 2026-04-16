# IFMS Biblioteca Plataforma

Base real de um sistema de biblioteca academica pensado para superar os concorrentes atuais em UX, automacao, visibilidade operacional e evolucao tecnica.

## Estado atual

O repositorio ja contem:

- planejamento do produto e arquitetura em `planejamento/`
- memoria operacional viva em `codex.md`
- backend Django funcional em `backend/`
- frontend real em `frontend/` com backoffice e portal do leitor
- integracao inicial de scanner patrimonial para inventario anual
- scripts de operacao em `scripts/`
- backlog e especificacoes em `docs/`

## Estrutura

```text
backend/        API, dominio e administracao
frontend/       backoffice, portal do leitor e pacote compartilhado
infra/          docker, observabilidade e deploy
planejamento/   produto, arquitetura e roadmap
docs/           backlog, especificacoes e guias
scripts/        bootstrap, testes e utilitarios
.tools/node/    Node.js portatil oficial para ambientes sem permissao de admin
```

## Backend

Stack atual:

- Python 3.13
- Django
- Django REST Framework
- Celery
- Redis
- PostgreSQL ou SQLite para desenvolvimento rapido

Capacidades implementadas:

- autenticacao por token para operadores
- referencia institucional com instituicao, campus e biblioteca
- dashboard resumido para o backoffice em `/api/v1/core/dashboard/overview/`
- catalogo inicial com autores, assuntos, registros e exemplares
- circulacao com emprestimo, reserva, devolucao e token auditavel
- reserva com fila, disponibilidade automatica, prazo de retirada e expiração de hold
- multa e bloqueio automatico por atraso
- notificacoes automaticas por e-mail para emprestimo, devolucao, atraso e reserva disponivel
- inventario com campanhas, leituras e exportacao CSV
- scanner patrimonial por patrimonio, barras, RFID, camera e entrada manual

Comandos principais:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap_backend.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\test_backend.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\process_overdue_loans.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\process_reservation_queue.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\seed_demo_data.ps1
```

## Frontend

O frontend esta ativo em monorepo Vite e usa `Node.js` portatil oficial em `.tools/node`, evitando instalacao global na maquina de trabalho.

Apps disponiveis:

- `frontend/apps/backoffice`: cockpit operacional para bibliotecarios
- `frontend/apps/portal-leitor`: experiencia publica de descoberta e consulta de token
- `frontend/packages/shared`: cliente de API tipado e utilitarios

Comandos principais:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\frontend.ps1 -Target install
powershell -ExecutionPolicy Bypass -File .\scripts\frontend.ps1 -Target backoffice
powershell -ExecutionPolicy Bypass -File .\scripts\frontend.ps1 -Target portal
powershell -ExecutionPolicy Bypass -File .\scripts\frontend.ps1 -Target lint
powershell -ExecutionPolicy Bypass -File .\scripts\frontend.ps1 -Target build
```

Portas de desenvolvimento:

- backoffice: `http://127.0.0.1:5173`
- portal: `http://127.0.0.1:5174`
- backend Django: `http://127.0.0.1:8000`

## Demo pronta

A carga demo oficial cria biblioteca, operadores, leitores, acervo, emprestimos, devolucao e campanha de inventario.

Credenciais:

- admin: `admin@ifms.local` / `Biblioteca!2026`
- bibliotecario: `bibliotecario@ifms.local` / `Biblioteca!2026`

Token publico de teste:

- `IFMS-DEV-RETORNO-0001`

## Validacoes ja executadas

- `powershell -ExecutionPolicy Bypass -File .\scripts\test_backend.ps1`
- `python backend\manage.py check`
- `powershell -ExecutionPolicy Bypass -File .\scripts\frontend.ps1 -Target lint`
- `powershell -ExecutionPolicy Bypass -File .\scripts\frontend.ps1 -Target build`

Estado mais recente:

- backend com 31 testes passando
- frontend com lint limpo
- frontend com build de producao concluido para backoffice e portal

## Documentos importantes

- `codex.md`
- `docs/API_INICIAL.md`
- `docs/MVP_BACKLOG.md`
- `docs/SCANNER_PATRIMONIO_ESPECIFICACAO.md`
- `planejamento/INDICE_DO_PROJETO.md`

## Meta permanente

Toda decisao deve nos deixar melhores que os concorrentes atuais, e nao apenas equivalentes.
