"""Testes unitários do short side da DonchianBreakoutStrategy (ADR-0013).

Cobrem:
- `long_only=True` (default) preserva comportamento ADR-0011 bit-a-bit.
- Validação estrita de `long_only`.
- Simetria de sinais no modo `long_only=False` (incluindo arbitragem
  "breakout duplo na mesma barra" → ENTER_SHORT).
- Integração engine + estratégia com reverse-on-signal (reusa ADR-0012).
- Stateless.

A suite ADR-0011 em `test_donchian_breakout.py` permanece intocada.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
import pytest

from alpha_forge.backtest.cost import CostModel
from alpha_forge.backtest.engine import run_backtest
from alpha_forge.backtest.schemas import Side, Signal
from alpha_forge.risk.schemas import RiskBudget
from alpha_forge.strategies.families.donchian import DonchianBreakoutStrategy


def _df_ohlc(
    highs: list[float],
    lows: list[float],
    *,
    opens: list[float] | None = None,
    closes: list[float] | None = None,
) -> pd.DataFrame:
    n = len(highs)
    assert len(lows) == n
    if opens is None:
        opens = [(h + l) / 2 for h, l in zip(highs, lows)]
    if closes is None:
        closes = [(h + l) / 2 for h, l in zip(highs, lows)]
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    idx = pd.date_range(start=start, periods=n, freq="1h", tz="UTC")
    return pd.DataFrame(
        {
            "open": opens,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": [1.0] * n,
        },
        index=idx,
    )


class TestDefaultPreservaLongOnly:
    """Construtor sem `long_only` deve ser idêntico ao comportamento ADR-0011."""

    def test_default_long_only_e_true(self) -> None:
        strat = DonchianBreakoutStrategy(entry_window=3, exit_window=3)
        assert strat.long_only is True

    def test_breakout_bearish_no_default_emite_exit_nao_short(self) -> None:
        strat = DonchianBreakoutStrategy(entry_window=3, exit_window=3)
        # Lows: 10, 10, 10, 10, 5 — na barra t=4, ref_low = lows[3] = 10;
        # prior_lows = lows[0:3] = [10,10,10], min = 10. 10 < 10 é falso.
        # Preciso que ref_low seja o quebra: ajustar para que lows[t-1] < min(prior).
        # Série: t: 0,1,2,3,4,5. decide(window) com len=6.
        # highs=[10]*6, lows=[10,10,10,10,5,10] → ref_low = lows[4]=5;
        # prior_lows = lows[1:4]=[10,10,10], min=10. 5<10 → bearish.
        highs = [20.0, 20.0, 20.0, 20.0, 20.0, 20.0]
        lows = [10.0, 10.0, 10.0, 10.0, 5.0, 10.0]
        df = _df_ohlc(highs, lows)
        sig = strat.decide(df)
        assert sig == Signal.EXIT
        assert sig != Signal.ENTER_SHORT

    def test_breakout_bullish_no_default_emite_enter_long(self) -> None:
        strat = DonchianBreakoutStrategy(entry_window=3, exit_window=3)
        highs = [10.0, 10.0, 10.0, 10.0, 15.0, 10.0]
        lows = [5.0, 5.0, 5.0, 5.0, 5.0, 5.0]
        df = _df_ohlc(highs, lows)
        assert strat.decide(df) == Signal.ENTER_LONG


class TestValidacaoLongOnly:
    def test_int_nao_aceito(self) -> None:
        with pytest.raises(TypeError, match="long_only deve ser bool"):
            DonchianBreakoutStrategy(entry_window=3, exit_window=3, long_only=1)  # type: ignore[arg-type]

    def test_none_nao_aceito(self) -> None:
        with pytest.raises(TypeError, match="long_only deve ser bool"):
            DonchianBreakoutStrategy(
                entry_window=3, exit_window=3, long_only=None  # type: ignore[arg-type]
            )

    def test_string_nao_aceito(self) -> None:
        with pytest.raises(TypeError, match="long_only deve ser bool"):
            DonchianBreakoutStrategy(
                entry_window=3, exit_window=3, long_only="true"  # type: ignore[arg-type]
            )

    def test_bool_explicito_aceito(self) -> None:
        a = DonchianBreakoutStrategy(entry_window=3, exit_window=3, long_only=True)
        b = DonchianBreakoutStrategy(entry_window=3, exit_window=3, long_only=False)
        assert a.long_only is True
        assert b.long_only is False


class TestSimetriaSinais:
    """No modo `long_only=False`, bearish emite ENTER_SHORT; bullish emite ENTER_LONG."""

    def test_breakout_bearish_emite_enter_short(self) -> None:
        strat = DonchianBreakoutStrategy(
            entry_window=3, exit_window=3, long_only=False
        )
        highs = [20.0, 20.0, 20.0, 20.0, 20.0, 20.0]
        lows = [10.0, 10.0, 10.0, 10.0, 5.0, 10.0]
        df = _df_ohlc(highs, lows)
        assert strat.decide(df) == Signal.ENTER_SHORT

    def test_breakout_bullish_emite_enter_long_em_modo_simetrico(self) -> None:
        strat = DonchianBreakoutStrategy(
            entry_window=3, exit_window=3, long_only=False
        )
        highs = [10.0, 10.0, 10.0, 10.0, 15.0, 10.0]
        lows = [5.0, 5.0, 5.0, 5.0, 5.0, 5.0]
        df = _df_ohlc(highs, lows)
        assert strat.decide(df) == Signal.ENTER_LONG

    def test_nunca_emite_exit_em_modo_simetrico(self) -> None:
        """Modo simétrico não usa EXIT — reversões são tratadas pelo engine."""
        strat = DonchianBreakoutStrategy(
            entry_window=3, exit_window=3, long_only=False
        )
        # Série com vários rompimentos em ambas as direções
        highs = [10.0, 10.0, 10.0, 10.0, 15.0, 15.0, 12.0, 12.0, 12.0, 18.0, 18.0]
        lows = [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 2.0, 2.0, 2.0, 2.0, 2.0]
        df = _df_ohlc(highs, lows)
        for t in range(len(df)):
            sig = strat.decide(df.iloc[: t + 1])
            assert sig != Signal.EXIT, f"t={t}: modo simétrico nunca deve emitir EXIT"

    def test_warm_up_respeitado_em_modo_simetrico(self) -> None:
        strat = DonchianBreakoutStrategy(
            entry_window=3, exit_window=3, long_only=False
        )
        # min_bars = max(3,3) + 2 = 5. Barras < 5 → HOLD.
        highs = [20.0, 20.0, 20.0, 20.0]
        lows = [10.0, 10.0, 10.0, 5.0]
        df = _df_ohlc(highs, lows)
        assert strat.decide(df) == Signal.HOLD

    def test_empate_exato_nao_e_sinal(self) -> None:
        """Desigualdades estritas (ADR-0011 preservado)."""
        strat = DonchianBreakoutStrategy(
            entry_window=3, exit_window=3, long_only=False
        )
        highs = [10.0] * 6
        lows = [5.0] * 6
        df = _df_ohlc(highs, lows)
        assert strat.decide(df) == Signal.HOLD

    def test_ambos_simultaneos_emitem_enter_short(self) -> None:
        """Arbitragem: breakout bullish + bearish na mesma barra → ENTER_SHORT (ADR-0013)."""
        strat = DonchianBreakoutStrategy(
            entry_window=3, exit_window=3, long_only=False
        )
        # decide(window) com len(window)=6: strips iloc[-1], ref é index 4 (t-1).
        # prior_highs = highs[1:4] = [10,10,10], prior_lows = lows[1:4] = [5,5,5].
        # Para disparar ambos: highs[4]=20>10 (bullish) e lows[4]=1<5 (bearish).
        highs = [10.0, 10.0, 10.0, 10.0, 20.0, 10.0]
        lows = [5.0, 5.0, 5.0, 5.0, 1.0, 5.0]
        df = _df_ohlc(highs, lows)
        assert strat.decide(df) == Signal.ENTER_SHORT


class TestLongToShort:
    """Integração engine + estratégia: reversões sucessivas em série construída."""

    def _build_series_with_reversals(
        self,
    ) -> tuple[list[float], list[float]]:
        # entry_window=3, exit_window=3; min_bars = 5.
        # Objetivo: warm-up → bullish → bearish → bullish,
        # cada transição forçando reverse-on-signal (ADR-0012).
        # Construção em níveis absolutos:
        #   t=0..4 base plana (high=110, low=90)
        #   t=5: high=130 → bullish (em t=6, ref = high[5]=130 > max(high[2:5])=110).
        #        Barra precisa estar dentro da janela para ser "ref"; na verdade,
        #        em decide(window[:t+1]), ref_high = highs.iloc[:-1].iloc[-1] = highs[t-1].
        #        Então para ativar bullish em decide() chamado com len(window)=t+1,
        #        preciso que highs[t-1] seja o rompimento.
        # Série construída (com len=15):
        #   [0-4] base estável (5 barras para warm-up)
        #   [5] high pulo para cima
        #   [6] decide(window[:7]) vê highs[5]=pulo → bullish → ENTER_LONG
        #   [6-8] mantém lateral sem novos rompimentos
        #   [9] low mergulho para baixo
        #   [10] decide(window[:11]) vê lows[9]=mergulho → bearish → ENTER_SHORT (reversa)
        #   [10-12] lateral low
        #   [13] high pulo acima
        #   [14] decide(window[:15]) vê highs[13]=pulo → bullish → ENTER_LONG (reversa)
        highs = [
            110.0, 110.0, 110.0, 110.0, 110.0,  # base plana
            130.0,                                # bullish em t=5
            110.0, 110.0, 110.0,                  # consolida
            110.0,                                # manter base
            110.0, 110.0, 110.0,                  # low mergulhou em t=9, aqui mantém
            130.0,                                # bullish em t=13
            110.0,                                # barra t=14 onde decide detecta
        ]
        lows = [
            90.0, 90.0, 90.0, 90.0, 90.0,        # base plana
            90.0,                                 # bullish em t=5 (low inalterado)
            90.0, 90.0, 90.0,                     # consolida
            70.0,                                 # bearish em t=9 — low mergulha
            90.0, 90.0, 90.0,                     # consolida (mantendo lows > 70 no prior window adequado)
            90.0,                                 # bullish em t=13 (low inalterado)
            90.0,                                 # t=14 final
        ]
        return highs, lows

    def test_reverse_on_signal_produz_trades_e_fills_long_short(self) -> None:
        highs, lows = self._build_series_with_reversals()
        df = _df_ohlc(highs, lows)
        strat = DonchianBreakoutStrategy(
            entry_window=3, exit_window=3, long_only=False
        )
        budget = RiskBudget(
            capital_inicial=10_000.0,
            fracao_por_trade=0.1,
            alavancagem_max=2.0,
        )
        cost_model = CostModel(taker_fee_bps=0.0, slippage_bps_per_unit_notional=0.0)
        result = run_backtest(
            prices=df,
            strategy=strat,
            budget=budget,
            cost_model=cost_model,
            dataset_id="test_donchian_long_to_short",
        )

        # Ao menos um LONG fechado via reversão (LONG → SHORT conta como 1 trade fechado)
        assert result.metrics is not None
        assert result.metrics.trade_count >= 1, (
            f"esperava ao menos 1 trade fechado, veio {result.metrics.trade_count}"
        )

        sides = {f.side for f in result.fills}
        assert Side.LONG in sides, "nenhum fill long registrado"
        assert Side.SHORT in sides, "nenhum fill short registrado"
        assert Side.FLAT in sides, "nenhum fill de fechamento registrado"

    def test_reversao_aplica_custo_duas_vezes(self) -> None:
        """Custo duplo é comportamento ADR-0012 reusado por ADR-0013."""
        highs, lows = self._build_series_with_reversals()
        df = _df_ohlc(highs, lows)
        strat = DonchianBreakoutStrategy(
            entry_window=3, exit_window=3, long_only=False
        )
        budget = RiskBudget(
            capital_inicial=10_000.0,
            fracao_por_trade=0.1,
            alavancagem_max=2.0,
        )
        zero_cost = CostModel(taker_fee_bps=0.0, slippage_bps_per_unit_notional=0.0)
        with_cost = CostModel(taker_fee_bps=20.0, slippage_bps_per_unit_notional=0.0)

        r_zero = run_backtest(
            prices=df, strategy=strat, budget=budget,
            cost_model=zero_cost, dataset_id="t_zero",
        )
        r_cost = run_backtest(
            prices=df, strategy=strat, budget=budget,
            cost_model=with_cost, dataset_id="t_cost",
        )

        assert r_cost.final_equity < r_zero.final_equity, (
            "custo deveria reduzir equity em série com reversões"
        )


class TestStateless:
    def test_duas_chamadas_mesma_janela_modo_simetrico(self) -> None:
        strat = DonchianBreakoutStrategy(
            entry_window=3, exit_window=3, long_only=False
        )
        highs = [20.0, 20.0, 20.0, 20.0, 20.0, 20.0]
        lows = [10.0, 10.0, 10.0, 10.0, 5.0, 10.0]
        df = _df_ohlc(highs, lows)
        assert strat.decide(df) == strat.decide(df) == Signal.ENTER_SHORT
