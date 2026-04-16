# MVP Backlog

## Epico 1: Fundacao da plataforma

- configurar backend Django com apps do dominio
- configurar settings por ambiente
- configurar healthcheck, schema OpenAPI e admin
- configurar git, scripts e estrutura de repositorio
- preparar docker local com Postgres e Redis

## Epico 2: Identidade institucional

- cadastrar instituicao, campus e biblioteca
- definir perfis administrativos e operadores
- modelar leitores e situacoes de vinculo
- preparar trilha de auditoria para operacoes criticas

## Epico 3: Catalogacao e exemplares

- cadastrar registro bibliografico
- cadastrar autores e assuntos
- cadastrar exemplares com patrimonio, tombo, barcode e RFID
- localizar exemplares por unidade e estante

## Epico 4: Circulacao

- emprestimo assistido
- renovacao com regras
- reserva por titulo
- devolucao com comprovante e token
- bloqueio e pendencias basicas
- multa e bloqueio automatico por atraso
- consulta por token de devolucao

## Epico 5: Inventario e scanner de patrimonio

- abrir campanha de inventario
- iniciar sessao de leitura
- registrar leitura por patrimonio, barcode ou RFID
- marcar correspondencia ou divergencia
- exibir historico de leitura por operador e dispositivo
- exportar leituras em CSV por campanha
- preparar API para coletor e app movel

## Epico 6: Comunicacoes

- email de emprestimo
- email de devolucao com token
- lembrete de vencimento
- aviso de reserva disponivel

## Entrega sugerida para a proxima iteracao

1. restringir acesso por perfil e acao com maior granularidade
2. consolidar multas e bloqueios por atraso com notificacao
3. evoluir reservas para fluxo completo de disponibilidade
4. expandir scanner de patrimonio com filtros e dashboards operacionais
5. preparar o frontend do backoffice
