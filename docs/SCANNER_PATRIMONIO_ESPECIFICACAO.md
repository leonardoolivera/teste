# Scanner de Patrimonio

## Objetivo

Permitir inventario anual ou extraordinario por leitura rapida da etiqueta patrimonial do livro, usando coletor, leitor dedicado ou dispositivo movel com camera.

## Problema que resolve

Os processos tradicionais de inventario sao lentos, dependem de fluxos pouco intuitivos e muitas vezes prendem a biblioteca a hardware especifico. Esta feature deve ser mais simples, rapida e aberta que as solucoes concorrentes.

## Escopo inicial

- abrir campanha de inventario por biblioteca
- iniciar sessao de leitura por operador
- registrar leitura por patrimonio, barcode ou RFID
- localizar automaticamente o exemplar correspondente
- marcar leitura como `matched` ou `unmatched`
- guardar operador, horario, origem da leitura e dispositivo
- permitir exportacao posterior das divergencias

## Fontes de leitura previstas

- etiqueta patrimonial numerica
- barcode
- RFID
- camera de dispositivo movel

## Endpoints sugeridos

- `POST /api/v1/inventory/campaigns/`
- `POST /api/v1/inventory/scan-sessions/`
- `POST /api/v1/inventory/scan-reads/`
- `GET /api/v1/inventory/campaigns/{id}/reads/`

## Regras importantes

- leitura deve ser registrada mesmo quando o exemplar nao for encontrado
- o sistema precisa suportar multiplas leituras do mesmo item para auditoria
- o historico nao deve ser apagado por deduplicacao automatica cega
- o operador precisa enxergar imediatamente se a leitura foi localizada ou nao
- a solucao deve minimizar dependencia de hardware proprietario

## Campos minimos da leitura

- campanha
- sessao
- codigo lido
- tipo de origem da leitura
- item correspondente, quando houver
- operador
- dispositivo
- horario
- status do match

## Diferencial esperado

O scanner deve ser mais rapido e mais tolerante a operacao real que os concorrentes, priorizando fluxo curto, resposta clara e compatibilidade com varios dispositivos.
