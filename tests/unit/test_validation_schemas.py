"""Validação estrutural dos schemas de `validation/` (ADR-0003).

Schemas são frozen + extra=forbid; validators em campos numéricos precisam
rejeitar valores inválidos na construção.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError as PydanticValidationError

from alpha_forge.validation.schemas import (
    MonteCarloSummary,
    WalkForwardWindow,
)


def _utc(y: int, m: int, d: int) -> datetime:
    return datetime(y, m, d, tzinfo=timezone.utc)


class TestWalkForwardWindow:
    def test_constroi_com_campos_validos(self) -> None:
        w = WalkForwardWindow(start=_utc(2025, 1, 1), end=_utc(2025, 2, 1), bars=30)
        assert w.bars == 30

    def test_rejeita_bars_negativo(self) -> None:
        with pytest.raises(PydanticValidationError):
            WalkForwardWindow(start=_utc(2025, 1, 1), end=_utc(2025, 2, 1), bars=-1)

    def test_frozen(self) -> None:
        w = WalkForwardWindow(start=_utc(2025, 1, 1), end=_utc(2025, 2, 1), bars=30)
        with pytest.raises(PydanticValidationError):
            w.bars = 99  # type: ignore[misc]

    def test_extra_forbid(self) -> None:
        with pytest.raises(PydanticValidationError):
            WalkForwardWindow(
                start=_utc(2025, 1, 1),
                end=_utc(2025, 2, 1),
                bars=30,
                extra_field="x",  # type: ignore[call-arg]
            )


class TestMonteCarloSummary:
    def _base_kwargs(self) -> dict[str, object]:
        return {
            "n_resamples": 1000,
            "seed": 42,
            "final_equity_percentiles": {5: 9500.0, 25: 9800.0, 50: 10000.0, 75: 10200.0, 95: 10500.0},
            "max_drawdown_percentiles": {5: 0.01, 25: 0.02, 50: 0.05, 75: 0.08, 95: 0.12},
            "original_final_equity": 10050.0,
            "original_max_drawdown": 0.04,
        }

    def test_constroi_com_campos_validos(self) -> None:
        s = MonteCarloSummary(**self._base_kwargs())  # type: ignore[arg-type]
        assert s.n_resamples == 1000
        assert s.seed == 42

    def test_rejeita_n_resamples_abaixo_do_minimo(self) -> None:
        kwargs = self._base_kwargs()
        kwargs["n_resamples"] = 50
        with pytest.raises(PydanticValidationError):
            MonteCarloSummary(**kwargs)  # type: ignore[arg-type]

    def test_frozen(self) -> None:
        s = MonteCarloSummary(**self._base_kwargs())  # type: ignore[arg-type]
        with pytest.raises(PydanticValidationError):
            s.seed = 99  # type: ignore[misc]

    def test_extra_forbid(self) -> None:
        kwargs = self._base_kwargs()
        kwargs["extra"] = 1
        with pytest.raises(PydanticValidationError):
            MonteCarloSummary(**kwargs)  # type: ignore[arg-type]
