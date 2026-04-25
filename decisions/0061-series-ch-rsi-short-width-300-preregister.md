# 0061 — Série CH: RSI short + BollingerWidthFilter min_width_bps=300 (pré-registro)

**Status:** Accepted — pré-registro; execução inicia imediatamente
**Date:** 2026-04-19
**Deciders:** Usuário + agente.
**Relates to:** ADR-0053 (closeout CE — short puro incluindo RSI), ADR-0057 (closeout CG Bollinger short + width 300 PASS), ADR-0060 (manifest v3 ativo).

## Context

CG (Bollinger short + width 300) passou 4/9 gate em cross-period, primeiro PASS em 7 séries consecutivas. Padrão 10 (ADR-0057): "filtro composicional parametrizado ao regime eleva edge borderline pra passer". Pergunta aberta: padrão 10 é genérico ou específico a Bollinger?

CE (short puro) incluiu RSI short e falhou 2/18. RSI 2025-H1 pilots tinham Sharpe compatível com Bollinger 2025-H1 short puro (ambos ~1.9-2.4 Sharpe). Se padrão 10 é genérico, RSI short + width 300 também deve passar em 2025-H1. Se RSI short + width 300 falha completamente, padrão 10 é específico a Bollinger (coerência semântica width↔Bollinger).

**Tradeoff conhecido**: width bps vem do Bollinger — filtrar RSI com BollingerWidthFilter é semanticamente coerente (filtro de regime de volatilidade) mas testa composição cross-family. ADR-0054 §Alternativas indicava "RSI + width pode ser testado depois se Bollinger+width passar"; agora é o momento.

## Decisão

Espelhar CG para RSI. Mesmos 9 pilotos, mesmos parâmetros de engine. Único delta: `--strategy rsi` em vez de `bollinger`.

### Matriz de pilotos

Idêntica a CG/CF/CE. 9 pilotos: BTC/ETH/SOL × 2024-H2/2025-H1/2025-H2.

Estratégia: `rsi period=14 oversold=30 overbought=70 long_only=false`.
Filtro: `bollinger_width:window=30:num_std=1.5:min_width_bps=300`.

### Parâmetros de engine (inalterados CA-CG)

- capital 10000, fracao 0.1, alavancagem 2.0
- taker 5bps, slippage 2bps, spread 0
- n-folds 5, rolling, train_fraction 0.5, min_test_bars 50
- mc_resamples 1000, mc_seed 42
- stress `fee+10:10:0:0`, `spread+10:0:0:10`
- `--no-long-only`

### Gates pré-registrados (espelho CG)

**Gate 1 — principal**: ≥ **3/9** passa critério manifest (trades≥30, Sharpe≥1.0, MDD≤20, MCp5>9500, cost_r≥0.95).

**Gate 2 — lift cost_r vs CE RSI short puro**: em ≥ **6/9** pilotos, CH cost_r > CE cost_r. Se filtro 300 não move cost_r pra cima em RSI, refuta diretamente genericidade do padrão 10.

**Gate 3 — preservação de edge**: em ≥ **6/9** pilotos, CH Sharpe > 0 E trades ≥ 30.

**Gate 4 — falsificacionista**: em 2024-H2 bull (3 pilotos), **≤ 1/3 passa Gate 1**.

### Regras anti-movimento

Gates fixos. Não renegociáveis. Se 2/9 no Gate 1, FAIL.

### Tooling

- `tools/run_ch_sweep.py`: 9 runs, run_id `ch-rsi-14-30-70-<asset>-<suffix>-width30-300-short`
- `tools/summarize_ch.py`: lê CH + CE runs existentes; aplica Gates 1-4

### Timebox

~15-20min compute + ADR-0062 closeout mesmo dia.

## Hipóteses explícitas

1. **H-generalidade**: CH passa 3-5/9. Razão: se padrão 10 é real, RSI short é estruturalmente análogo a Bollinger short (ambos mean-rev), width filtra regime de volatilidade genericamente.
2. **H-especificidade** (refutação parcial): CH passa menos que CG mas > 0/9. Razão: filtro funciona mas menos efetivamente em RSI (RSI já tem implicitamente um filtro de extremo; width pode ser redundante).
3. **H-refutação** (menos provável): CH falha 0-1/9. Razão: width só faz sentido pareado com Bollinger. Padrão 10 é específico.

## Alternativas consideradas

### Série com ATR filter em vez de width
Rejeitado por ora. ATR filter é outra família de filtro de volatilidade; se CH (com filtro que já sabemos funciona pra Bollinger) falhar, ATR provavelmente falha também. Se CH passar, ATR vira teste adicional (ADR futura).

### RSI com parâmetros diferentes (9/25/75 ou 21/30/70)
Rejeitado. Variar 2 eixos quebra falsificabilidade. CE usou 14/30/70 — manter.

### Adicionar long em CH
Rejeitado. Séries pré-registradas focam uma direção. Long já em manifest v2.

## Saída da série

- Gate 1 PASS + Gate 4 PASS: **elegível pra manifest v4** via ADR de promoção separada (espelho ADR-0058).
- Gate 1 FAIL com Gate 2 PASS: filtro moveu cost_r mas edge RSI+width em chop é intrinsecamente insuficiente. Pivot pra outra família de filtro ou volta pra §D3.
- Gate 1 FAIL com Gate 2 FAIL: filtro não transfere pra RSI. Padrão 10 é específico a Bollinger. Arquivar RSI short.

## Consequences

**Positive:**
- Teste estreito e falsificável de genericidade do padrão 10.
- Reusa 100% da tooling de CG.
- Se passar, manifest v4 adiciona RSI short.

**Negative:**
- Se refutar, RSI short arquivado definitivamente.
- Custo de oportunidade ~20min de compute.

**Neutral:**
- Manifests v2 e v3 inalterados.
- Bot continua paper v3 independentemente.

## Critério de sucesso

1. 9 runs rodam sem crash.
2. `summarize_ch.py` avalia Gates 1-4 com saída interpretável.
3. ADR-0062 decide direção.
