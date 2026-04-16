# Requisitos Funcionais

## Cadastro e acesso

- RF-001 O sistema deve permitir autenticacao por login interno e SSO institucional.
- RF-002 O sistema deve suportar perfis distintos para bibliotecario, atendente, gestor, leitor e integracao.
- RF-003 O sistema deve registrar trilha de auditoria para inclusao, alteracao e exclusao logica.

## Usuarios e leitores

- RF-004 O sistema deve importar usuarios de fontes externas.
- RF-005 O sistema deve permitir bloqueio automatico por atraso, multa ou vencimento de vinculo.
- RF-006 O sistema deve manter historico de situacao do leitor.

## Catalogacao

- RF-007 O sistema deve cadastrar obras, autores, assuntos, edicoes e exemplares.
- RF-008 O sistema deve suportar importacao bibliografica por MARC21 e Z39.50.
- RF-009 O sistema deve permitir controle de autoridades.
- RF-010 O sistema deve permitir anexar capa, sumario e arquivos complementares.

## Exemplares

- RF-011 O sistema deve gerar identificadores unicos por exemplar.
- RF-012 O sistema deve armazenar barcode, RFID, tombo e patrimonio.
- RF-013 O sistema deve controlar estados como disponivel, emprestado, reservado, em processamento, perdido e descartado.

## Circulacao

- RF-014 O sistema deve registrar emprestimo presencial e assistido.
- RF-015 O sistema deve permitir renovacao manual e online conforme regras.
- RF-016 O sistema deve controlar fila de reservas.
- RF-017 O sistema deve permitir devolucao parcial ou total.
- RF-018 O sistema deve recalcular prazos com base em calendario e politica.
- RF-019 O sistema deve bloquear renovacao quando houver reserva pendente.
- RF-020 O sistema deve suportar emprestimo entre bibliotecas da mesma rede.

## Devolucao e token

- RF-021 O sistema deve gerar comprovante digital de devolucao.
- RF-022 O sistema deve gerar token unico de devolucao para consultas futuras.
- RF-023 O sistema deve permitir validacao do token por portal ou API.
- RF-024 O sistema deve enviar o token automaticamente por email.

## Financeiro e pendencias

- RF-025 O sistema deve calcular multa por regra configuravel.
- RF-026 O sistema deve registrar isencoes, descontos e justificativas.
- RF-027 O sistema deve manter extrato de pendencias do leitor.

## Aquisicoes

- RF-028 O sistema deve registrar solicitacoes de compra e doacao.
- RF-029 O sistema deve controlar fornecedores, pedidos e recebimento.
- RF-030 O sistema deve converter itens recebidos em material pronto para catalogacao.

## Inventario e etiquetas

- RF-031 O sistema deve abrir campanhas de inventario por unidade, colecao ou localizacao.
- RF-032 O sistema deve importar leituras por barcode ou RFID.
- RF-033 O sistema deve gerar etiquetas em lote com templates configuraveis.
- RF-033A O sistema deve oferecer scanner de patrimonio para inventario anual com leitura da etiqueta do exemplar por coletor, leitor dedicado ou dispositivo movel com camera.
- RF-033B O sistema deve registrar, a cada leitura de patrimonio, campanha, operador, data, hora, unidade, exemplar localizado e resultado da conferencia.

## Comunicacoes

- RF-034 O sistema deve enviar emails automaticos baseados em eventos e agendas.
- RF-035 O sistema deve manter historico de mensagens enviadas.
- RF-036 O sistema deve permitir parametrizacao de templates por tipo de evento.

## Relatorios

- RF-037 O sistema deve oferecer relatorios operacionais prontos.
- RF-038 O sistema deve permitir filtros por periodo, unidade, curso, categoria e status.
- RF-039 O sistema deve exportar relatorios em CSV, XLSX e PDF.

## Portal do leitor

- RF-040 O portal deve permitir consulta ao acervo e autenticacao.
- RF-041 O portal deve permitir reserva, renovacao e consulta de historico.
- RF-042 O portal deve exibir pendencias, mensagens e comprovantes.

## APIs

- RF-043 O sistema deve expor API para consulta de usuarios, acervo e circulacao conforme permissao.
- RF-044 O sistema deve publicar webhooks para eventos criticos.
- RF-045 O sistema deve registrar chave, escopo e consumo por integracao.

