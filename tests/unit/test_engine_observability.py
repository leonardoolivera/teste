"""Testes da observabilidade do engine (frente iii, sem ADR — logging dev-only).

Invariantes:
- `run_backtest` produz `BacktestResult` bit-a-bit idêntico com ou sem logging ativo
  (logging não altera contrato público).
- Logger `alpha_forge.backtest` emite evento `backtest.start` e `backtest.end` em INFO.
- Em DEBUG: cada `Fill` de abertura vira `engine.fill.open`; cada `Fill` de fechamento
  vira `engine.fill.close`; cada `Rejection` vira `engine.rejection`; cada reverse-on-signal
  (ADR-0012) vira `engine.reverse_on_signal`.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

import pandas as pd
import pytest

from alpha_forge.backtest.cost import CostModel
from alpha_forge.backtest.engine import run_backtest
from alpha_forge.risk.schemas import RiskBudget
from alpha_forge.strategies.families.ma_crossover import MovingAverageCrossoverStrategy


LOGGER_NAME = "alpha_forge.backtest"


def _df_from_closes(closes: list[float]) -> pd.DataFrame:
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    idx = pd.date_range(start=start, periods=len(closes), freq="1h", tz="UTC")
    return pd.DataFrame(
        {
            "open": closes,
            "high": [c * 1.01 for c in closes],
            "low": [c * 0.99 for c in closes],
            "close": closes,
            "volume": [1.0] * len(closes),
        },
        index=idx,
    )


def _series_with_reversals() -> list[float]:
    # Mesma série da ADR-0012: short=2/long=3, produz LONG→SHORT→LONG.
    return [
        100.0, 100.0, 100.0,
        102.0, 102.0, 102.0,
        98.0, 98.0, 98.0,
        102.0, 102.0,
    ]


def _run(
    *,
    strat: MovingAverageCrossoverStrategy | None = None,
    closes: list[float] | None = None,
):
    closes = closes or _series_with_reversals()
    strat = strat or MovingAverageCrossoverStrategy(
        short_window=2, long_window=3, long_only=False
    )
    df = _df_from_closes(closes)
    budget = RiskBudget(
        capital_inicial=10_000.0,
        fracao_por_trade=0.1,
        alavancagem_max=2.0,
    )
    cost = CostModel(taker_fee_bps=5.0, slippage_bps_per_unit_notional=2.0)
    return run_backtest(
        prices=df,
        strategy=strat,
        budget=budget,
        cost_model=cost,
        dataset_id="test_observability",
    )


class TestLoggingNaoAlteraContrato:
    """Ligando/desligando logging, `BacktestResult` idêntico."""

    def test_result_identico_com_e_sem_logging(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        r_silent = _run()
        with caplog.at_level(logging.DEBUG, logger=LOGGER_NAME):
            r_verbose = _run()
        assert r_silent.final_equity == r_verbose.final_equity
        assert r_silent.max_equity == r_verbose.max_equity
        assert r_silent.min_equity == r_verbose.min_equity
        assert len(r_silent.fills) == len(r_verbose.fills)
        assert len(r_silent.rejections) == len(r_verbose.rejections)
        assert len(r_silent.trades) == len(r_verbose.trades)
        assert r_silent.metrics is not None and r_verbose.metrics is not None
        assert r_silent.metrics.total_pnl == r_verbose.metrics.total_pnl
        assert r_silent.metrics.trade_count == r_verbose.metrics.trade_count
        assert r_silent.metrics.hit_rate == r_verbose.metrics.hit_rate
        assert r_silent.metrics.max_drawdown == r_verbose.metrics.max_drawdown


class TestEventosInfo:
    def test_start_e_end_emitidos_em_info(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
            result = _run()
        messages = [r.getMessage() for r in caplog.records if r.name == LOGGER_NAME]
        starts = [m for m in messages if m.startswith("backtest.start")]
        ends = [m for m in messages if m.startswith("backtest.end")]
        assert len(starts) == 1
        assert len(ends) == 1
        assert "dataset_id=test_observability" in starts[0]
        assert f"bars={result.bars}" in starts[0]
        assert f"fills={len(result.fills)}" in ends[0]
        assert f"trades={len(result.trades)}" in ends[0]


class TestEventosDebug:
    def test_cada_fill_e_cada_trade_vira_evento(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        with caplog.at_level(logging.DEBUG, logger=LOGGER_NAME):
            result = _run()
        messages = [r.getMessage() for r in caplog.records if r.name == LOGGER_NAME]
        opens = [m for m in messages if m.startswith("engine.fill.open")]
        closes = [m for m in messages if m.startswith("engine.fill.close")]

        n_opens = sum(1 for f in result.fills if f.side.name != "FLAT")
        n_closes = sum(1 for f in result.fills if f.side.name == "FLAT")
        assert len(opens) == n_opens
        assert len(closes) == n_closes
        assert len(closes) == len(result.trades)

    def test_reverse_on_signal_emite_evento(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        with caplog.at_level(logging.DEBUG, logger=LOGGER_NAME):
            result = _run()
        messages = [r.getMessage() for r in caplog.records if r.name == LOGGER_NAME]
        reverses = [m for m in messages if m.startswith("engine.reverse_on_signal")]
        # Série tem duas reversões (LONG→SHORT em t=7; SHORT→LONG em t=10).
        assert len(reverses) >= 2
        # Cada reverse precede um fill.close + fill.open na mesma ts_exec — invariante
        # coberta por tests/property/test_engine_reverse_on_signal.py. Aqui só confirmamos
        # que o evento existe e cita ambos os lados.
        for m in reverses:
            assert "from=" in m
            assert "to=" in m
        assert result.metrics is not None
        assert result.metrics.trade_count >= 2

    def test_rejeicao_vira_evento(self, caplog: pytest.LogCaptureFixture) -> None:
        # Preço open=0 → SIZE_INF determinístico (ADR-0004), mesmo gatilho usado por
        # test_engine_reject_invalid_sizing::test_rejeita_preco_zero_como_size_inf.
        from alpha_forge.backtest.schemas import Signal
        from alpha_forge.strategies.base import Strategy

        class AlwaysLong(Strategy):
            name = "always_long"

            def decide(self, window: pd.DataFrame) -> Signal:
                return Signal.ENTER_LONG if len(window) == 1 else Signal.HOLD

        start = datetime(2024, 1, 1, tzinfo=timezone.utc)
        opens = [100.0, 0.0, 100.0]
        idx = pd.date_range(start=start, periods=len(opens), freq="1h", tz="UTC")
        df = pd.DataFrame(
            {
                "open": opens,
                "high": [p * 1.01 if p > 0 else 1.0 for p in opens],
                "low": [p * 0.99 if p > 0 else 0.0 for p in opens],
                "close": opens,
                "volume": [100.0] * len(opens),
            },
            index=idx,
        )
        budget = RiskBudget(
            capital_inicial=1_000.0,
            fracao_por_trade=0.1,
            alavancagem_max=1.0,
        )
        cost = CostModel(taker_fee_bps=0.0, slippage_bps_per_unit_notional=0.0)
        with caplog.at_level(logging.DEBUG, logger=LOGGER_NAME):
            result = run_backtest(
                prices=df,
                strategy=AlwaysLong(),
                budget=budget,
                cost_model=cost,
                dataset_id="test_rejection_event",
            )
        messages = [r.getMessage() for r in caplog.records if r.name == LOGGER_NAME]
        rejections = [m for m in messages if m.startswith("engine.rejection")]
        assert len(rejections) == len(result.rejections) >= 1
        for m in rejections:
            assert "reason=" in m


class TestLoggerNameEhBacktest:
    def test_logger_namespace(self) -> None:
        # Estável para downstream (grep/filter por namespace).
        log = logging.getLogger(LOGGER_NAME)
        assert log.name == "alpha_forge.backtest"
