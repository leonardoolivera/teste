# 0041 — Série CB: RSI mean-reversion cross-period — gate pré-registrado

**Status:** Accepted — gate pré-registrado antes da execução
**Date:** 2026-04-19
**Deciders:** Usuário + agente.

## Context

Revisão dos AUDIT.md RSI em `agentic/active/rsi-*` revelou perfil favorável: **7/8 pilotos canary_only** (único fail foi `rsi-7-25-75-btc-1h-2024-baseline`, janelas não-canônicas). Exemplo SOL 2024-H2 + atr_regime: 52 trades, hit=55.77%, fe=9913, MC p5=9610, cost_r=0.9791 — hit-rate acima de 50%, perfil de edge real de mean-reversion.

**Risco:** todos os pilotos RSI rodaram em janela **única 2024**. Mesmo padrão que matou Donchian na Série CA (passou 1 piloto SOL 2024 canary_only → ao estender cross-period, Sharpe negativo em 8/10 recortes 2024-2025). Hipótese "edge RSI é regime-agnostic" é explicitamente testável.

A Série CB cumpre essa confirmação cross-period antes de considerar manifest.

## Matriz (9 pilotos)

3 ativos × 3 recortes novos (2024-H2 pulado: já existe baseline):

| Tag | Dataset | min_atr_bps |
|---|---|---:|
| CB.1 | ETHUSDT 2023-H2 | 105 |
| CB.2 | BTCUSDT 2023-H2 | 55 |
| CB.3 | SOLUSDT 2023-H2 | 100 |
| CB.4 | ETHUSDT 2025-H1 | 105 |
| CB.5 | BTCUSDT 2025-H1 | 55 |
| CB.6 | SOLUSDT 2025-H1 | 100 |
| CB.7 | ETHUSDT 2025-H2 | 105 |
| CB.8 | BTCUSDT 2025-H2 | 55 |
| CB.9 | SOLUSDT 2025-H2 | 100 |

`min_atr_bps` por ativo copiado dos pilotos 2024 existentes (ADR-0027 Série N/AB usou esses valores) — não re-calibro aqui pra manter hipótese "edge generaliza temporalmente com mesmos hiperparâmetros".

Engine fixo (copia dos pilotos 2024):
- `RSIMeanReversionStrategy(period=14, oversold=30, overbought=70, long_only=True)`
- capital 10000, fracao 0.1, alavancagem 2.0
- taker 5bps, slippage 2bps/notional, spread 0bps
- Walk-forward: n_folds=5, rolling, train_fraction=0.5, min_test_bars=50
- MC: 1000 resamples, seed=42
- Cost stress: `fee+10:10:0:0`, `spread+10:0:0:10`

## Gate pré-registrado (decisão)

**PASS geral da série** se **todas** as condições abaixo forem satisfeitas em `≥ 6 de 9` pilotos (~67%):

1. `trades ≥ 30`
2. `Sharpe ≥ 1.0`
3. `MDD ≤ 20%`
4. `final_equity > 9800` (quase breakeven — mean-rev é edge fraco por natureza)
5. `cost_stress_ratio_min ≥ 0.95`
6. `MC p5 final_equity > 9200`

**Notas sobre o gate (calibração deliberada):**
- Mais apertado que Série CA (que tinha fe>9500, Sharpe>=0.8) porque RSI 2024 mostrou edge mais forte (hit>50%, fe próximos de 10000).
- Mais frouxo que Bollinger strict (que exigia fe>10000 via composto MC p5>10000) porque RSI é edge de captura pequena e alto turnover — breakeven é vitória.
- Limiar binário `≥6/9 = 67%`. Sem ajustes post-hoc.

## Timebox

1 dia de trabalho. Se passar, sanity check Série CC (sensibilidade oversold=25 ou period=21, 3 pilotos extras ETH/BTC/SOL melhor recorte); se duplo PASS, manifest e entrega ao bot.

## Convenções de run_id

`cb-rsi-14-30-70-{asset}-{yyyymmdd_yyyymmdd}-atrbps{N}` (ex: `cb-rsi-14-30-70-eth-20230705_20231231-atrbps105`).

## Alternativas consideradas

- **Testar parâmetros alternativos (period=7 ou 21) nesta série** — rejeitado: misturaria teste de generalização temporal com teste de sensibilidade. Se esta série passar, abro CC pra sensibilidade; se falhar, arquiva sem tuning (mesma regra CA).
- **Incluir 2024-H2 como controle** — rejeitado: já foi rodado (baseline Série AB). Repetir seria desperdício de timebox; vou referenciar nos resultados.
- **Gate ≥5/9 (mais frouxo)** — rejeitado: se o edge for real, deveria replicar em maioria dos recortes. 67% é o threshold mínimo pra confiar em reprodutibilidade.

## Gate não-movível

Declarado antes de qualquer execução. Alteração futura exige ADR nova justificando inadequação — nunca edit deste arquivo.
