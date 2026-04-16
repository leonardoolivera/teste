# CODEX.md

Este arquivo e a memoria operacional do projeto. Em todo novo chat, ele deve ser lido primeiro para entender o estado atual, o que ja foi entregue e qual deve ser o proximo passo mais logico.

## Identidade do projeto

- Nome de trabalho: `IFMS Biblioteca Plataforma`
- Objetivo: construir um sistema de biblioteca academica claramente superior ao Pergamum e aos concorrentes atuais
- Estrategia: produto feito do zero, modular, API-first e orientado a operacao real de biblioteca
- Ideal supremo: superar o mercado em UX, automacao, velocidade operacional, inteligencia de inventario e capacidade de evolucao
- Status atual: backend funcional validado, frontend funcional validado e demo operacional pronta

## Resultado concreto ja existente

O repositorio ja possui:

- documentacao de produto em `planejamento/`
- memoria operacional em `codex.md`
- repositorio `git` inicializado
- backend Django real em `backend/`
- frontend real em `frontend/`
- scripts de operacao em `scripts/`
- especificacoes e backlog em `docs/`
- Node.js portatil oficial em `.tools/node`
- carga demo oficial acessivel por script

## Estrutura atual do repositorio

```text
backend/
frontend/
infra/
docs/
planejamento/
scripts/
.tools/node/
codex.md
README.md
```

## Backend implementado ate agora

Stack aplicada:

- `Python 3.13`
- `Django`
- `Django REST Framework`
- `drf-spectacular`
- `rest_framework.authtoken`
- `Celery`
- `Redis`
- `PostgreSQL` ou `SQLite` para desenvolvimento rapido

Apps em `backend/apps/`:

- `core`
- `users`
- `catalog`
- `circulation`
- `inventory`
- `acquisitions`
- `notifications`
- `reports`
- `integrations`
- `portal`

## O que o backend ja faz

Ja existe implementacao inicial de:

- configuracao por ambiente em `backend/config/settings.py`
- endpoint de saude em `GET /api/health/`
- schema OpenAPI em `GET /api/schema/`
- autenticacao inicial de operadores por token
- permissao por perfil para escrita e operacao
- modelos de instituicao, campus e biblioteca
- endpoints de referencia institucional em `/api/v1/core/`
- dashboard operacional em `GET /api/v1/core/dashboard/overview/`
- usuario interno customizado
- leitor, bloqueio e perfis basicos
- catalogo com autores, assuntos, registro bibliografico e exemplar
- circulacao com emprestimo, renovacao, reserva e comprovante de devolucao com token
- fluxo de reserva com fila, hold automatico, expiracao e promocao da proxima pessoa
- portal do leitor: autenticacao por matricula+senha, minha conta, meus emprestimos, minhas reservas, renovacao online
- multa e bloqueio automatico por atraso via rotina de processamento
- emails automaticos para emprestimo, devolucao, atraso e reserva disponivel
- log de emails enviados em `EmailNotificationLog`
- inventario com campanha, sessao de leitura e leitura individual
- servico inicial do scanner de patrimonio
- exportacao CSV das leituras de inventario por campanha
- carga demo idempotente por `seed_demo_data`

## Frontend implementado ate agora

O frontend agora e real e validado.

Arquitetura atual:

- `frontend/apps/backoffice`
- `frontend/apps/portal-leitor`
- `frontend/packages/shared`
- `frontend/package.json` com workspace

Backoffice ja entrega:

- login por token
- radar operacional com metricas de acervo, circulacao e inventario
- consumo do dashboard resumido do backend
- registro de emprestimo
- registro de reserva e acompanhamento das reservas em aberto
- registro de devolucao com consulta imediata do token auditavel
- cadastro e edicao de autores e assuntos
- cadastro e edicao de registros bibliograficos e exemplares
- cadastro e edicao de leitores
- CRUD completo de operadores com escolha de perfil, biblioteca de vinculo e reset de senha (restrito a admin/gerente)
- pesquisa de catalogo e exemplares
- criacao de campanha de inventario
- scanner patrimonial com leitura por patrimonio, barras, RFID, camera e manual
- exportacao CSV por campanha

Portal do leitor ja entrega:

- busca publica no catalogo
- filtro por biblioteca
- consulta publica de token de devolucao
- autenticacao real do leitor por matricula + senha
- primeiro acesso: criacao de senha pelo proprio leitor (sem necessidade de operador)
- area logada "minha conta" com historico de emprestimos e status
- renovacao online de emprestimo diretamente no portal
- fila de reservas pessoal com status em tempo real
- sessao persistida em localStorage com logout

## Demo operacional

Scripts relevantes:

- `scripts/seed_demo_data.ps1`
- `scripts/frontend.ps1`
- `scripts/process_overdue_loans.ps1`
- `scripts/process_reservation_queue.ps1`

Credenciais:

- `admin@ifms.local` / `Biblioteca!2026`
- `bibliotecario@ifms.local` / `Biblioteca!2026`

Token publico:

- `IFMS-DEV-RETORNO-0001`

URLs locais em desenvolvimento:

