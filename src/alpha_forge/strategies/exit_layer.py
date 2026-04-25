"""Exit Layer — V2/RAIO Cycle 11-14 (ADR-0226 + ADR-0227 + ADR-0229).

Wraps qualquer Strategy para impor exit policy adicional além do signal nativo.

Wrappers implementados:
- TimeStopWrapper (Cycle 11, ADR-0226): força EXIT após N bars-in-position.
- ATRTrailingWrapper (Cycle 12, ADR-0227): trailing stop dinâmico baseado em
  ATR(period) × mult. Força EXIT quando preço cruza o trailing stop adverso.
- BEAfterMFEWrapper (Cycle 14, ADR-0229): break-even após MFE atingir limiar
  ATR. Tracks max favorable excursion; quando MFE >= mfe_trigger * atr, move
  stop para entry_price (break-even). Força EXIT se preço retorna a entry.

Stateful por instância — engine deve criar nova instance por fold de walk-forward
(behavior padrão Strategy ABC).

ADR-0226+0227+0229 V2/RAIO methodology guideline: roadmap V2 EX001-036 destrava 36
hipóteses Exit Research.
"""
from __future__ import annotations

from typing import Optional

import pandas as pd

from alpha_forge.backtest.schemas import Signal
from alpha_forge.strategies.base import Strategy


class TimeStopWrapper(Strategy):
    """Decora `base` strategy adicionando time stop após N bars-in-position.

    Semântica:
    - Quando `base.decide()` retorna ENTER_LONG/ENTER_SHORT, contador interno
      `_bars_in_position` reset para 0.
    - A cada chamada subsequente onde houver posição (last signal foi ENTER ou HOLD
      após ENTER), incrementa contador.
    - Quando contador >= `max_bars_in_position` E base retornaria HOLD, força EXIT.
    - Quando base retorna EXIT explicitamente, reseta contador para None.
    - EXIT precede ENTER em ordem de prioridade (ADR-0026 §EXIT antes ENTER).

    State semantics: instância por backtest run; engine cria nova por fold.
    """

    name = "exit_layer_time_stop"

    def __init__(self, base: Strategy, max_bars_in_position: int) -> None:
        if not isinstance(max_bars_in_position, int) or isinstance(max_bars_in_position, bool):
            raise TypeError(
                f"max_bars_in_position deve ser int, recebeu {type(max_bars_in_position).__name__}"
            )
        if max_bars_in_position <= 0:
            raise ValueError(
                f"max_bars_in_position deve ser > 0, recebeu {max_bars_in_position}"
            )
        self.base = base
        self.max_bars_in_position = max_bars_in_position
        # State
        self._bars_in_position: Optional[int] = None  # None = sem posição
        # Composite name preserva params para introspecção
        self.name = f"{base.name}+ts{max_bars_in_position}"

    def decide(self, window: pd.DataFrame) -> Signal:
        base_signal = self.base.decide(window)

        # Caso 1: base diz EXIT → reseta contador e propaga.
        if base_signal == Signal.EXIT:
            self._bars_in_position = None
            return Signal.EXIT

        # Caso 2: base diz ENTER_* → reseta contador para 0 (nova posição).
        if base_signal in (Signal.ENTER_LONG, Signal.ENTER_SHORT):
            self._bars_in_position = 0
            return base_signal

        # Caso 3: base diz HOLD.
        if self._bars_in_position is None:
            # Sem posição — apenas hold.
            return Signal.HOLD

        # Estamos em posição. Incrementa.
        self._bars_in_position += 1
        if self._bars_in_position >= self.max_bars_in_position:
            # Time stop atingido: força EXIT, reset contador.
            self._bars_in_position = None
            return Signal.EXIT

        return Signal.HOLD


