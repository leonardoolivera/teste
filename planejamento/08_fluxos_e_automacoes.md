# Fluxos e Automacoes

## Fluxo 1: catalogacao e disponibilizacao

1. Receber material por compra, doacao ou processamento interno.
2. Criar ou importar registro bibliografico.
3. Vincular autores, assuntos, classificacao e colecao.
4. Gerar exemplares, patrimonio, barcode e RFID.
5. Imprimir etiquetas.
6. Marcar item como disponivel no acervo.

## Fluxo 2: emprestimo

1. Identificar o leitor.
2. Validar vinculo, bloqueios e limite de itens.
3. Ler barcode ou RFID do exemplar.
4. Aplicar politica de circulacao.
5. Registrar emprestimo.
6. Enviar comprovante por email.

## Fluxo 3: renovacao

1. Validar prazo atual.
2. Verificar bloqueios e reservas pendentes.
3. Recalcular nova data conforme politica.
4. Registrar historico de renovacao.
5. Notificar o leitor.

## Fluxo 4: reserva

1. Leitor solicita reserva no portal ou atendimento.
2. Sistema insere o usuario na fila.
3. Ao retornar exemplar elegivel, o sistema separa para reserva.
4. O leitor recebe aviso automatico de disponibilidade.
5. Expirado o prazo, a reserva passa ao proximo.

## Fluxo 5: devolucao com token

1. Registrar devolucao.
2. Calcular atraso e multa, se houver.
3. Gerar comprovante digital.
4. Criar token unico assinado.
5. Enviar email com dados da operacao e token.
6. Permitir consulta posterior pelo portal.

## Fluxo 6: alertas automaticos

- lembrete antes do vencimento
- aviso de atraso
- aviso de reserva disponivel
- aviso de vinculo prestes a expirar
- aviso de inventario pendente ou divergencia

## Fluxo 7: inventario

1. Abrir campanha por unidade ou colecao.
2. Iniciar sessao de scanner de patrimonio no coletor, leitor ou dispositivo movel.
3. Registrar leituras por etiqueta de patrimonio, barcode ou RFID.
4. Comparar leituras com base esperada.
5. Gerar divergencias.
6. Encaminhar ajustes e baixa, se necessario.

## Jobs agendados recomendados

- processar fila de emails
- recalcular multas
- expirar reservas
- sincronizar usuarios externos
- gerar snapshots de dashboard
- reindexar busca
- validar pendencias de etiquetas e RFID




