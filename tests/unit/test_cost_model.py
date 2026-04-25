"""Testes unitários do modelo mínimo de custos (ADR-0006 + ADR-0019)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from alpha_forge.backtest.cost import CostModel, apply_cost, zero_cost
from alpha_forge.backtest.schemas import Side


def test_cost_model_rejeita_valores_negativos() -> None:
    with pytest.raises(ValidationError):
        CostModel(taker_fee_bps=-1.0, slippage_bps_per_unit_notional=0.0)
    with pytest.raises(ValidationError):
        CostModel(taker_fee_bps=0.0, slippage_bps_per_unit_notional=-1.0)


def test_zero_cost_nao_altera_preco() -> None:
    cm = zero_cost()
    for side in (Side.LONG, Side.SHORT):
        for is_entry in (True, False):
            out = apply_cost(
                price_market=100.0,
                notional=500.0,
                capital_inicial=1000.0,
                side=side,
                is_entry=is_entry,
                cost_model=cm,
            )
            assert out == pytest.approx(100.0)


def test_taker_fee_aplicado_contra_trader_em_entrada_long() -> None:
    cm = CostModel(taker_fee_bps=10.0, slippage_bps_per_unit_notional=0.0)
    out = apply_cost(
        price_market=100.0,
        notional=500.0,
        capital_inicial=1000.0,
        side=Side.LONG,
        is_entry=True,
        cost_model=cm,
    )
    assert out == pytest.approx(100.0 * 1.001)


def test_taker_fee_aplicado_contra_trader_em_saida_long() -> None:
    cm = CostModel(taker_fee_bps=10.0, slippage_bps_per_unit_notional=0.0)
    out = apply_cost(
        price_market=100.0,
        notional=500.0,
        capital_inicial=1000.0,
        side=Side.LONG,
        is_entry=False,
        cost_model=cm,
    )
    assert out == pytest.approx(100.0 * 0.999)


def test_taker_fee_aplicado_contra_trader_em_entrada_short() -> None:
    cm = CostModel(taker_fee_bps=10.0, slippage_bps_per_unit_notional=0.0)
    out = apply_cost(
        price_market=100.0,
        notional=500.0,
        capital_inicial=1000.0,
        side=Side.SHORT,
        is_entry=True,
        cost_model=cm,
    )
    assert out == pytest.approx(100.0 * 0.999)


def test_taker_fee_aplicado_contra_trader_em_saida_short() -> None:
    cm = CostModel(taker_fee_bps=10.0, slippage_bps_per_unit_notional=0.0)
    out = apply_cost(
        price_market=100.0,
        notional=500.0,
        capital_inicial=1000.0,
        side=Side.SHORT,
        is_entry=False,
        cost_model=cm,
    )
    assert out == pytest.approx(100.0 * 1.001)


def test_slippage_linear_com_notional_sobre_capital() -> None:
    cm = CostModel(taker_fee_bps=0.0, slippage_bps_per_unit_notional=10.0)
    p_small = apply_cost(
        price_market=100.0,
        notional=100.0,
        capital_inicial=1000.0,
        side=Side.LONG,
        is_entry=True,
        cost_model=cm,
    )
    p_big = apply_cost(
        price_market=100.0,
        notional=1000.0,
        capital_inicial=1000.0,
        side=Side.LONG,
        is_entry=True,
        cost_model=cm,
    )
    assert p_small == pytest.approx(100.0 * (1.0 + 0.0001))
    assert p_big == pytest.approx(100.0 * (1.0 + 0.001))


def test_notional_igual_capital_paga_taker_mais_slippage_full() -> None:
    cm = CostModel(taker_fee_bps=5.0, slippage_bps_per_unit_notional=10.0)
    out = apply_cost(
        price_market=100.0,
        notional=1000.0,
        capital_inicial=1000.0,
        side=Side.LONG,
        is_entry=True,
        cost_model=cm,
    )
    expected_bps = 5.0 + 10.0
    assert out == pytest.approx(100.0 * (1.0 + expected_bps / 10_000.0))


# --- ADR-0019 spread_bps -----------------------------------------------------


def test_spread_bps_default_zero_preserva_comportamento_adr_0006() -> None:
    # CostModel construído sem `spread_bps` usa default 0.0 — todos os backtests
    # pré-E.9 devem permanecer bit-a-bit idênticos.
    cm = CostModel(taker_fee_bps=5.0, slippage_bps_per_unit_notional=10.0)
    assert cm.spread_bps == 0.0


def test_spread_bps_rejeita_negativo() -> None:
    with pytest.raises(ValidationError):
        CostModel(
            taker_fee_bps=0.0,
            slippage_bps_per_unit_notional=0.0,
            spread_bps=-1.0,
        )


def test_spread_bps_aplicado_contra_trader_nas_quatro_direcoes() -> None:
    # Spread sozinho (fee=0, slip=0): compra paga mais, venda recebe menos.
    cm = CostModel(
        taker_fee_bps=0.0, slippage_bps_per_unit_notional=0.0, spread_bps=10.0
    )

    # Compra (entrada long ou saída short) → preço sobe.
    for side, is_entry in ((Side.LONG, True), (Side.SHORT, False)):
        out = apply_cost(
            price_market=100.0,
            notional=500.0,
            capital_inicial=1000.0,
            side=side,
            is_entry=is_entry,
            cost_model=cm,
        )
        assert out == pytest.approx(100.0 * 1.001), (side, is_entry)

    # Venda (saída long ou entrada short) → preço desce.
    for side, is_entry in ((Side.LONG, False), (Side.SHORT, True)):
        out = apply_cost(
            price_market=100.0,
            notional=500.0,
            capital_inicial=1000.0,
            side=side,
            is_entry=is_entry,
            cost_model=cm,
        )
        assert out == pytest.approx(100.0 * 0.999), (side, is_entry)


def test_spread_bps_soma_linear_com_fee_e_slippage() -> None:
    cm = CostModel(
        taker_fee_bps=5.0,
        slippage_bps_per_unit_notional=10.0,
        spread_bps=3.0,
    )
    out = apply_cost(
        price_market=100.0,
        notional=1000.0,
        capital_inicial=1000.0,
        side=Side.LONG,
        is_entry=True,
        cost_model=cm,
    )
    # total_bps = 5 + 10 * (1000/1000) + 3 = 18 bps
    assert out == pytest.approx(100.0 * (1.0 + 18.0 / 10_000.0))
