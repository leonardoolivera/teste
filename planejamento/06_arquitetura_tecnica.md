# Arquitetura Tecnica

## Abordagem recomendada

Comecar com um monolito modular bem organizado, e nao com microservicos. Para este tipo de sistema, essa estrategia entrega:

- menor custo inicial
- regras de negocio consistentes
- menor complexidade operacional
- evolucao segura para servicos separados apenas quando houver necessidade real

## Stack sugerida

### Backend

- Python 3
- Django
- Django REST Framework
- Celery para filas e jobs

### Frontend

- Next.js
- TypeScript
- design system proprio para backoffice e portal

### Dados e infraestrutura

- PostgreSQL
- Redis
- MinIO ou S3 para anexos
- Meilisearch ou OpenSearch para busca
- RabbitMQ ou Redis Streams para eventos assincronos

## Modulos tecnicos

- `apps/core`: autenticacao, permissoes, auditoria, configuracoes
- `apps/users`: usuarios, leitores, vinculos e bloqueios
- `apps/catalog`: obras, autoridades, metadados e importacoes
- `apps/inventory`: exemplares, tombos, etiquetas, RFID e inventario
- `apps/circulation`: emprestimos, reservas, devolucoes e multas
- `apps/acquisitions`: compras, fornecedores, recebimento e doacoes
- `apps/notifications`: emails, templates, filas e historicos
- `apps/reports`: consultas materializadas e exportacoes
- `apps/integrations`: ERP, SSO, AVA, SIP2, webhooks e APIs externas
- `apps/portal`: servicos para experiencia do leitor

## Padroes recomendados

- arquitetura em camadas: interface, aplicacao, dominio e infraestrutura
- eventos de dominio para acoes como emprestimo realizado, reserva liberada e devolucao confirmada
- jobs assincronos para email, exportacoes, inventario em lote e sincronizacoes
- versionamento de API desde o inicio
- feature flags para liberar modulos sem reimplantar tudo

## Componentes essenciais

- API administrativa
- API do portal do leitor
- worker de processamento assincrono
- servico de busca
- servico de arquivos
- servico de observabilidade

## Decisoes importantes

- multas e regras de circulacao devem ficar no dominio, nunca apenas na interface
- token de devolucao deve ser assinado e auditavel
- integracoes externas devem ser resilientes e reprocessaveis
- relatorios analiticos podem evoluir para um data mart sem contaminar o banco transacional
