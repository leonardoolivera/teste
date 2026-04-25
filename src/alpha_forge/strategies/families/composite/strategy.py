"""Composite BB+RSI engine — ADR-0189.

Logic AND-at-entry, BB primary para EXIT (long_only=True):
- ENTER_LONG sse BB long_entry AND RSI rsi_now < oversold
- ENTER_SHORT (long_only=False) sse BB short_entry AND RSI rsi_now > overbought
- EXIT emitido quando BB emitiria EXIT (cruzamento de close com mu)
- HOLD caso contrario

Rationale: BB fornece preço-based mean-rev, RSI fornece momentum-confirmation.
Exigir concordância reduz false signals em regimes de alta volatilidade onde
banda toca sem extreme momentum (ou vice-versa).

Parâmetros herdados literalmente das duas engines (ADR-0026, ADR-0027).
"""
from __future__ import annotations

import pandas as pd

from alpha_forge.backtest.schemas import Signal
from alpha_forge.strategies.base import Strategy


class CompositeBBRSIStrategy(Strategy):
    name = "composite_bb_rsi"

    def __init__(
        self,
        bb_window: int,
        bb_num_std: float,
        rsi_period: int,
        rsi_oversold: float,
        rsi_overbought: float,
        long_only: bool = True,
    ) -> None:
        if not isinstance(bb_window, int) or isinstance(bb_window, bool) or bb_window <= 0:
            raise ValueError(f"bb_window deve ser int > 0, recebeu {bb_window}")
        if not isinstance(bb_num_std, (int, float)) or isinstance(bb_num_std, bool) or bb_num_std <= 0:
            raise ValueError(f"bb_num_std deve ser float > 0, recebeu {bb_num_std}")
        if not isinstance(rsi_period, int) or isinstance(rsi_period, bool) or rsi_period <= 0:
            raise ValueError(f"rsi_period deve ser int > 0, recebeu {rsi_period}")
        if not isinstance(rsi_oversold, (int, float)) or isinstance(rsi_oversold, bool) or not (0 < rsi_oversold < 50):
            raise ValueError(f"rsi_oversold deve estar em (0, 50), recebeu {rsi_oversold}")
        if not isinstance(rsi_overbought, (int, float)) or isinstance(rsi_overbought, bool) or not (50 < rsi_overbought < 100):
            raise ValueError(f"rsi_overbought deve estar em (50, 100), recebeu {rsi_overbought}")
        if not isinstance(long_only, bool):
            raise TypeError(f"long_only deve ser bool, recebeu {type(long_only).__name__}")
        self.bb_window = bb_window
        self.bb_num_std = float(bb_num_std)
        self.rsi_period = rsi_period
        self.rsi_oversold = float(rsi_oversold)
        self.rsi_overbought = float(rsi_overbought)
        self.long_only = long_only

    def decide(self, window: pd.DataFrame) -> Signal:
        min_bars = max(self.bb_window, self.rsi_period) + 3
        if len(window) < min_bars:
            return Signal.HOLD

        closes = window["close"].iloc[:-1]

        # Bollinger
        now_slice = closes.iloc[-self.bb_window :]
        prev_slice = closes.iloc[-self.bb_window - 1 : -1]
        mu_now = float(now_slice.mean())
        sigma_now = float(now_slice.std(ddof=0))
        mu_prev = float(prev_slice.mean())
        sigma_prev = float(prev_slice.std(ddof=0))
        lower_now = mu_now - self.bb_num_std * sigma_now
        lower_prev = mu_prev - self.bb_num_std * sigma_prev
        upper_now = mu_now + self.bb_num_std * sigma_now
        upper_prev = mu_prev + self.bb_num_std * sigma_prev
        c_tm1 = float(closes.iloc[-1])
        c_tm2 = float(closes.iloc[-2])
        bb_long_entry = c_tm1 < lower_now and c_tm2 >= lower_prev
        bb_short_entry = c_tm1 > upper_now and c_tm2 <= upper_prev
        bb_exit = c_tm1 >= mu_now and c_tm2 < mu_prev

        # RSI
        deltas = closes.diff().iloc[1:]
        gains = deltas.where(deltas > 0, 0.0)
        losses = (-deltas).where(deltas < 0, 0.0)
        gains_now = gains.iloc[-self.rsi_period :]
        losses_now = losses.iloc[-self.rsi_period :]
        avg_gain = float(gains_now.mean())
        avg_loss = float(losses_now.mean())
        if avg_loss == 0.0:
            rsi_now = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi_now = 100.0 - 100.0 / (1.0 + rs)
        rsi_long_ok = rsi_now < self.rsi_oversold
        rsi_short_ok = rsi_now > self.rsi_overbought

        long_entry = bb_long_entry and rsi_long_ok
        short_entry = bb_short_entry and rsi_short_ok

        if self.long_only:
            if bb_exit:
                return Signal.EXIT
            if long_entry:
                return Signal.ENTER_LONG
            return Signal.HOLD

        if long_entry and short_entry:
            return Signal.HOLD
        if long_entry:
            return Signal.ENTER_LONG
        if short_entry:
            return Signal.ENTER_SHORT
        return Signal.HOLD


__all__ = ["CompositeBBRSIStrategy"]
