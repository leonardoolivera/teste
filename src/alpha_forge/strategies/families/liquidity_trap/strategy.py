"""Liquidity Trap (False Breakout) — ADR-0231 V2/RAIO Cycle 16.

Implements LQ001/LQ002 do ROADMAP_V2: false breakout reversal.

Mecanismo causal (V2 hipóteses):
- Stops acima da máxima anterior (ou abaixo da mínima) viram liquidez.
- Se mercado rejeita o rompimento (close back inside range), compradores tardios
  ficam presos → reversão.

Regra (causal, ADR-0002):
- causal = window.iloc[:-1] (barra t ignorada).
- prev_high = max(causal.high[-(lookback+2):-2])  # high máximo antes de t-1
- prev_low  = min(causal.low [-(lookback+2):-2])

Eventos:
- **False breakout high → ENTER_SHORT (LQ001)**:
  high[t-1] > prev_high (rompeu a máxima)
  AND close[t-1] < prev_high (mas fechou de volta dentro do range)

- **False breakout low → ENTER_LONG (LQ002)**:
  low[t-1] < prev_low (rompeu a mínima)
  AND close[t-1] > prev_low (mas fechou de volta dentro do range)

- **EXIT** quando MFE atinge target_atr × ATR ou time_stop_bars passou desde entry.
  Default: signal natural se preço retorna mean_window mean (proxy de VWAP).

Modo: bidirectional por design (LQ001 + LQ002 em conjunto). `long_only=True`
filtra para apenas LQ002.

Params:
- lookback: bars history para computar prev_high/prev_low (default 20).
- exit_mean_window: bars para SMA exit (default 10 — quando close cruza SMA mid,
  EXIT — proxy VWAP-like).

Causal: usa apenas window.iloc[:-1]. Stateless (engine maneja state via fills).
"""
from __future__ import annotations

import pandas as pd

from alpha_forge.backtest.schemas import Signal
from alpha_forge.strategies.base import Strategy


class LiquidityTrapStrategy(Strategy):
    name = "liquidity_trap"

    def __init__(
        self,
        lookback: int = 20,
        exit_mean_window: int = 10,
        long_only: bool = False,
    ) -> None:
        if not isinstance(lookback, int) or isinstance(lookback, bool):
            raise TypeError(f"lookback deve ser int, recebeu {type(lookback).__name__}")
        if lookback < 5:
            raise ValueError(f"lookback deve ser >= 5, recebeu {lookback}")
        if not isinstance(exit_mean_window, int) or isinstance(exit_mean_window, bool):
            raise TypeError(f"exit_mean_window deve ser int, recebeu {type(exit_mean_window).__name__}")
        if exit_mean_window < 2:
            raise ValueError(f"exit_mean_window deve ser >= 2, recebeu {exit_mean_window}")
        if not isinstance(long_only, bool):
            raise TypeError(f"long_only deve ser bool, recebeu {type(long_only).__name__}")
        self.lookback = lookback
        self.exit_mean_window = exit_mean_window
        self.long_only = long_only

    def decide(self, window: pd.DataFrame) -> Signal:
        # Causal: ignora barra t.
        causal = window.iloc[:-1]
        # Warm-up: precisa lookback+2 bars (lookback bars de history + atual)
        min_bars = max(self.lookback + 2, self.exit_mean_window + 1)
        if len(causal) < min_bars:
            return Signal.HOLD

        # bar atual (t-1, última bar com close confirmado)
        bar = causal.iloc[-1]
        last_high = float(bar["high"])
        last_low = float(bar["low"])
        last_close = float(bar["close"])

        # History anterior: lookback bars antes de t-1 (ou seja, [-lookback-1:-1])
        history = causal.iloc[-(self.lookback + 1):-1]
        prev_high = float(history["high"].max())
        prev_low = float(history["low"].min())

        # Detect false breakouts
        false_break_high = (last_high > prev_high) and (last_close < prev_high)
        false_break_low = (last_low < prev_low) and (last_close > prev_low)

        # Exit signal: close cruza SMA mid (proxy VWAP)
        sma_mid = float(causal["close"].iloc[-self.exit_mean_window:].mean())

        # Edge cases: ambos simultaneamente (raro mas possível) → HOLD ambíguo
        if false_break_high and false_break_low:
            return Signal.HOLD

        # LQ002: false break low → ENTER_LONG (reversão alta)
        if false_break_low:
            return Signal.ENTER_LONG

        # LQ001: false break high → ENTER_SHORT (reversão baixa)
        # Em long_only=True, vetar.
        if false_break_high and not self.long_only:
            return Signal.ENTER_SHORT

        # Sem signal direcional novo, EXIT se close cruza mid (mean revert proxy)
        # Nota: stateless — engine gerencia se há posição aberta.
        # Geramos EXIT quando close == sma_mid; engine ignora se não posicionado.
        # Pra reduzir falsos EXITs, só emite se close estiver muito próximo (1bp).
        if abs(last_close - sma_mid) / sma_mid < 0.001:
            return Signal.EXIT

        return Signal.HOLD
