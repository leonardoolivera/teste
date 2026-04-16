"""Sizing determinístico do núcleo mínimo (ADR-0004).

Fixed fractional puro: a posição é uma função de
``(capital_corrente, fracao_por_trade, alavancagem_max, preco_entrada)``.
Nenhum estado. Nenhuma aleatoriedade. Nenhum I/O.

A validação do resultado (rejeição determinística por zero/NaN/inf/acima do cap)
é responsabilidade do engine; esta função apenas devolve o valor calculado.
"""

from __future__ import annotations

from alpha_forge.risk.schemas import RiskBudget


def fixed_fractional_position_sizing(
    budget: RiskBudget, preco_entrada: float, capital_corrente: float
) -> float:
    """Tamanho da posição em unidades do ativo.

    Fórmula: ``(capital_corrente * fracao_por_trade * alavancagem_max) / preco_entrada``.

    Retorna 0.0, NaN ou ±inf em vez de levantar exceção quando os inputs são
    patológicos (preço zero, capital zero). O engine decide rejeitar.
    """
    notional = capital_corrente * budget.fracao_por_trade * budget.alavancagem_max
    if preco_entrada == 0.0:
        return float("inf") if notional > 0 else 0.0
    return notional / preco_entrada