class ATRTrailingWrapper(Strategy):
    """Decora `base` strategy adicionando ATR trailing stop dinâmico.

    Semântica:
    - Quando `base.decide()` retorna ENTER_LONG, registra entry_price = close[t-1]
      e direction='long'; trailing_stop = entry_price - atr * mult.
    - Quando `base.decide()` retorna ENTER_SHORT, registra entry_price = close[t-1]
      e direction='short'; trailing_stop = entry_price + atr * mult.
    - A cada bar com posição aberta:
      * long: atualiza trailing_stop para max(trailing_stop, close[t-1] - atr * mult).
      * short: atualiza trailing_stop para min(trailing_stop, close[t-1] + atr * mult).
      * se long e close[t-1] <= trailing_stop → força EXIT.
      * se short e close[t-1] >= trailing_stop → força EXIT.
    - Quando base diz EXIT explicitamente, reseta state.

    ATR (Average True Range) é calculado sobre `atr_period` barras com formula
    classic Wilder smoothing simplified: TR = max(high-low, |high-close_prev|,
    |low-close_prev|), ATR = mean(TR, atr_period).

    Causal: ATR e trailing_stop usam apenas window.iloc[:-1] (barra t ignored).
    """

    name = "exit_layer_atr_trail"

    def __init__(self, base: Strategy, atr_period: int, atr_mult: float) -> None:
        if not isinstance(atr_period, int) or isinstance(atr_period, bool):
            raise TypeError(f"atr_period deve ser int, recebeu {type(atr_period).__name__}")
        if atr_period < 2:
            raise ValueError(f"atr_period deve ser >= 2, recebeu {atr_period}")
        if isinstance(atr_mult, bool) or not isinstance(atr_mult, (int, float)):
            raise TypeError(f"atr_mult deve ser numérico, recebeu {type(atr_mult).__name__}")
        if atr_mult <= 0:
            raise ValueError(f"atr_mult deve ser > 0, recebeu {atr_mult}")
        self.base = base
        self.atr_period = atr_period
        self.atr_mult = float(atr_mult)
        # State
        self._direction: Optional[str] = None  # 'long' | 'short' | None
        self._trailing_stop: Optional[float] = None
        self.name = f"{base.name}+atrtrail{atr_period}x{atr_mult:g}"

    def _compute_atr(self, window) -> Optional[float]:
        causal = window.iloc[:-1]
        if len(causal) < self.atr_period + 1:
            return None
        # Use last (atr_period+1) bars to compute atr_period TRs.
        recent = causal.iloc[-(self.atr_period + 1):]
        highs = recent["high"].to_numpy()
        lows = recent["low"].to_numpy()
        closes = recent["close"].to_numpy()
        trs = []
        for i in range(1, len(recent)):
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i - 1]),
                abs(lows[i] - closes[i - 1]),
            )
            trs.append(tr)
        if not trs:
            return None
        return sum(trs) / len(trs)

    def _reset(self) -> None:
        self._direction = None
        self._trailing_stop = None

    def decide(self, window) -> Signal:
        base_signal = self.base.decide(window)

        # base diz EXIT → reset + propaga
        if base_signal == Signal.EXIT:
            self._reset()
            return Signal.EXIT

        # base diz ENTER → registra entry + ATR
        atr = self._compute_atr(window)
        causal = window.iloc[:-1]
        last_close = float(causal["close"].iloc[-1]) if len(causal) > 0 else None

        if base_signal == Signal.ENTER_LONG:
            if atr is None or last_close is None:
                # Sem ATR causal disponível (warm-up): propaga sem trail.
                self._reset()
                return Signal.ENTER_LONG
            self._direction = "long"
            self._trailing_stop = last_close - atr * self.atr_mult
            return Signal.ENTER_LONG

        if base_signal == Signal.ENTER_SHORT:
            if atr is None or last_close is None:
                self._reset()
                return Signal.ENTER_SHORT
            self._direction = "short"
            self._trailing_stop = last_close + atr * self.atr_mult
            return Signal.ENTER_SHORT

        # base diz HOLD
        if self._direction is None or self._trailing_stop is None:
            return Signal.HOLD
        if atr is None or last_close is None:
            return Signal.HOLD

        # Atualiza trailing + checa breach
        if self._direction == "long":
            new_stop = last_close - atr * self.atr_mult
            if new_stop > self._trailing_stop:
                self._trailing_stop = new_stop
            if last_close <= self._trailing_stop:
                self._reset()
                return Signal.EXIT
        else:  # short
            new_stop = last_close + atr * self.atr_mult
            if new_stop < self._trailing_stop:
                self._trailing_stop = new_stop
            if last_close >= self._trailing_stop:
                self._reset()
                return Signal.EXIT

        return Signal.HOLD


