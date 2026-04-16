# Frontend IFMS Biblioteca

O frontend agora esta funcional e dividido em dois apps React com Vite:

- `apps/backoffice`: painel operacional para bibliotecarios
- `apps/portal-leitor`: experiencia publica para descoberta do acervo e consulta de token de devolucao
- `packages/shared`: cliente de API tipado e utilitarios compartilhados

## Como executar

O projeto usa um `Node.js` portatil oficial em `.tools/node`, entao nao depende de instalacao global na maquina.

### Instalar dependencias

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\frontend.ps1 -Target install
```

### Rodar o backoffice

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\frontend.ps1 -Target backoffice
```

### Rodar o portal do leitor

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\frontend.ps1 -Target portal
```

### Validar frontend

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\frontend.ps1 -Target lint
powershell -ExecutionPolicy Bypass -File .\scripts\frontend.ps1 -Target build
```

## Portas de desenvolvimento

- backoffice: `http://127.0.0.1:5173`
- portal: `http://127.0.0.1:5174`

Os dois apps usam proxy Vite para `/api`, apontando por padrao para `http://127.0.0.1:8000`.

## Demo pronta

A carga demo deixa o front preenchido com biblioteca, leitores, acervo, emprestimos, token e inventario.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\seed_demo_data.ps1
```

Credenciais do backoffice:

- `admin@ifms.local` / `Biblioteca!2026`
- `bibliotecario@ifms.local` / `Biblioteca!2026`

Token publico para teste no portal:

- `IFMS-DEV-RETORNO-0001`

## O que ja esta pronto

### Backoffice

- login por token
- radar operacional com metricas de acervo, circulacao e inventario
- consumo do dashboard resumido do backend
- registro de emprestimo
- registro de reserva e lista das reservas em aberto
- registro de devolucao com consulta imediata do token auditavel
- cadastro e edicao de autores e assuntos
- cadastro e edicao de registros bibliograficos e exemplares
- cadastro e edicao de leitores
- pesquisa de catalogo e exemplares
- criacao de campanha de inventario
- scanner patrimonial com leitura manual, patrimonial, RFID, barras e camera
- exportacao CSV por campanha

### Portal do leitor

- busca publica no catalogo
- filtro por biblioteca
- consulta publica de token de devolucao
- narrativa inicial de produto e proximos modulos de autoatendimento

## Estado de qualidade

- `lint` limpo nos dois apps
- `build` de producao validado nos dois apps
