"""Testes unitários de `risk` — schema e sizing puro (ADR-0004)."""

from __future__ import annotations

import math

import pytest
from pydantic import ValidationError

from alpha_forge.risk.schemas import RiskBudget
from alpha_forge.risk.sizing import fixed_fractional_position_sizing


def test_budget_aceita_faixa_valida() -> None:
    budget = RiskBudget(capital_inicial=1000.0, fracao_por_trade=0.1, alavancagem_max=1.0)
    assert budget.alavancagem_max == 1.0


def test_budget_aceita_alavancagem_10() -> None:
    budget = RiskBudget(capital_inicial=1000.0, fracao_por_trade=0.1, alavancagem_max=10.0)
    assert budget.alavancagem_max == 10.0


def test_budget_rejeita_alavancagem_acima_do_cap() -> None:
    with pytest.raises(ValidationError):
        RiskBudget(capital_inicial=1000.0, fracao_por_trade=0.1, alavancagem_max=10.1)


def test_budget_rejeita_alavancagem_abaixo_do_piso() -> None:
    with pytest.raises(ValidationError):
        RiskBudget(capital_inicial=1000.0, fracao_por_trade=0.1, alavancagem_max=0.5)


def test_budget_rejeita_fracao_zero_ou_negativa() -> None:
    with pytest.raises(ValidationError):
        RiskBudget(capital_inicial=1000.0, fracao_por_trade=0.0, alavancagem_max=1.0)
    with pytest.raises(ValidationError):
        RiskBudget(capital_inicial=1000.0, fracao_por_trade=-0.1, alavancagem_max=1.0)


def test_budget_rejeita_fracao_maior_que_um() -> None:
    with pytest.raises(ValidationError):
        RiskBudget(capital_inicial=1000.0, fracao_por_trade=1.1, alavancagem_max=1.0)


def test_budget_rejeita_capital_zero() -> None:
    with pytest.raises(ValidationError):
        RiskBudget(capital_inicial=0.0, fracao_por_trade=0.1, alavancagem_max=1.0)


def test_sizing_sem_alavancagem() -> None:
    budget = RiskBudget(capital_inicial=1000.0, fracao_por_trade=0.1, alavancagem_max=1.0)
    size = fixed_fractional_position_sizing(budget, preco_entrada=100.0, capital_corrente=1000.0)
    assert size == pytest.approx(1.0)


def test_sizing_com_alavancagem_10() -> None:
    budget = RiskBudget(capital_inicial=1000.0, fracao_por_trade=0.1, alavancagem_max=10.0)
    size = fixed_fractional_position_sizing(budget, preco_entrada=100.0, capital_corrente=1000.0)
    assert size == pytest.approx(10.0)


def test_sizing_com_preco_zero_devolve_inf() -> None:
    budget = RiskBudget(capital_inicial=1000.0, fracao_por_trade=0.1, alavancagem_max=1.0)
    size = fixed_fractional_position_sizing(budget, preco_entrada=0.0, capital_corrente=1000.0)
    assert math.isinf(size)


def test_sizing_e_funcao_pura() -> None:
    budget = RiskBudget(capital_inicial=1000.0, fracao_por_trade=0.1, alavancagem_max=2.0)
    a = fixed_fractional_position_sizing(budget, preco_entrada=50.0, capital_corrente=500.0)
    b = fixed_fractional_position_sizing(budget, preco_entrada=50.0, capital_corrente=500.0)
    assert a == b
