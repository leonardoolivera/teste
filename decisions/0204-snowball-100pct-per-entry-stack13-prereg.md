# 0204 — Snowball 100%/entrada sobre stack 13 (pré-reg, diagnóstico)

**Status:** Accepted (pré-reg diagnóstico)
**Date:** 2026-04-22
**Deciders:** Usuário ("pegue as nossas estratégias que ja foram aprovadas, agora teste elas novamente mas com cada entrada representando 100% do capital") + agente
**Relates to:** ADR-0030 (runtime_contract faithful, sizing invariant), ADR-0063 (SizingMode SNOWBALL), AGENTS.md §8 (`disallow_sizing_modes: ["snowball","kelly_like","martingale"]`).

## Contexto

Stack aprovado em 13 combos (ver STATE.md, manifests em `exports/approved/`) foi validado sob `sizing_mode: fixed_notional` (notional literal por trade, ADR-0030). User pediu **re-teste diagnóstico** com cada entrada consumindo 100% do capital disponível — isto é, `sizing_mode: SNOWBALL`, `fracao_por_trade: 1.0`, `alavancagem_max: 1.0`. Objetivo: observar curva de equity sob compounding puro e expor blow-ups (principalmente shorts, onde perda teórica > 100% do notional).

Manifests do stack v3+ explicitamente **proíbem** `snowball` em runtime (`disallow_sizing_modes`). Este exercício é **pesquisa offline**, não gera novo manifest, não altera aprovações existentes, não é candidato a handoff ao bot.

## Decisão

Rodar os 13 combos aprovados (período de `validation_window` do manifest, parâmetros canônicos do manifest) via `alpha_forge.backtest.engine.run_backtest` com `RiskBudget(capital_inicial=10_000, fracao_por_trade=1.0, alavancagem_max=1.0, sizing_mode=SNOWBALL)` e `CostModel` baseline (taker_fee_bps=5, slippage_bps_per_unit_notional=2, spread_bps=0 — match manifest baseline 14 bps round-trip).

Filtros de regime são aplicados conforme manifest (`bollinger_width` window=30 num_std=1.5 min_width=250/300, `trend_htf` 4h sma=50 short_only).

## Gates / critérios de observação

Não há gate de promoção (exercício diagnóstico). Registramos por combo:

- `final_equity`, `pnl_pct` (compounding), `max_equity`, `min_equity`, `max_drawdown`.
- `sharpe` OOS no período completo (annualized), **trade_count** final.
- **Blow-up flag**: `min_equity <= 0` ou `capital_corrente <= 0` em alguma rejeição de sizing (engine skipa trade quando capital_corrente ≤ 0 — ver `engine.py:317`).
- **Edge preservation**: `sharpe_snowball` vs `sharpe_baseline` do manifest. Snowball geralmente degrada Sharpe via variance inflation mesmo com PnL nominal maior.

## Consequences

- **Positive:** evidência empírica do perfil risco/retorno sob compounding agressivo em cada combo; expõe assimetrias long vs short.
- **Negative:** resultado pode tentar narrativa de "snowball funciona" e erodir a disciplina de `fixed_notional_literal` (ADR-0030). Para contrapor: este ADR registra que **o resultado é diagnóstico e não promove nada** — manifests ficam inalterados.
- **Neutral:** artefato em `results/snowball_100/stack13_20260422.json` + summary em `exports/diag/`.

## Alternatives considered

- **Re-validate com walk-forward + MC por combo**: rejeitado, custo compute alto (~10min × 13 = ~2h20) sem valor adicional para pergunta diagnóstica pontual. Full-period backtest é suficiente.
- **Fixed_notional 100% (fracao=1.0, sem snowball)**: rejeitado — isso seria notional fixo = capital_inicial, não "100% do capital corrente". Interpretação natural de "cada entrada = 100% do capital" é snowball 100%.
- **Leverage > 1**: rejeitado — fora do escopo da pergunta.

## Follow-ups

- Script determinístico `scripts/run_snowball_100_stack13.py` — entrada: lista hardcoded dos 13 combos + seus params; saída: JSON com métricas por combo.
- ADR-0205 closeout com tabela de resultados + interpretação.
- Update STATE.md com link para ADR-0204/0205.