- backoffice: `http://127.0.0.1:5173/`
- portal: `http://127.0.0.1:5174/`
- backend: `http://127.0.0.1:8000/`

## Node portatil

O ambiente corporativo nao permitiu instalacao tradicional do Node por elevacao do Windows.

Solucao aplicada:

- download oficial do `Node.js 24.15.0` em formato portatil
- runtime disponivel em `.tools/node`
- script `scripts/frontend.ps1` para instalar dependencias, rodar apps, lint e build sem depender de Node global

## APIs expostas hoje

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

### Portal do leitor

- `POST /api/v1/portal/auth/login/`
- `POST /api/v1/portal/auth/set-password/`
- `GET /api/v1/portal/auth/me/`
- `GET /api/v1/portal/my/loans/`
- `GET /api/v1/portal/my/reservations/`
- `POST /api/v1/portal/my/loans/{loan_id}/renew/`

### Inventario e scanner

- `GET|POST /api/v1/inventory/campaigns/`
- `GET /api/v1/inventory/campaigns/{id}/export-reads/`
- `GET|POST /api/v1/inventory/scan-sessions/`
- `GET /api/v1/inventory/reads/`
- `GET /api/v1/inventory/reads/{id}/`
- `POST /api/v1/inventory/scan-reads/`

## Regras de negocio ja implementadas

- catalogo e referencias institucionais aceitam leitura publica
- escrita operacional exige operador autenticado
- criar emprestimo muda o exemplar para `loaned`
- criar emprestimo pode consumir uma reserva `available` do proprio leitor
- criar emprestimo dispara email automatico quando o leitor tem email
- criar comprovante de devolucao muda o emprestimo para `returned`
- criar comprovante de devolucao promove a proxima reserva quando existir fila
- criar comprovante de devolucao devolve o exemplar para `available` quando nao existe fila
- criar comprovante de devolucao envia email com token quando o leitor tem email
- criar reserva calcula a fila inicial
- criar reserva pode prender imediatamente um exemplar disponivel da biblioteca de retirada
- renovacao bloqueia quando existe reserva pendente de outro leitor
- processamento de atrasos marca emprestimos como `overdue`
- processamento de atrasos recalcula multa por dia
- processamento de atrasos bloqueia leitor automaticamente por atraso
- processamento de atrasos envia notificacao de atraso quando o item entra em atraso
- processamento da fila de reservas expira holds vencidos e promove a proxima pessoa
- devolucao de emprestimo atrasado pode liberar o bloqueio automatico
- leitura de inventario tenta localizar exemplar por patrimonio, barcode ou RFID
- campanha de inventario pode exportar leituras em CSV

## Validacao mais recente

Foi validado com sucesso:

- `Push-Location backend; ..\.venv\Scripts\python manage.py test; Pop-Location`
- `powershell -ExecutionPolicy Bypass -File .\scripts\frontend.ps1 -Target lint`
- `powershell -ExecutionPolicy Bypass -File .\scripts\frontend.ps1 -Target build`

Resultado atual:

- backend com 42 testes passando (suite completa)
- frontend com lint limpo
- frontend com build de producao concluido para backoffice e portal
- portal do leitor com autenticacao real, area logada e renovacao online
- backoffice com CRUD de operadores controlado por perfil

## Arquivos mais importantes para retomada

Ordem recomendada:

1. `codex.md`
2. `README.md`
3. `docs/API_INICIAL.md`
4. `docs/MVP_BACKLOG.md`
5. `docs/SCANNER_PATRIMONIO_ESPECIFICACAO.md`
6. `planejamento/INDICE_DO_PROJETO.md`
7. `frontend/README.md`
8. `planejamento/06_arquitetura_tecnica.md`

## Decisoes permanentes do projeto

- nao fazer clone literal de legado
- usar monolito modular como primeira fase
- manter o scanner de patrimonio como diferencial real
- priorizar baixa dependencia de hardware proprietario
- alinhar produto, dados, API, operacao e UX do leitor
- toda iteracao deve nos deixar melhores que os concorrentes, nunca apenas equivalentes

## Proximo passo recomendado

1. modulo de relatorios operacionais e gerenciais (circulacao, atrasos, multas, inventario)
2. impressao de etiquetas de lombada, patrimonio e codigo de barras
3. estrategia de deploy local e homologacao
4. integracoes mais profundas com RFID e dispositivos de coleta

## Pendencias atuais

- modulo de relatorios e indicadores historicos
- impressao de etiquetas de lombada, patrimonio e codigo de barras
- integracoes mais profundas com RFID e dispositivos de coleta
- estrategia de deploy local e homologacao

## Como atualizar esta memoria

Sempre registrar aqui:

- o que foi criado
- o que foi validado
- o que ficou pendente
- qual e o proximo passo mais logico
- qualquer restricao real de ambiente, como ausencia de permissao de admin

## Observacao importante

Este arquivo serve como ponto de retomada do projeto. Ele nao garante leitura automatica pelo cliente em todo novo chat, mas mantem a memoria operacional centralizada para qualquer agente ou pessoa continuar de onde paramos.
