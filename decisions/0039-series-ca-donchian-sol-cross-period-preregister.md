# 0039 — Série CA: Donchian SOL 1h cross-period — gate pré-registrado

**Status:** Accepted — gate pré-registrado antes da execução
**Date:** 2026-04-19
**Deciders:** Usuário + agente.

## Context

Revisão dos AUDIT.md da família Donchian em `agentic/active/` revelou: de 13 pilotos com AUDIT, **12 falham** (`release_decision: fail`). Único piloto que passou foi `donchian-20-10-sol-1h-2024-regime-atr-100` (`release_decision: canary_only`), com métricas apertadas: 93 trades, hit=45.16%, fe=9580.01, MC p5=8761.82, cost_ratio=0.9613.

Hipótese a testar: **o edge Donchian 20/10 + regime ATR-100 em SOL 1h é reproduzível em outros recortes temporais, não foi sorte de 2024.**

Essa ADR cumpre a disciplina do ciclo de pesquisa (feedback `strategy_research_cycle`): **gate declarado antes do backtest**, não depois. Evita viés de mover a régua post-hoc.

## Matriz (10 pilotos)

5 recortes temporais × 2 variantes regime_filter ATR:

Recortes (datasets existentes em `data/processed/SOLUSDT/1h/`):
- CA.1/CA.6: SOL 2023-H2 (20230705_20231231)
- CA.2/CA.7: SOL 2024-H1 (20240105_20240704)
- CA.3/CA.8: SOL 2024-H2 (20240705_20241231) — **piloto original que passou**
- CA.4/CA.9: SOL 2025-H1 (20250105_20250704)
- CA.5/CA.10: SOL 2025-H2 (20250705_20251231)

Variantes regime (sintaxe real: `atr_regime:window=14:min_atr_bps=N`):
- Arm A (CA.1-CA.5): `atr_regime:window=14:min_atr_bps=100` (igual ao piloto original que passou)
- Arm B (CA.6-CA.10): `atr_regime:window=14:min_atr_bps=80` (perturbação -20% no threshold — sensibilidade ao ponto de corte de volatilidade)

Nota: janela do ATR fica fixa em 14 (convenção Wilder, usada em todos os pilotos anteriores desta família). O eixo testado de sensibilidade é o `min_atr_bps`, que é o parâmetro com influência comportamental real (quão exigente é o filtro sobre volatilidade mínima).

Engine fixo: Donchian `entry_window=20, exit_window=10, long_only=True`, capital 10000, fracao 0.1, alavancagem 2.0, taker 5bps, slippage 2bps/notional, spread 0bps.

Walk-forward: n_folds=5, rolling, train_fraction=0.5, min_test_bars=50.
Monte Carlo: 1000 resamples, seed=42.
Cost stress: fee+10:10:0:0, spread+10:0:0:10.

## Gate pré-registrado (decisão)

**PASS geral da série** se **todas** as condições abaixo forem satisfeitas em `≥ 6 de 10` pilotos:

1. `trades ≥ 30`
2. `Sharpe ≥ 0.8`
3. `MDD ≤ 25%`
4. `final_equity > 9500` (tolera -5% vs capital inicial; Donchian é trend-follower, breakeven em período lateral é aceitável)
5. `cost_stress_ratio_min ≥ 0.92`
6. `MC p5 final_equity > 8500`

**Notas sobre o gate:**
- Mais frouxo que o gate Bollinger (que exigia 7/8 aprox) porque partimos de um piloto conhecido apertado (fe=9580, hit=45.16% no limiar). Aplicar gate Bollinger strict aqui já implicaria reprovação antes de rodar — sem valor informativo.
- Limiar `≥6/10 = 60%` é deliberadamente baixo mas binário. Se 5/10 passarem, FAIL mesmo que por pequena margem.
- Se passar, abrir ADR de deploy (Série CA manifest novo) e entregar ao bot.
- Se falhar, arquiva: Donchian 20/10 SOL 1h é campo queimado; próxima candidata vem de outro eixo (RSI? MA crossover? outra família não tentada).

## Timebox

1 dia de trabalho:
- hoje: escrever `run_ca_sweep.py`, rodar 10 pilotos, `summarize_ca.py`, ADR de fechamento
- se estourar 1 dia sem fechar: reduzir matriz (ex: só Arm A com 5 recortes) ou arquivar parcial

## Convenções de run_id

`ca-donchian-20-10-sol-{yyyymmdd_yyyymmdd}-atrbps{N}` (ex: `ca-donchian-20-10-sol-20240705_20241231-atrbps100`).

Output: `results/validation/<run_id>/{walk_forward,monte_carlo,cost_stress,run}.json`.

## Alternativas consideradas

- **Expandir pra BTC/ETH em vez de mais recortes SOL**: rejeitado — BTC/ETH já falharam 20/10 em 180d (ADRs de AUDIT). Risco de queimar tempo em território sabidamente ruim.
- **Tunar janelas (55/20 ou 40/20)**: rejeitado — muda estratégia, não confirma o edge observado. Vira outra série.
- **Abandonar Donchian inteiro e ir pra RSI/MA**: adiado — se Série CA falhar, aí sim.

## Registro de não-movência do gate

Este gate é **declarado antes** de qualquer execução. Qualquer alteração futura (depois de ver resultados) deve ser por **nova ADR** explicando por que o gate original era inadequado, nunca por edit deste arquivo. Esta regra é a disciplina do ciclo de pesquisa (memória `strategy_research_cycle`).
