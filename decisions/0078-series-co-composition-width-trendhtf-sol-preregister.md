# 0078 — Série CO: composição AND width 300 + TrendHTF SOL-only (pré-registro)

**Status:** Accepted — pré-registro; execução autorizada
**Date:** 2026-04-19
**Deciders:** Usuário + agente
**Relates to:** ADR-0075 (CK closeout — TrendHTF mono-SOL amplificador não load-bearing), ADR-0077 (CL closeout — Padrão 16), ADR-0068 (Padrão 12 audit Gate B), ADR-0062 (CH closeout PASS RSI+width)

## Contexto

Série CK (ADR-0075) provou que TrendHTF mono-SOL é **amplificador não load-bearing** — sem ele, CH.6 SOL 2025-H1 (Sh=1.32) e v4b SOL 2025-H2 (Sh=2.30) já passam. Gate 4 bloqueou promoção isolada do TrendHTF como filter único.

**Hipótese aberta no closeout CK:** composição AND de width 300 + TrendHTF pode **elevar edge ALÉM** do que cada isolado faz. Se composição compõe de verdade, load-bearing do composto é mensurável: o **composto** é load-bearing se remover **qualquer um dos dois** faz o combo cair pra FAIL.

Padrão 12 ADR-0068 foi formalizado para filter isolado. Composto exige Gate B reformulado: **composto load-bearing sse remover qualquer perna derruba edge.**

## Decisão

Abrir Série CO **mono-SOL** (3 pilotos, espelho CK), mesmo engine RSI(14/30/70) short do track v4, com filter composto:

```
and(bollinger_width:window=30:num_std=1.5:min_width_bps=300,trend_htf:htf=4h:sma_window=50:mode=short_only)
```

### Matriz (3 pilotos SOL)

- CO.1 — SOL 2024-H2
- CO.2 — SOL 2025-H1
- CO.3 — SOL 2025-H2

### Parâmetros de engine (espelho CH/CK)

- capital 10000, fracao 0.1, alavancagem 2.0, `--sizing-mode fixed_notional`
- taker 5bps, slippage 2bps, spread 0
- strategy rsi, period=14, oversold=30, overbought=70, `--no-long-only`
- filter composto `and(bollinger_width:30:1.5:300, trend_htf:4h:50:short_only)`
- n-folds 5, rolling, train_fraction 0.5, min_test_bars 50
- mc_resamples 1000, mc_seed 42
- stress `fee+10:10:0:0`, `spread+10:0:0:10`

### Gates pré-registrados

- **Gate 1 — principal:** ≥ **2/3** PASS critério manifest (Sharpe≥1.0, MDD≤20%, trades≥30, MC p5>9500, cost_r≥0.95)
- **Gate 2 — lift vs ambas pernas isoladas:** Sharpe composto ≥ **max(Sh_widthOnly, Sh_trendOnly) + 0.3** em ≥ **2/3** pilotos. Referências comparativas:
  - SOL 2024-H2: width Sh=−0.39 (CH.3), trend Sh=n/a CJ.3 — CK.1 Sh=−1.02 (FAIL ambos)
  - SOL 2025-H1: width Sh=+1.32 (CH.6), trend-only n/a, CK.2 Sh=+1.96 (trend-amp)
  - SOL 2025-H2: width Sh=+1.92 (CH.9), trend-only n/a, CK.3 Sh=+2.71 (trend-amp)
- **Gate 3 — trade count:** ≥ **2/3** com trades ≥ 30. Composto AND é mais restritivo → risco real de zeragem.
- **Gate 4 — Gate B audit do composto (OBRIGATÓRIO se Gate 1 PASS):** para cada piloto CO PASS, rodar 2 auditorias:
  - **Sem trend:** apenas width 300 → deve cair para FAIL
  - **Sem width:** apenas TrendHTF → deve cair para FAIL
  
  Composto é **load-bearing** sse **ambas** as remoções derrubam. Se alguma perna isolada já passa ou composto == perna dominante, FAIL Gate 4.
- **Gate 5 — Padrão 15 prevenção:** lift Sharpe sem Gate 4 load-bearing = candidato edge fantasma. Mesmo se Gate 1+2+3 PASS, Gate 4 FAIL bloqueia promoção.

## Hipóteses explícitas

1. **H-composto-load-bearing** (CO PASS 2-3/3 + Gate 4 PASS): composição width+TrendHTF cria edge estrutural distinto de cada perna isolada. Abre track v5 SOL-composite.
2. **H-composto-redundante** (CO PASS ~CK PASS mas Gate 4 FAIL): composição só preserva TrendHTF amplificação; width é ornamento. Documenta, arquiva sem promoção (mesma lição que CK).
3. **H-composto-destrutivo** (CO FAIL ≤1/3): AND é restritivo demais, trade count colapsa ou amostra residual perde edge. Confirma Padrão 15 — composição não é salvação universal.

## Saída da série

- **H-composto-load-bearing PASS:** emitir ADR de promoção v5 SOL-composite (2-3 combos escopados). Bridge AF↔bot postar mudança de stack.
- **H-composto-redundante:** closeout analítico, NÃO-promoção. Padrão 15 reafirmado; possível Padrão 17 sobre "composição que preserva apenas perna dominante não qualifica como edge composto".
- **H-composto-destrutivo:** closeout FAIL refutador. Padrão derivado: composição AND tem overhead de seletividade que pode destruir edge mesmo quando pernas isoladas funcionam.

## Tooling

- `tools/run_co_sweep.py`: 3 runs, run_id `co-rsi-width300-trendhtf-sol-<suffix>-short`
- Gate 4 audit (se aplicável): reusar `tools/run_ch_sweep.py` + filter-less runs já arquivados; `tools/run_cj_sweep.py` fornece trend-only baselines parciais (CJ.3/6/9 são trend-only SOL).

## Timebox

~5-10min compute (3 runs) + ADR-0079 closeout mesmo turno. Se Gate 1 PASS, +10min pra Gate 4 audit runs.

## Critério de sucesso desta ADR

1. 3 runs executam sem crash
2. Métricas extraídas e gates avaliados
3. Se Gate 1 PASS, Gate 4 audit runs executados
4. ADR-0079 emitida com decisão (promoção ou não)