class BEAfterMFEWrapper(Strategy):
    """Decora `base` strategy adicionando break-even stop após MFE atingir limiar.

    Semântica:
    - Quando `base.decide()` retorna ENTER_LONG/ENTER_SHORT, registra entry_price
      e direction; max_favorable_excursion = 0; be_armed = False.
    - A cada bar com posição aberta:
      * computa MFE em ATR units: |close - entry_price| / atr (positivo se favorável).
      * atualiza max_favorable se progresso favorável.
      * se max_favorable >= mfe_trigger_atr → arma BE (be_armed = True).
      * se BE armado E preço retorna a (ou cruza) entry_price → força EXIT.
    - EXIT explícito do base reseta state.

    `mfe_trigger_atr`: multiplier ATR para arm BE (ex: 1.0 = MFE atinge 1× ATR).
    `atr_period`: window do ATR (Wilder TR mean simplified).
    """

    name = "exit_layer_be_after_mfe"

    def __init__(self, base: Strategy, atr_period: int, mfe_trigger_atr: float) -> None:
        if not isinstance(atr_period, int) or isinstance(atr_period, bool):
            raise TypeError(f"atr_period deve ser int, recebeu {type(atr_period).__name__}")
        if atr_period < 2:
            raise ValueError(f"atr_period deve ser >= 2, recebeu {atr_period}")
        if isinstance(mfe_trigger_atr, bool) or not isinstance(mfe_trigger_atr, (int, float)):
            raise TypeError(f"mfe_trigger_atr deve ser numérico, recebeu {type(mfe_trigger_atr).__name__}")
        if mfe_trigger_atr <= 0:
            raise ValueError(f"mfe_trigger_atr deve ser > 0, recebeu {mfe_trigger_atr}")
        self.base = base
        self.atr_period = atr_period
        self.mfe_trigger_atr = float(mfe_trigger_atr)
        # State
        self._entry_price: Optional[float] = None
        self._direction: Optional[str] = None
        self._max_fav_atr: float = 0.0
        self._be_armed: bool = False
        self.name = f"{base.name}+be{atr_period}x{mfe_trigger_atr:g}"

    def _compute_atr(self, window) -> Optional[float]:
        causal = window.iloc[:-1]
        if len(causal) < self.atr_period + 1:
            return None
        recent = causal.iloc[-(self.atr_period + 1):]
        highs = recent["high"].to_numpy()
        lows = recent["low"].to_numpy()
        closes = recent["close"].to_numpy()
        trs = []
        for i in range(1, len(recent)):
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i - 1]),
                abs(lows[i] - closes[i - 1]),
            )
            trs.append(tr)
        if not trs:
            return None
        return sum(trs) / len(trs)

    def _reset(self) -> None:
        self._entry_price = None
        self._direction = None
        self._max_fav_atr = 0.0
        self._be_armed = False

    def decide(self, window) -> Signal:
        base_signal = self.base.decide(window)

        if base_signal == Signal.EXIT:
            self._reset()
            return Signal.EXIT

        atr = self._compute_atr(window)
        causal = window.iloc[:-1]
        last_close = float(causal["close"].iloc[-1]) if len(causal) > 0 else None

        if base_signal == Signal.ENTER_LONG:
            if atr is None or last_close is None:
                self._reset()
                return Signal.ENTER_LONG
            self._entry_price = last_close
            self._direction = "long"
            self._max_fav_atr = 0.0
            self._be_armed = False
            return Signal.ENTER_LONG

        if base_signal == Signal.ENTER_SHORT:
            if atr is None or last_close is None:
                self._reset()
                return Signal.ENTER_SHORT
            self._entry_price = last_close
            self._direction = "short"
            self._max_fav_atr = 0.0
            self._be_armed = False
            return Signal.ENTER_SHORT

        # base diz HOLD
        if self._direction is None or self._entry_price is None:
            return Signal.HOLD
        if atr is None or last_close is None or atr <= 0:
            return Signal.HOLD

        # Compute MFE em ATR units
        if self._direction == "long":
            fav_atr = (last_close - self._entry_price) / atr
        else:
            fav_atr = (self._entry_price - last_close) / atr

        if fav_atr > self._max_fav_atr:
            self._max_fav_atr = fav_atr

        if not self._be_armed and self._max_fav_atr >= self.mfe_trigger_atr:
            self._be_armed = True

        # Se BE armado e preço cruza entry adversamente → EXIT
        if self._be_armed:
            if self._direction == "long" and last_close <= self._entry_price:
                self._reset()
                return Signal.EXIT
            if self._direction == "short" and last_close >= self._entry_price:
                self._reset()
                return Signal.EXIT

        return Signal.HOLD
