# 0044 — Série CC: Bollinger + TrendHTF cross-period — gate pré-registrado

**Status:** Accepted — gate pré-registrado antes da execução
**Date:** 2026-04-19
**Deciders:** Usuário + agente.

## Context

Séries CA (Donchian cross-period) e CB (RSI cross-period) arquivadas FAIL (ADRs 0040, 0042). Padrão diagnosticado: estratégias LTF puras não generalizam fora da janela onde foram calibradas. Hipótese emergente (ADR-0043): filtrar o lado contra-tendência via bias HTF (Dow/Turtles/Elder) recupera edge.

ADR-0043 entregou `TrendHTFRegimeFilter`. Série CC é o primeiro teste **com filtro HTF ativo**, usando a estratégia mais próxima de edge dos experimentos anteriores: **Bollinger 20/1.5 + atr_regime min_atr_bps={BTC=55, ETH=105, SOL=100}** (já canary_only em pilotos 2024 segundo manifests `agentic/active/bollinger-20-15-*`).

Teste fundamental: **bias HTF resgata generalização cross-period?** Se sim, primeiro filtro arquitetural que altera a distribuição de resultados. Se não, hipótese Dow/Turtles/Elder é rejeitada empiricamente no nosso universo — arquiva `trend_htf` da lista de candidatos default, mas o código fica (outras estratégias podem testar depois).

Share do regime long_only (medido pre-registro, não é tunning): 43–61% das barras em SOL 1h 4h/SMA50 por recorte 2023-H2 a 2025-H2 — distribuição saudável, nenhum recorte degenera (nem 0% nem 100%).

## Matriz (9 pilotos)

3 ativos × 3 recortes "novos" (2024-H2 é holdout referência; 2024-H1 pulado por ter overlap parcial com tuning histórico):

| Tag | Dataset | min_atr_bps |
|---|---|---:|
| CC.1 | ETHUSDT 2023-H2 | 105 |
| CC.2 | BTCUSDT 2023-H2 | 55 |
| CC.3 | SOLUSDT 2023-H2 | 100 |
| CC.4 | ETHUSDT 2025-H1 | 105 |
| CC.5 | BTCUSDT 2025-H1 | 55 |
| CC.6 | SOLUSDT 2025-H1 | 100 |
| CC.7 | ETHUSDT 2025-H2 | 105 |
| CC.8 | BTCUSDT 2025-H2 | 55 |
| CC.9 | SOLUSDT 2025-H2 | 100 |

Engine fixo:
- `BollingerMeanReversionStrategy(window=20, num_std=1.5, long_only=True)`
- Regime composto: `and(atr_regime:window=14:min_atr_bps=N, trend_htf:htf=4h:sma_window=50:mode=long_only)`
- Capital 10000, fracao 0.1, alavancagem 2.0
- Taker 5bps, slippage 2bps/notional, spread 0bps
- Walk-forward: n_folds=5, rolling, train_fraction=0.5, min_test_bars=50
- MC: 1000 resamples, seed=42
- Cost stress: `fee+10:10:0:0`, `spread+10:0:0:10`

**Escolha dos hiperparâmetros `trend_htf`**:
- `htf=4h`: balanceado entre 1h (ruidoso) e 1d (poucos candles nos recortes ~180d).
- `sma_window=50`: ~8 dias no 4h, captura trend de médio prazo. Valor "clássico" em livros técnicos; evita tunning.
- `mode=long_only`: Bollinger long-only já é direcional; filtrar quando HTF bearish é a única combinação consistente.

Esses três valores são **fixados pré-registro** — não serão varridos. Se CC falhar, não vou re-tunar `sma_window=20/100` no mesmo recorte (mesma regra CA/CB: nada de rescue).

## Gate pré-registrado (decisão)

**PASS geral da série** se **todas** as condições abaixo em **≥ 6 de 9** pilotos (~67%):

1. `trades ≥ 25` — gate menor que CB (filtro HTF reduz naturalmente trade count — 43–61% share observado)
2. `Sharpe ≥ 1.0`
3. `MDD ≤ 20%`
4. `final_equity > 9800`
5. `cost_stress_ratio_min ≥ 0.95`
6. `MC p5 final_equity > 9200`

**Gate adicional crítico (single condition, não contado nos 6/9)**:

7. **Lift vs baseline sem filtro**: em **≥ 5 de 9** pilotos, a versão com `trend_htf` deve ter `final_equity` maior ou drawdown menor que a versão só com `atr_regime` (baseline histórico). **Sem essa condição, PASS ainda conta** mas ADR de closeout registra explicitamente: "a estratégia passou, mas não por causa do `trend_htf` — baseline passaria também". Esse gate separa "bias HTF é útil" de "Bollinger 20/1.5 funciona em 2023-H2 e 2025 com ou sem filtro".

**Notas sobre o gate**:
- `trades ≥ 25` (vs 30 na CB) porque filtro HTF corta ~40-55% das barras ⇒ trade count cai proporcionalmente. Abaixo de 25 trades MC fica ruidoso demais (aceito degradação de intervalo pelo preço de testar hipótese).
- Gate 7 é não-aditivo ao 1-6. É o teste da **hipótese da série**, não da estratégia.
- Limiar binário `≥6/9` no principal + `≥5/9` no lift. Sem ajustes post-hoc.

## Critério de rejeição limpa

- Se **0-2 pilotos** passam o gate 1-6: arquivamento forte, hipótese HTF-bias rejeitada para Bollinger.
- Se **3-5 pilotos** passam: ADR de closeout "ambíguo" — discutir expansão ou arquivamento sem retunning.
- Se **≥6 pilotos** + lift confirmado: Série CD (testar mesma ideia no RSI, ou testar `htf=1d` no Bollinger).

## Timebox

1 dia de trabalho. Se PASS+lift, propor Série CD ou manifest. Sem rescue intermediário.

## Convenções de run_id

- Com filtro: `cc-boll-20-15-{asset}-{yyyymmdd_yyyymmdd}-atr{N}-htf4h50`
- Baseline sem trend_htf (para gate 7): `cc-boll-20-15-{asset}-{yyyymmdd_yyyymmdd}-atr{N}-baseline`

Total: 18 runs (9 pilotos × 2 variantes: filtered + baseline).

## Alternativas consideradas

- **`mode=both_sides`**: rejeitado. Nosso engine é long-only; `both_sides` degenera em "filtro sempre ativo exceto na linha exata da SMA", ~= sem filtro.
- **Varrer `sma_window ∈ {20, 50, 100}`**: rejeitado. Misturaria teste de generalização temporal com teste de sensibilidade do filtro. Se CC passar, abro CD pra sensibilidade; se falhar, arquiva.
- **Testar RSI + trend_htf em vez de Bollinger**: rejeitado para primeira série. Bollinger tem baseline 2024 mais próximo de passar (canary_only em manifests). RSI fica pra CD se CC passar.
- **Usar `htf=1d`**: rejeitado como primeira tentativa. Recortes ~180d ⇒ ~180 candles 1d, warm-up `sma_window=50+1 = 51` ⇒ 129 candles úteis, ~70% do dataset. Excessivo. 4h dá ~1080 candles, warm-up ~200 barras, aceitável.

## Gate não-movível

Declarado antes de qualquer execução. Alteração futura exige ADR nova justificando inadequação — nunca edit deste arquivo.
