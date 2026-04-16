"""Contratos de I/O do backtest do núcleo mínimo.

Mantidos pequenos e frozen. Eventos cobrem o suficiente para auditar
causalidade e rejeições de sizing.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Side(StrEnum):
    LONG = "long"
    SHORT = "short"
    FLAT = "flat"


class Signal(StrEnum):
    """Contrato mínimo de sinais emitidos pela estratégia (ADR-0002)."""

    ENTER_LONG = "enter_long"
    ENTER_SHORT = "enter_short"
    EXIT = "exit"
    HOLD = "hold"


class Fill(BaseModel):
    """Execução efetiva de uma ordem em `t+1 open`."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    timestamp: datetime
    signal_timestamp: datetime
    side: Side
    price: float
    size: float
    notional: float


class RejectionReason(StrEnum):
    SIZE_ZERO = "size_zero"
    SIZE_NEGATIVE = "size_negative"
    SIZE_NAN = "size_nan"
    SIZE_INF = "size_inf"
    ABOVE_LEVERAGE_CAP = "above_leverage_cap"


class Rejection(BaseModel):
    """Ordem rejeitada por sizing inválido (ADR-0004)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    timestamp: datetime
    signal_timestamp: datetime
    reason: RejectionReason
    raw_size: float
    price: float


class Trade(BaseModel):
    """Trade fechado = par (entrada, saída). Usado pelas métricas (ADR-0007).

    Entrada sem saída correspondente até o fim do backtest **não** vira `Trade`.
    PnL calculado com preços efetivos (pós-custo) para manter consistência com
    o `final_equity`.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    side: Side
    entry_timestamp: datetime
    exit_timestamp: datetime
    entry_price: float
    exit_price: float
    size: float
    pnl: float


class BacktestMetrics(BaseModel):
    """Métricas mínimas do núcleo (ADR-0007).

    - `total_pnl`: `final_equity - capital_inicial` (absoluto).
    - `trade_count`: trades fechados; entrada sem saída **não** conta.
    - `hit_rate`: fração de trades fechados com PnL > 0. `None` quando não há
      trades. Nunca `0.0` nem `NaN`.
    - `max_drawdown`: fração ∈ [0, 1]; 0 se equity nunca cair.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    total_pnl: float
    trade_count: int = Field(ge=0)
    hit_rate: float | None = Field(default=None, ge=0.0, le=1.0)
    max_drawdown: float = Field(ge=0.0, le=1.0)


class BacktestResult(BaseModel):
    """Saída do engine. Mantida flat para facilitar inspeção."""

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    dataset_id: str
    bars: int = Field(ge=0)
    fills: list[Fill]
    rejections: list[Rejection]
    trades: list[Trade] = Field(default_factory=list)
    final_equity: float
    max_equity: float
    min_equity: float
    equity_curve: list[tuple[datetime, float]]
    metrics: BacktestMetrics | None = None
