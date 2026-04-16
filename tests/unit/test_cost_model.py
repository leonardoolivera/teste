"""Testes unitários do modelo mínimo de custos (ADR-0006)."""

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
