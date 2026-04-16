"""Contratos de dados do módulo `data`.

Estrutura mínima exigida por ADR-0005. Pydantic v2.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class OHLCVBar(BaseModel):
    """Uma barra OHLCV. Usada como contrato lógico; em runtime trabalhamos com DataFrame."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    timestamp: datetime
    open: float = Field(gt=0)
    high: float = Field(gt=0)
    low: float = Field(gt=0)
    close: float = Field(gt=0)
    volume: float = Field(ge=0)

    @model_validator(mode="after")
    def _check_hlc_consistency(self) -> OHLCVBar:
        if self.high < max(self.open, self.close):
            raise ValueError("high < max(open, close)")
        if self.low > min(self.open, self.close):
            raise ValueError("low > min(open, close)")
        if self.high < self.low:
            raise ValueError("high < low")
        return self


class GapRecord(BaseModel):
    """Intervalo ausente declarado no manifesto.

    Ambos os timestamps inclusivos. Intervalos declarados são aceitos pelo loader;
    intervalos não declarados derrubam o carregamento.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    start: datetime
    end: datetime
    reason: str = ""

    @model_validator(mode="after")
    def _check_order(self) -> GapRecord:
        if self.end < self.start:
            raise ValueError("gap.end < gap.start")
        return self


class DatasetManifest(BaseModel):
    """Entrada única de `data/datasets.yaml` (ADR-0005)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    dataset_id: str = Field(min_length=1)
    symbol: str = Field(min_length=1)
    timeframe: str = Field(min_length=1)
    path: str = Field(min_length=1)
    sha256: str = Field(min_length=64, max_length=64)
    row_count: int = Field(gt=0)
    start_ts: datetime
    end_ts: datetime
    timezone: str = Field(min_length=1)
    declared_gaps: list[GapRecord] = Field(default_factory=list)
    source: str = Field(min_length=1)

    @model_validator(mode="after")
    def _check_window(self) -> DatasetManifest:
        if self.end_ts < self.start_ts:
            raise ValueError("end_ts < start_ts")
        return self
