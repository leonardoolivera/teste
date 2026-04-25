# 0056 — Série CG: Bollinger short + BollingerWidthFilter min_width_bps=300 (pré-registro)

**Status:** Accepted — pré-registro; execução inicia imediatamente
**Date:** 2026-04-19
**Deciders:** Usuário + agente.
**Relates to:** ADR-0048 (audit manifest long), ADR-0053 (closeout CE short puro), ADR-0055 (closeout CF short + width 250).

## Context

ADR-0055 arquivou Série CF com gate FAIL 2/9, MAS:

- **Gate 2 PASS 9/9** — filtro é unambiguously load-bearing; reduz cost_r em todos os pilotos
- **CF.5** (ETH 2025-H1): Sharpe 2.89 — PASS Gate 1
- **CF.4** (BTC 2025-H1): Sharpe 1.25 — PASS Gate 1
- **CF.6** (SOL 2025-H1): Sharpe 2.61, fe 11749, MC p5 10371 — **FAIL só por cost_r 0.9461** (1 pp abaixo do gate 0.95)
- **CF.3** (SOL 2024-H2): Sharpe 1.24, fe 10644, MC p5 9706 — FAIL só por cost_r 0.9466
- **CF.9** (SOL 2025-H2): Sharpe 1.08 — FAIL por MC p5 e cost_r

Cost_r é o corte em 3 dos 4 pilotos mais promissores. Hipótese: `min_width_bps=300` (filtro mais seletivo que 250) reduz turnover o bastante pra mover cost_r acima do gate sem matar o edge puro.

**Tradeoff conhecido**: filtro mais seletivo = menos trades = possível edge atenuado. Se edge puro do short em chop é "reversão quando width está alto E cruzou pra cima da banda", ir de 250 pra 300 pode ou (a) remover ruído residual (bom) ou (b) remover trades genuínos (ruim). Série CG falsifica.

## Decisão

Repetir matriz de CF com filtro `min_width_bps=300`. Mesmos 9 pilotos, mesmos parâmetros de engine e estratégia. Único delta: parâmetro do filtro.

### Matriz de pilotos

Idêntica a ADR-0054. 9 pilotos: BTC/ETH/SOL × 2024-H2/2025-H1/2025-H2.

Estratégia: `bollinger window=20 num_std=1.5 long_only=False`.
Filtro: `bollinger_width:window=30:num_std=1.5:min_width_bps=300`.

### Parâmetros de engine (inalterados de CA-CF)

- capital 10000, fracao 0.1, alavancagem 2.0
- taker 5bps, slippage 2bps, spread 0
- n-folds 5, rolling, train_fraction 0.5, min_test_bars 50
- mc_resamples 1000, mc_seed 42
- stress `fee+10:10:0:0`, `spread+10:0:0:10`
- `--no-long-only`

### Gates pré-registrados

**Gate 1 — principal**: ≥ **3/9** passa critério manifest completo (mesmo gate de CF). 3/9 ≈ 33% de densidade, simétrico ao manifest v2.

**Gate 2 — lift cost_r vs CF** (teste específico da hipótese): em ≥ **6/9** pilotos, CG cost_r > CF cost_r. Se filtro 300 não move cost_r pra cima vs 250, a hipótese "mais seletivo = menos custo" é refutada diretamente.

**Gate 3 — preservação de edge**: em ≥ **6/9** pilotos, CG Sharpe > 0 E trades ≥ 30. Falsifica "matei edge com filtro seletivo". Se CG trades cai muito (< 30) ou Sharpe colapsa (< 0), o filtro 300 é demasiadamente restrito.

**Gate 4 — falsificacionista**: em 2024-H2 bull (3 pilotos), **≤ 1/3 passa Gate 1**. Idêntico a CF Gate 3.

### Pipeline

- `tools/run_cg_sweep.py`: 9 runs, `run_id = cg-bol-20-15-<asset>-<suffix>-width30-300-short`
- `tools/summarize_cg.py`: lê CG + CF runs existentes; aplica Gates 1-4

### Regras anti-movimento de régua

Idênticas a CE/CF. Gates fixos. Não renegociáveis. Se 2/9 no Gate 1, FAIL.

### Timebox

~15-20min compute + ADR-0057 mesmo dia.

## Hipóteses explícitas

1. **H-principal**: CG passa 3-5/9 no Gate 1. Razão: CF.6 e CF.3 estavam a 1pp do gate cost_r; filtro mais seletivo resolve exatamente esse gap.
2. **H-preservação**: edge puro sobrevive a filtro 300. Razão: width alto (≥300bps) é regime de volatilidade **confirmada** — mean-rev só faz sentido quando há amplitude, e 300 é filtro de "amplitude forte" não "amplitude mínima".
3. **H-refutação** (menos provável): edge colapsa — CG Sharpe cai abaixo de 0 em múltiplos pilotos. Significaria que o edge do short estava sendo *carregado* por barras de width média (250-300), não de width alta (>300).

## Alternativas consideradas

### `min_width_bps=350` ou 400

Rejeitado. Passo de 50 pp é proporcional ao delta de CF cost_r (3-5pp abaixo do gate). Passo de 100 ou 150 testaria uma hipótese diferente ("filtro muito mais seletivo") que merece ADR separada se 300 falhar.

### Re-rodar CF com `num_std=2.0` em vez de mudar width

Rejeitado. ADR-0054 §"Alternativas" já rejeitou grid-search. Variar **um** parâmetro por série preserva falsificabilidade. `num_std` muda a **entrada** da estratégia; `min_width_bps` muda o **filtro**. Série CG isola o filtro.

### Rodar ambos (250 e 300) em paralelo com 18 runs

Rejeitado. CF já rodou 250. Re-rodar desperdiça compute; `summarize_cg.py` lê CF existente pra comparação Gate 2.

### Adicionar RSI short + width ao escopo

Rejeitado. Width é semanticamente vinculado a Bollinger. Se CG passar, ADR futura pode testar "RSI short + outro filtro composicional semanticamente adequado" (ex: ATR filter).

## Saída da série

- Gate 1 PASS + Gate 4 PASS: **elegível pra manifest v3** via ADR de promoção separada.
- Gate 1 FAIL com Gate 2/3 PASS: filtro seletivo funcionou mas edge é intrinsecamente frágil; pivota pra ADR-0050 §D3 (vol-adjusted sizing).
- Gate 1 FAIL com Gate 2 ou 3 FAIL: filtro 300 é erro (ou quebra cost_r ou quebra edge); família mean-rev short arquivada.

## Consequences

**Positive:**
- Testa hipótese estreita e falsificável (1 parâmetro).
- Reusa 100% da tooling de CF.
- Se passar, desbloqueia manifest v3.

**Negative:**
- Se falhar completamente (Gate 3 FAIL), ordena o arquivamento de mean-rev short como família.
- Se falhar parcialmente (Gate 2 PASS, Gate 1 FAIL), força próxima iteração em direção arquitetural mais cara (§D3).

**Neutral:**
- Manifest v2 não muda durante série.
- Bot não é notificado.

## Critério de sucesso

1. 9 runs rodam sem crash.
2. `summarize_cg.py` avalia Gates 1-4 com saída interpretável.
3. ADR-0057 decide direção baseada em combinação (1, 2, 3, 4).
