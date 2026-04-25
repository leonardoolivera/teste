# 0193 — Engine SuperTrend (trend-follow) pré-reg

**Status:** Proposed
**Date:** 2026-04-21
**Deciders:** Usuário ("tenta outras estratégias ai, ta foda") + agente
**Relates to:** ADR-0172 (Keltner arquivado), ADR-0176 (zscore arquivado), ADR-0192 (autopilot parada round 3), Padrão 45

## Motivação

Stack atual 13 combos é **100% mean-reversion** (BB/RSI + filters) + 1 exceção híbrida (RSI short + trend_htf SOL 2025-H1). Todo engine novo testado pós-ADR-0096 foi MR (Keltner, zscore, pyramid, composite BB+RSI) — todos refutados. Paradigma trend-follow **nunca foi testado como engine primário** no AF (trend_htf só aparece como filter).

User sinaliza frustração operacional no bot. Bot com stack único-paradigma tem risco regime-concentrado: todo MR sofre em trending markets. Adicionar paradigma ortogonal pode destravar diversificação sem competir com combos existentes.

SuperTrend é o candidato trend-follow canônico mais simples: ATR-based trailing band que flip em breakout. Ortogonal a BB/RSI (que operam em reversão contra extremos).

## Engine spec

### Parâmetros
- `atr_period`: int > 0 (default 10)
- `atr_mult`: float > 0 (default 3.0)
- `long_only`: bool (default false — suporta bidirectional)

### Cálculo (causal, ADR-0030 friendly)

Sobre `window["high"/"low"/"close"].iloc[:-1]` (ignora bar t):

1. `hl2 = (high + low) / 2`
2. `tr[i] = max(high[i]-low[i], |high[i]-close[i-1]|, |low[i]-close[i-1]|)`
3. `atr[i] = SMA(tr, atr_period)` terminando em i
4. `upper_band[i] = hl2[i] + atr_mult * atr[i]`
5. `lower_band[i] = hl2[i] - atr_mult * atr[i]`
6. **Final bands** (trailing):
   - `f_upper[i] = min(upper_band[i], f_upper[i-1])` se `close[i-1] <= f_upper[i-1]`, senão `upper_band[i]`
   - `f_lower[i] = max(lower_band[i], f_lower[i-1])` se `close[i-1] >= f_lower[i-1]`, senão `lower_band[i]`
7. **Trend** (recursivo):
   - `trend[i] = -1` se `trend[i-1] == +1 AND close[i] < f_lower[i]`
   - `trend[i] = +1` se `trend[i-1] == -1 AND close[i] > f_upper[i]`
   - senão `trend[i] = trend[i-1]`

### Sinais edge-triggered

Usando `trend_now = trend[-1]` (flip em t-1), `trend_prev = trend[-2]` (flip em t-2):

- **Entrada long**: `trend_now == +1 AND trend_prev == -1` (flip up)
- **Entrada short** (`long_only=false`): `trend_now == -1 AND trend_prev == +1` (flip down)
- **Saída (long-only)**: flip down (`trend_now == -1 AND trend_prev == +1`)
- **Saída (bidirectional)**: reverse-on-signal via Backtester (ADR-0011)
- **Warm-up**: HOLD enquanto `len(window) < atr_period + 5`

### Invariantes herdadas (ADR-0030 `faithful`)
1. entry_fill: market_at_open_next_bar
2. exit_fill: market_at_open_next_bar
3. sizing: fixed_notional_literal
4. stop_loss: disabled
5. signal_arbitration: exit_wins_on_tie

## Série ST probes (Fase 1 — naked cross-asset 2025-H1)

| Tag | Combo | Config |
|---|---|---|
| ST.1 | BTC 2025-H1 SuperTrend 10/3 bi | --no-long-only |
| ST.2 | ETH 2025-H1 idem | idem |
| ST.3 | SOL 2025-H1 idem | idem |

## Gate pré-registrado

### Fase 1 pass (→ Fase 2 + width filter):
- ≥2/3 pass Sh≥1.5 AND trades≥30

### Fase 1 pass fraco (1/3, outlier Padrão 41):
- Trigger Fase 2 +filter cedo (Padrão 45: filter pode normalizar outlier sem criar edge, mas vale testar)

### Fase 1 refutada (0/3):
- SuperTrend arquivado naked. Opcional probe +filter (1 run, se trades baseline razoáveis). Se filter não resgata, arquivar família trend-follow definitivamente em AF-offline.

## Hipótese

**Crypto 1h em 2025-H1 tem trending windows (BTC bull 40→60k Jan-Mar, ETH bear, SOL mixed).** Trend-follow em breakout de banda deve capturar movimentos direcionais onde MR é estopado. Prior médio: **~25-35%** de 2/3 pass — paradigma não testado, mas cost ATR-based envelope similar a Keltner que refutou.

Downside: SuperTrend notório por whipsaws em chop — muitos fake breakouts. 1h crypto tem ruído alto. 10/3 é baseline conservador; se fail por ruído, Fase 2 com width filter ou período maior pode ajudar.

## Não-alvo

- Não testar com pyramid (v4 dormente, ADR-0192)
- Não cross-asset + cross-window na Fase 1 (só 2025-H1 para diagnóstico rápido)
- Não variar parâmetros na Fase 1 (fixar 10/3 canônico)
- Não compor com RSI/BB nesta fase (deixa para Fase 2 se pass)

## Ação

1. Implementar `src/alpha_forge/strategies/families/supertrend/`
2. Wire CLI (`--strategy supertrend`, `--supertrend-atr-period`, `--supertrend-atr-mult`)
3. 1 unit test smoke (trend flip detectável)
4. `run_st_sweep.py` + `summarize_st.py`
5. 3 runs ST.1-3
6. ADR-0194 closeout
