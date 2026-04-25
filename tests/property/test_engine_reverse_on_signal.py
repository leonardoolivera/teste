"""Property-based de regressão dura do engine (ADR-0012).

Invariante central:

    Para toda execução em que a estratégia nunca emite sinal de entrada
    contra posição aberta (ex: MA crossover long-only, que emite EXIT
    em cross-down e ENTER_LONG em cross-up — nunca ENTER_SHORT), o ramo
    reverse-on-signal do engine (ADR-0012) **não** é exercitado. Logo:

    1. Não existem dois fills consecutivos com o mesmo `timestamp` de
       execução (reverse-on-signal é a única fonte desse padrão).
    2. Para cada fill de abertura, existe exatamente um fill de
       fechamento (side=FLAT) posterior, ou a posição ficou aberta.

A propriedade garante que nenhuma chamada que caía no caminho antigo
passou silenciosamente a usar o caminho novo.

Estratégia de referência: MovingAverageCrossoverStrategy(long_only=True)
sobre o dataset seminal, variando janelas e cost model.
"""

from __future__ import annotations

import pandas as pd
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from alpha_forge.backtest.cost import CostModel
from alpha_forge.backtest.engine import run_backtest
from alpha_forge.backtest.schemas import Side
from alpha_forge.data.loaders import DatasetNotFoundError, load_dataset
from alpha_forge.risk.schemas import RiskBudget
from alpha_forge.strategies.families.ma_crossover import (
    MovingAverageCrossoverStrategy,
)


REFERENCE_DATASET_ID = "synthetic_btcusdt_1h_seed42"


@pytest.fixture(scope="module")
def reference_prices() -> pd.DataFrame:
    try:
        return load_dataset(REFERENCE_DATASET_ID)
    except (DatasetNotFoundError, FileNotFoundError) as exc:
        pytest.skip(
            f"dataset seminal '{REFERENCE_DATASET_ID}' ausente: {exc}"
        )


@given(
    short_window=st.integers(min_value=2, max_value=30),
    long_gap=st.integers(min_value=1, max_value=40),
    fee_bps=st.floats(
        min_value=0.0, max_value=20.0, allow_nan=False, allow_infinity=False
    ),
    slip_bps=st.floats(
        min_value=0.0, max_value=20.0, allow_nan=False, allow_infinity=False
    ),
)
@settings(
    max_examples=25,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
def test_long_only_nunca_produz_reverse_on_signal(
    reference_prices: pd.DataFrame,
    short_window: int,
    long_gap: int,
    fee_bps: float,
    slip_bps: float,
) -> None:
    long_window = short_window + long_gap
    strat = MovingAverageCrossoverStrategy(
        short_window=short_window, long_window=long_window, long_only=True
    )
    budget = RiskBudget(
        capital_inicial=10_000.0, fracao_por_trade=0.1, alavancagem_max=2.0
    )
    cost_model = CostModel(
        taker_fee_bps=fee_bps, slippage_bps_per_unit_notional=slip_bps
    )
    result = run_backtest(
        prices=reference_prices,
        strategy=strat,
        budget=budget,
        cost_model=cost_model,
        dataset_id=REFERENCE_DATASET_ID,
    )

    # Invariante 1: nenhum par consecutivo de fills compartilha ts_exec.
    # Reverse-on-signal é a única origem desse padrão no engine atual.
    for i in range(1, len(result.fills)):
        assert result.fills[i].timestamp != result.fills[i - 1].timestamp, (
            f"fills consecutivos com mesma ts_exec em i={i}: "
            f"{result.fills[i - 1]} / {result.fills[i]} — "
            "reverse-on-signal não deveria disparar em modo long-only"
        )

    # Invariante 2: toda abertura (LONG/SHORT) é seguida de exatamente um
    # fechamento (FLAT) antes da próxima abertura, ou é a última posição
    # aberta ao fim do backtest. Garante que o pareamento de fills
    # pré-ADR-0012 não mudou.
    open_side: Side | None = None
    for f in result.fills:
        if f.side in (Side.LONG, Side.SHORT):
            assert open_side is None, (
                f"nova abertura {f.side} sem fechamento prévio "
                f"(posição aberta era {open_side}) em {f.timestamp}"
            )
            open_side = f.side
        elif f.side == Side.FLAT:
            assert open_side is not None, (
                f"fechamento {f} sem abertura prévia"
            )
            open_side = None
