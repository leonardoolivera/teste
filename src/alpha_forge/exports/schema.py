"""Manifest validator for `exports/approved/*.json` (v3+). ADR-0031.

The canonical schema is `exports/approved/manifest.schema.json` (JSON Schema
Draft 2020-12). This module provides an equivalent validator in Python using
pydantic, so export tooling can validate without adding `jsonschema` as a
runtime dependency. The two sources must stay in sync; `test_manifest_schema.py`
asserts that.

v1/v2 manifests are legacy and explicitly out of scope (see ADR-0031).
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, ValidationError, model_validator


class ManifestValidationError(ValueError):
    """Raised when a manifest fails v3 schema validation."""


_SHA40 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{40}$")]
_MANIFEST_VERSION = Annotated[str, StringConstraints(pattern=r"^v(3|[4-9]|[1-9][0-9]+)(\.[0-9]+)*$")]
_ADR_PATH = Annotated[str, StringConstraints(pattern=r"^decisions/\d{4}-.+\.md$")]
_SYMBOL = Annotated[str, StringConstraints(pattern=r"^[A-Z]{2,10}USDT$")]
_TIMEFRAME = Annotated[str, StringConstraints(pattern=r"^(1m|5m|10m|15m|30m|1h|4h|1d)$")]
_WINDOW = Annotated[str, StringConstraints(pattern=r"^\d{4}-\d{2}-\d{2}\.\.\d{4}-\d{2}-\d{2}$")]
_WINDOW_TAG = Annotated[str, StringConstraints(pattern=r"^\d{4}-H[12]$")]
_VERSION_TAG = Annotated[str, StringConstraints(pattern=r"^v\d+$")]


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ApprovedCombo(_StrictModel):
    symbol: _SYMBOL
    timeframe: _TIMEFRAME
    validation_window: _WINDOW
    window_tag: _WINDOW_TAG
    oos_trades: int = Field(ge=30)
    oos_sharpe: float = Field(ge=1.0)
    oos_mdd_pct: float = Field(ge=0, le=20)
    oos_pnl_pct: float = Field(gt=0)
    approved_in: _VERSION_TAG | None = None
    # ADR-0066: tracking/doc fields (optional).
    regime: str | None = None
    cost_stress_ratio_min: float | None = Field(default=None, ge=0.0, le=1.0)
    mc_p5_final_equity: float | None = None
    source_tag: str | None = None
    source_run_id: str | None = None
    note: str | None = None


class ExcludedCombo(_StrictModel):
    symbol: _SYMBOL
    timeframe: _TIMEFRAME
    window_tag: _WINDOW_TAG
    reason: str = Field(min_length=1)
    source_tag: str | None = None  # ADR-0066


class ExpansionPolicy(_StrictModel):
    rule: str = Field(min_length=1)
    excluded_combos: list[ExcludedCombo]
    regime_dependence_note: str | None = None  # ADR-0066


class Engine(_StrictModel):
    family: str = Field(min_length=1)
    params: dict[str, Any]


class ValidationBlock(BaseModel):
    model_config = ConfigDict(extra="allow")

    method: str = Field(min_length=1)
    cost_model_baseline_pct: float = Field(gt=0)
    cost_model_stress_fee_plus_10_pct: float = Field(gt=0)
    cost_stress_ratio_min: float = Field(ge=0.95)
    seed_monte_carlo: int


class ExecutionHints(_StrictModel):
    """ADR-0066: accept either legacy `entry_rule` singular OR
    `entry_rule_long` + `entry_rule_short` (post ADR-0051 short-side).
    Exactly one form must be present; short-side form requires both sides."""

    position_sizing: Literal["fixed_notional_per_trade"]
    notional_per_trade_quote_ccy: float = Field(gt=0)
    entry_rule: str | None = Field(default=None, min_length=1)
    entry_rule_long: str | None = Field(default=None, min_length=1)
    entry_rule_short: str | None = Field(default=None, min_length=1)
    exit_rule: str = Field(min_length=1)
    regime_gate: str = Field(min_length=1)
    causal_invariant: str = Field(min_length=1)
    signal_arbitration: str = Field(min_length=1)
    reverse_on_signal: str | None = None

    @model_validator(mode="after")
    def _check_entry_rule_form(self) -> "ExecutionHints":
        has_singular = self.entry_rule is not None
        has_long = self.entry_rule_long is not None
        has_short = self.entry_rule_short is not None
        if has_singular and (has_long or has_short):
            raise ValueError(
                "execution_hints: use either `entry_rule` (singular) "
                "or `entry_rule_long`+`entry_rule_short`, not both."
            )
        if not has_singular and not (has_long and has_short):
            raise ValueError(
                "execution_hints: missing entry rule. "
                "Provide `entry_rule` (singular) or both `entry_rule_long` and `entry_rule_short`."
            )
        return self


class RuntimeInvariants(_StrictModel):
    entry_fill: Literal["market_at_open_next_bar"]
    exit_fill: Literal["market_at_open_next_bar"]
    sizing: Literal["fixed_notional_literal"]
    stop_loss: Literal["disabled"]
    signal_arbitration: Literal["exit_wins_on_tie"]


_DISALLOWED_SIZING = Literal["snowball", "kelly_like", "martingale"]


class ManifestV3(_StrictModel):
    manifest_version: _MANIFEST_VERSION
    strategy_name: str = Field(min_length=1)
    alpha_forge_commit: _SHA40
    approved_at: datetime
    approval_adr: _ADR_PATH
    prior_approval_adr: _ADR_PATH | None = None
    supersedes: str | None = None
    engine: Engine
    approved_combos: list[ApprovedCombo] = Field(min_length=1)
    validation: ValidationBlock
    execution_hints: ExecutionHints
    runtime_contract: Literal["faithful"]
    runtime_invariants: RuntimeInvariants
    disallow_sizing_modes: list[_DISALLOWED_SIZING] | None = None
    disallow_sizing_reason: str | None = None
    expansion_policy: ExpansionPolicy
    # ADR-0066: tracking fields (optional).
    complementary_to: str | None = None
    live_status: Literal["pending_audit", "active", "deprecated"] | None = None
    live_status_since: datetime | None = None
    audit_adr: _ADR_PATH | None = None
    audit_closeout_adr: _ADR_PATH | None = None
    series_source: dict[str, Any] | None = None


def validate_manifest(payload: dict[str, Any]) -> ManifestV3:
    version = payload.get("manifest_version")
    if not isinstance(version, str) or not re.match(r"^v\d+", version):
        raise ManifestValidationError(
            f"missing or malformed manifest_version: {version!r}. "
            f"v3+ required; v1/v2 manifests are legacy and not validated."
        )
    if version.startswith(("v1", "v2")):
        raise ManifestValidationError(
            f"manifest_version={version!r} is legacy; schema only validates v3+."
        )
    try:
        return ManifestV3.model_validate(payload)
    except ValidationError as exc:
        raise ManifestValidationError(str(exc)) from exc


def validate_manifest_file(path: str | Path) -> ManifestV3:
    p = Path(path)
    with p.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)
    return validate_manifest(payload)
