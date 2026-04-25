"""Tests for exports.schema (ADR-0031)."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from alpha_forge.exports.schema import (
    ManifestValidationError,
    validate_manifest,
    validate_manifest_file,
)


def _minimal_valid_v3() -> dict:
    return {
        "manifest_version": "v3",
        "strategy_name": "bollinger_width_regime",
        "alpha_forge_commit": "a" * 40,
        "approved_at": "2026-04-18T00:00:00Z",
        "approval_adr": "decisions/0028-bollinger-width-regime-deploy-approval.md",
        "engine": {
            "family": "bollinger",
            "params": {"window": 30, "num_std": 1.5, "long_only": True},
        },
        "approved_combos": [
            {
                "symbol": "ETHUSDT",
                "timeframe": "1h",
                "validation_window": "2024-01-05..2024-07-04",
                "window_tag": "2024-H1",
                "oos_trades": 38,
                "oos_sharpe": 1.834,
                "oos_mdd_pct": 1.823,
                "oos_pnl_pct": 4.678,
            }
        ],
        "validation": {
            "method": "walk-forward-4fold",
            "cost_model_baseline_pct": 0.20,
            "cost_model_stress_fee_plus_10_pct": 0.40,
            "cost_stress_ratio_min": 0.95,
            "seed_monte_carlo": 42,
        },
        "execution_hints": {
            "position_sizing": "fixed_notional_per_trade",
            "notional_per_trade_quote_ccy": 2000,
            "entry_rule": "close[t-1] cruza abaixo",
            "exit_rule": "close[t-1] cruza acima de ma",
            "regime_gate": "bw_bps >= 250",
            "causal_invariant": "engine ignora iloc[-1]",
            "signal_arbitration": "EXIT vence ENTER",
        },
        "runtime_contract": "faithful",
        "runtime_invariants": {
            "entry_fill": "market_at_open_next_bar",
            "exit_fill": "market_at_open_next_bar",
            "sizing": "fixed_notional_literal",
            "stop_loss": "disabled",
            "signal_arbitration": "exit_wins_on_tie",
        },
        "expansion_policy": {
            "rule": "Novo combo requer nova ADR.",
            "excluded_combos": [],
        },
    }


def test_minimal_v3_passes():
    manifest = validate_manifest(_minimal_valid_v3())
    assert manifest.manifest_version == "v3"
    assert len(manifest.approved_combos) == 1


def test_v1_legacy_rejected():
    p = _minimal_valid_v3()
    p["manifest_version"] = "v1"
    with pytest.raises(ManifestValidationError, match="legacy"):
        validate_manifest(p)


def test_v2_legacy_rejected():
    p = _minimal_valid_v3()
    p["manifest_version"] = "v2"
    with pytest.raises(ManifestValidationError, match="legacy"):
        validate_manifest(p)


def test_missing_version_rejected():
    p = _minimal_valid_v3()
    del p["manifest_version"]
    with pytest.raises(ManifestValidationError, match="missing or malformed"):
        validate_manifest(p)


def test_unknown_top_level_field_rejected():
    p = _minimal_valid_v3()
    p["unexpected"] = "nope"
    with pytest.raises(ManifestValidationError):
        validate_manifest(p)


def test_runtime_contract_must_be_faithful():
    p = _minimal_valid_v3()
    p["runtime_contract"] = "trailing_stop"
    with pytest.raises(ManifestValidationError):
        validate_manifest(p)


def test_runtime_invariants_values_are_fixed():
    p = _minimal_valid_v3()
    p["runtime_invariants"]["stop_loss"] = "enabled"
    with pytest.raises(ManifestValidationError):
        validate_manifest(p)


def test_oos_trades_below_30_rejected():
    p = _minimal_valid_v3()
    p["approved_combos"][0]["oos_trades"] = 29
    with pytest.raises(ManifestValidationError):
        validate_manifest(p)


def test_oos_sharpe_below_one_rejected():
    p = _minimal_valid_v3()
    p["approved_combos"][0]["oos_sharpe"] = 0.99
    with pytest.raises(ManifestValidationError):
        validate_manifest(p)


def test_oos_mdd_above_20_rejected():
    p = _minimal_valid_v3()
    p["approved_combos"][0]["oos_mdd_pct"] = 20.01
    with pytest.raises(ManifestValidationError):
        validate_manifest(p)


def test_oos_pnl_non_positive_rejected():
    p = _minimal_valid_v3()
    p["approved_combos"][0]["oos_pnl_pct"] = 0.0
    with pytest.raises(ManifestValidationError):
        validate_manifest(p)


def test_cost_stress_ratio_below_095_rejected():
    p = _minimal_valid_v3()
    p["validation"]["cost_stress_ratio_min"] = 0.94
    with pytest.raises(ManifestValidationError):
        validate_manifest(p)


def test_disallow_sizing_modes_enum_enforced():
    p = _minimal_valid_v3()
    p["disallow_sizing_modes"] = ["snowball", "custom_mode"]
    with pytest.raises(ManifestValidationError):
        validate_manifest(p)


def test_disallow_sizing_modes_all_valid():
    p = _minimal_valid_v3()
    p["disallow_sizing_modes"] = ["snowball", "kelly_like", "martingale"]
    validate_manifest(p)


def test_invalid_sha_rejected():
    p = _minimal_valid_v3()
    p["alpha_forge_commit"] = "xyz"
    with pytest.raises(ManifestValidationError):
        validate_manifest(p)


def test_invalid_adr_path_rejected():
    p = _minimal_valid_v3()
    p["approval_adr"] = "some/random/path.md"
    with pytest.raises(ManifestValidationError):
        validate_manifest(p)


def test_position_sizing_must_be_fixed_notional():
    p = _minimal_valid_v3()
    p["execution_hints"]["position_sizing"] = "risk_based"
    with pytest.raises(ManifestValidationError):
        validate_manifest(p)


def test_validate_manifest_file_roundtrip(tmp_path: Path):
    p = _minimal_valid_v3()
    f = tmp_path / "manifest.json"
    f.write_text(json.dumps(p), encoding="utf-8")
    manifest = validate_manifest_file(f)
    assert manifest.strategy_name == "bollinger_width_regime"


def test_schema_json_exists_and_parses():
    """Canonical JSON Schema file must exist and be valid JSON (ADR-0031)."""
    schema_path = (
        Path(__file__).parent.parent.parent
        / "exports"
        / "approved"
        / "manifest.schema.json"
    )
    assert schema_path.exists(), f"Missing canonical schema at {schema_path}"
    with schema_path.open("r", encoding="utf-8") as fh:
        schema = json.load(fh)
    assert schema["$schema"].startswith("https://json-schema.org/draft/")
    assert "manifest_version" in schema["required"]
    assert "runtime_contract" in schema["required"]
    assert "runtime_invariants" in schema["required"]


def test_deepcopy_of_minimal_does_not_affect_original():
    """Sanity: helper stays pure across repeated calls."""
    a = _minimal_valid_v3()
    b = _minimal_valid_v3()
    a["strategy_name"] = "mutated"
    assert b["strategy_name"] == "bollinger_width_regime"
    # copy roundtrip
    c = copy.deepcopy(b)
    assert c == b


# ---------- ADR-0066: tracking fields + short-side entry rules ----------


def _approved_manifests_on_disk() -> list[Path]:
    root = Path(__file__).parent.parent.parent / "exports" / "approved"
    return [
        p
        for p in sorted(root.glob("*.json"))
        if p.name != "manifest.schema.json"
        and not p.name.startswith(("v1_", "v2_", "bollinger_width_regime_20260418_v2", "eth_2025h1"))
    ]


@pytest.mark.parametrize("manifest_path", _approved_manifests_on_disk(), ids=lambda p: p.name)
def test_real_v3_plus_manifests_validate(manifest_path: Path):
    """ADR-0066: every v3+ manifest on disk must validate against the relaxed schema."""
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not payload.get("manifest_version", "").startswith(("v3", "v4", "v5", "v6", "v7", "v8", "v9")):
        pytest.skip(f"{manifest_path.name} is legacy (v1/v2)")
    validate_manifest(payload)  # raises on failure


def test_tracking_fields_accepted_on_approved_combo():
    m = _minimal_valid_v3()
    m["approved_combos"][0].update({
        "regime": "chop",
        "cost_stress_ratio_min": 0.97,
        "mc_p5_final_equity": 9900,
        "source_tag": "XX.1",
        "source_run_id": "xx-run-id",
        "note": "tracking only",
    })
    validate_manifest(m)


def test_top_level_tracking_fields_accepted():
    m = _minimal_valid_v3()
    m.update({
        "complementary_to": "other_manifest.json",
        "live_status": "active",
        "live_status_since": "2026-04-19T00:00:00Z",
        "audit_adr": "decisions/0059-audit.md",
        "audit_closeout_adr": "decisions/0060-closeout.md",
        "series_source": {"series_tag": "XX"},
    })
    validate_manifest(m)


def test_live_status_enum_enforced():
    m = _minimal_valid_v3()
    m["live_status"] = "not_a_valid_state"
    with pytest.raises(ManifestValidationError):
        validate_manifest(m)


def test_short_side_entry_rules_accepted():
    m = _minimal_valid_v3()
    m["execution_hints"].pop("entry_rule")
    m["execution_hints"]["entry_rule_long"] = "close cruza abaixo"
    m["execution_hints"]["entry_rule_short"] = "close cruza acima"
    validate_manifest(m)


def test_both_singular_and_dual_entry_rules_rejected():
    m = _minimal_valid_v3()
    m["execution_hints"]["entry_rule_long"] = "x"
    m["execution_hints"]["entry_rule_short"] = "y"
    with pytest.raises(ManifestValidationError):
        validate_manifest(m)


def test_missing_all_entry_rules_rejected():
    m = _minimal_valid_v3()
    m["execution_hints"].pop("entry_rule")
    with pytest.raises(ManifestValidationError):
        validate_manifest(m)


def test_short_side_only_without_long_rejected():
    m = _minimal_valid_v3()
    m["execution_hints"].pop("entry_rule")
    m["execution_hints"]["entry_rule_short"] = "only short"
    with pytest.raises(ManifestValidationError):
        validate_manifest(m)


def test_runtime_invariants_still_strict_after_addendum():
    """ADR-0066 relaxes doc fields but MUST preserve runtime_invariants strict."""
    m = _minimal_valid_v3()
    m["runtime_invariants"]["sizing"] = "snowball"
    with pytest.raises(ManifestValidationError):
        validate_manifest(m)


def test_extra_unknown_field_on_combo_still_rejected():
    """Relaxation is enumerated — random extras still fail."""
    m = _minimal_valid_v3()
    m["approved_combos"][0]["random_extra"] = "nope"
    with pytest.raises(ManifestValidationError):
        validate_manifest(m)
