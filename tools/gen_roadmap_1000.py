"""Gerador de roadmap 1000 estratégias (ADR pendente).

Organiza em 4 tiers + subcategorias. Cada entry:
  id, tier, engine, direction, timeframe, asset, window, regime_filter, params, prior, rationale.

Output: decisions/roadmap_1000.md (tabelado) + exports/diag/roadmap_1000.json (machine-readable).

Dimensões usadas:
  engines:     ma_crossover, donchian, bollinger, rsi, keltner, zscore, composite_bb_rsi, supertrend
  directions:  long, short, bi (alguns engines são sempre bi)
  timeframes:  5m, 10m, 15m, 30m, 1h, 4h
  assets:      BTC, ETH, SOL (com LINK/DOT/AVAX como expansão tier 4)
  windows:     2024-H2, 2025-H1, 2025-H2
  filters:     none, width_basic, width_tight, trend_htf_long, trend_htf_short, AND(width,trend_htf)
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_MD = ROOT / "decisions" / "roadmap_1000.md"
OUT_JSON = ROOT / "exports" / "diag" / "roadmap_1000.json"


ASSETS = ["BTC", "ETH", "SOL"]
WINDOWS = ["2024-H2", "2025-H1", "2025-H2"]


# =====================================================================
# TIER 1 (250 entries) — high EV: extensões diretas de achados positivos
# =====================================================================

def tier1_regime_detection_meta() -> list[dict]:
    """50: meta-strategy com regime gating.

    Usa detector de regime (ATR expansion, HTF trend, realized vol) para
    alocar entre MR 1h (sweet spot) e trend-following long-only 10m
    (bear-avoidance). Testa em 3 assets × 3 windows × variações gate.
    """
    out = []
    gates = [
        "atr_expansion_50pct",
        "trend_htf_4h_sma50_flat",
        "realized_vol_percentile_70",
        "width_narrow_10m",
        "funding_rate_extreme",  # if data available
    ]
    for asset, window, gate in itertools.product(ASSETS, WINDOWS, gates):
        out.append({
            "id": f"T1-RM-{asset}-{window}-{gate}",
            "tier": 1, "engine": "regime_meta",
            "direction": "adaptive", "timeframe": "mix",
            "asset": asset, "window": window,
            "regime_filter": gate,
            "params": "stack_13_gated_by_regime",
            "prior": 0.25,
            "rationale": "regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-friendly, H1 2025 bear-friendly trend)",
        })
    return out


def tier1_padrao50_cross_era() -> list[dict]:
    """60: Padrão 50 (ma_crossover/supertrend bear-avoidance) cross-era extenso.

    TF10I.5 ETH 2025-H1 passou Sh=1.61 alfa=+30%. Validar cross-era em:
    - Mais bear windows históricos (se data disponível)
    - Params MA (15/45, 20/50, 25/75, 30/90, 50/200) × 2 assets (ETH/SOL) × 3 windows
    """
    ma_params = [(10, 30), (15, 45), (20, 50), (25, 75), (30, 90), (50, 200)]
    for (s, l), asset, window in itertools.product(ma_params, ["ETH", "SOL"], WINDOWS):
        out = {
            "id": f"T1-MA-{s}-{l}-{asset}-{window}",
            "tier": 1, "engine": "ma_crossover",
            "direction": "long", "timeframe": "10m",
            "asset": asset, "window": window,
            "regime_filter": "none",
            "params": f"short={s},long={l}",
            "prior": 0.18,
            "rationale": "Padrão 50 cross-era: MA crossover long bear-avoidance",
        }
        yield_list.append(out)
    return yield_list


yield_list: list[dict] = []


def tier1_padrao50_extended() -> list[dict]:
    """60 — MA crossover param grid cross-asset cross-window 10m."""
    out = []
    ma_params = [(10, 30), (15, 45), (20, 50), (25, 75), (30, 90), (50, 200)]
    for (s, l), asset, window in itertools.product(ma_params, ["ETH", "SOL"], WINDOWS):
        out.append({
            "id": f"T1-MA-{s}-{l}-{asset}-{window}",
            "tier": 1, "engine": "ma_crossover",
            "direction": "long", "timeframe": "10m",
            "asset": asset, "window": window,
            "regime_filter": "none",
            "params": f"short={s},long={l}",
            "prior": 0.18,
            "rationale": "Padrão 50 cross-era MA crossover bear-avoidance",
        })
    # supertrend params grid
    st_params = [(7, 2.5), (10, 2.5), (10, 3.0), (14, 3.0), (14, 3.5), (20, 3.5)]
    for (atr_p, atr_m), asset, window in itertools.product(st_params, ["ETH", "SOL"], WINDOWS):
        out.append({
            "id": f"T1-ST-{atr_p}-{atr_m}-{asset}-{window}",
            "tier": 1, "engine": "supertrend",
            "direction": "long", "timeframe": "10m",
            "asset": asset, "window": window,
            "regime_filter": "none",
            "params": f"atr_period={atr_p},atr_mult={atr_m}",
            "prior": 0.18,
            "rationale": "Padrão 50 cross-era supertrend bear-avoidance",
        })
    return out


def tier1_padrao48_sol_regime() -> list[dict]:
    """60 — SOL 2024-H2 regime replication em outros SOL windows + outros alts."""
    # Check if MR engines fire similarly in other SOL windows or on LINK/DOT/AVAX 2024-H2 if data available
    out = []
    engines = [
        ("bollinger", "short", "window=20,num_std=2.0"),
        ("bollinger", "long", "window=30,num_std=1.5"),
        ("rsi", "short", "period=14,os=30,ob=70"),
        ("rsi", "long", "period=14,os=30,ob=70"),
        ("composite_bb_rsi", "short", "bb=20/2,rsi=14/30/70"),
    ]
    # SOL cross-windows (existing data)
    for (eng, dr, p), window in itertools.product(engines, WINDOWS):
        out.append({
            "id": f"T1-48-{eng}-{dr}-SOL-{window}",
            "tier": 1, "engine": eng,
            "direction": dr, "timeframe": "10m",
            "asset": "SOL", "window": window,
            "regime_filter": "none",
            "params": p,
            "prior": 0.22 if window == "2024-H2" else 0.08,
            "rationale": "Padrão 48 SOL regime replication cross-window",
        })
    # SOL longer history window — 2024-H1 if data
    for eng, dr, p in engines:
        out.append({
            "id": f"T1-48-{eng}-{dr}-SOL-2024-H1",
            "tier": 1, "engine": eng,
            "direction": dr, "timeframe": "10m",
            "asset": "SOL", "window": "2024-H1",
            "regime_filter": "none",
            "params": p,
            "prior": 0.15,
            "rationale": "Padrão 48 expansion SOL 2024-H1 (requires data ingest)",
        })
    return out[:60]  # cap


def tier1_portfolio_stack13() -> list[dict]:
    """50 — portfolio equal-weight / risk-parity do stack 13 combos."""
    out = []
    allocation = ["equal_weight", "risk_parity_vol", "sharpe_weighted", "min_var"]
    for alloc, window, corr_window in itertools.product(allocation, WINDOWS, [30, 60, 90]):
        out.append({
            "id": f"T1-PF-{alloc}-{window}-cw{corr_window}",
            "tier": 1, "engine": "portfolio_stack13",
            "direction": "mixed", "timeframe": "1h",
            "asset": "multi", "window": window,
            "regime_filter": "none",
            "params": f"alloc={alloc},corr_window={corr_window}",
            "prior": 0.30,
            "rationale": "portfolio combining 13 validated stack combos",
        })
    # Subsets (BTC-only, ETH-only, SOL-only, long-only, short-only)
    subsets = ["btc_only", "eth_only", "sol_only", "long_only_sub", "short_only_sub", "mr_only", "trend_only"]
    for sub, window, alloc in itertools.product(subsets, WINDOWS, ["equal_weight", "risk_parity_vol"]):
        out.append({
            "id": f"T1-PF-sub-{sub}-{alloc}-{window}",
            "tier": 1, "engine": "portfolio_subset",
            "direction": "mixed", "timeframe": "1h",
            "asset": "multi", "window": window,
            "regime_filter": "none",
            "params": f"subset={sub},alloc={alloc}",
            "prior": 0.25,
            "rationale": "portfolio subset analysis",
        })
    return out[:50]


def tier1_stack_param_sensitivity() -> list[dict]:
    """30 — parameter sensitivity do stack 13 (1h)."""
    out = []
    combos = [
        ("v2_bol_long", "bollinger", "long", "1h"),
        ("v3_rsi_short_width", "rsi", "short", "1h"),
        ("v4_bol_short_width_short", "bollinger", "short", "1h"),
        ("v6_rsi_short_trendhtf_sol", "rsi", "short", "1h"),
    ]
    perturbations = [
        ("win_up", "window *= 1.2"),
        ("win_down", "window *= 0.83"),
        ("ns_up", "num_std += 0.25"),
        ("ns_down", "num_std -= 0.25"),
        ("period_up", "period *= 1.2"),
        ("period_down", "period *= 0.83"),
        ("threshold_tight", "threshold ± 5"),
    ]
    for (cname, eng, dr, tf), pert, asset in itertools.product(combos, perturbations, ASSETS):
        out.append({
            "id": f"T1-PS-{cname}-{pert[0]}-{asset}",
            "tier": 1, "engine": eng,
            "direction": dr, "timeframe": tf,
            "asset": asset, "window": "2024-H2",
            "regime_filter": "stack_canonical",
            "params": pert[1],
            "prior": 0.20,
            "rationale": f"stack {cname} param sensitivity test",
        })
    return out[:30]


# =====================================================================
# TIER 2 (300 entries) — param grid sweeps em engines stack canonical TF
# =====================================================================

def tier2_bollinger_grid_1h() -> list[dict]:
    """90 — BB grid window × num_std × direction × asset × window."""
    out = []
    windows = [15, 20, 25, 30, 40, 50]
    stds = [1.5, 1.75, 2.0, 2.25, 2.5]
    for w, s, dr, asset, win in itertools.product(windows, stds, ["long", "short"], ASSETS, WINDOWS):
        out.append({
            "id": f"T2-BB-{w}-{s}-{dr}-{asset}-{win}",
            "tier": 2, "engine": "bollinger",
            "direction": dr, "timeframe": "1h",
            "asset": asset, "window": win,
            "regime_filter": "width_basic",
            "params": f"window={w},num_std={s}",
            "prior": 0.10,
            "rationale": "BB grid 1h canonical TF",
        })
    return out[:90]


def tier2_rsi_grid_1h() -> list[dict]:
    """90 — RSI grid period × thresholds × direction × asset × window."""
    out = []
    periods = [7, 10, 14, 21]
    thresholds = [(20, 80), (25, 75), (30, 70), (35, 65)]
    for p, (os, ob), dr, asset, win in itertools.product(periods, thresholds, ["long", "short"], ASSETS, WINDOWS):
        out.append({
            "id": f"T2-RSI-{p}-{os}-{ob}-{dr}-{asset}-{win}",
            "tier": 2, "engine": "rsi",
            "direction": dr, "timeframe": "1h",
            "asset": asset, "window": win,
            "regime_filter": "width_basic",
            "params": f"period={p},os={os},ob={ob}",
            "prior": 0.10,
            "rationale": "RSI grid 1h canonical TF",
        })
    return out[:90]


def tier2_filter_combinations() -> list[dict]:
    """60 — regime filter combinations em BB/RSI 1h."""
    out = []
    filters = [
        "width:min=100",
        "width:min=150",
        "width:min=250",
        "width:min=400",
        "trend_htf:4h:sma=50:long_only",
        "trend_htf:4h:sma=50:short_only",
        "trend_htf:4h:sma=100",
        "AND(width=150,trend_htf_long)",
        "AND(width=250,trend_htf_short)",
        "OR(width=250,trend_htf_long)",
    ]
    engines = [("bollinger", "long"), ("bollinger", "short"), ("rsi", "long"), ("rsi", "short")]
    for f, (eng, dr), asset, win in itertools.product(filters, engines, ASSETS, WINDOWS):
        out.append({
            "id": f"T2-F-{eng}-{dr}-{hash(f)%10000}-{asset}-{win}",
            "tier": 2, "engine": eng,
            "direction": dr, "timeframe": "1h",
            "asset": asset, "window": win,
            "regime_filter": f,
            "params": "canonical",
            "prior": 0.12,
            "rationale": "filter combination sweep",
        })
    return out[:60]


def tier2_composite_mr_sweep() -> list[dict]:
    """60 — composite BB+RSI param grid 1h."""
    out = []
    bb_windows = [15, 20, 25]
    bb_stds = [1.5, 2.0, 2.5]
    rsi_thresh = [(25, 75), (30, 70), (35, 65)]
    for bw, bs, (ro, rb), asset, win in itertools.product(bb_windows, bb_stds, rsi_thresh, ASSETS, WINDOWS):
        out.append({
            "id": f"T2-COMP-{bw}-{bs}-{ro}-{rb}-{asset}-{win}",
            "tier": 2, "engine": "composite_bb_rsi",
            "direction": "short", "timeframe": "1h",
            "asset": asset, "window": win,
            "regime_filter": "none",
            "params": f"bb_w={bw},bb_ns={bs},rsi_os={ro},rsi_ob={rb}",
            "prior": 0.10,
            "rationale": "composite MR 1h param grid",
        })
    return out[:60]


# =====================================================================
# TIER 3 (300 entries) — cobertura sistemática gaps
# =====================================================================

def tier3_tf_coverage() -> list[dict]:
    """100 — TF coverage: 5m, 15m, 30m, 4h em engines non-MR (gap)."""
    out = []
    engines = [("ma_crossover", "long"), ("supertrend", "bi"), ("donchian", "long")]
    tfs = ["5m", "15m", "30m", "4h"]
    for (eng, dr), tf, asset, win in itertools.product(engines, tfs, ASSETS, WINDOWS):
        out.append({
            "id": f"T3-TF-{eng}-{tf}-{asset}-{win}",
            "tier": 3, "engine": eng,
            "direction": dr, "timeframe": tf,
            "asset": asset, "window": win,
            "regime_filter": "none",
            "params": "canonical",
            "prior": 0.05,
            "rationale": f"gap coverage non-MR {tf}",
        })
    return out[:100]


def tier3_short_variants() -> list[dict]:
    """80 — short-only variants de engines normalmente long (ma_crossover, donchian)."""
    out = []
    engines = [("ma_crossover", "short"), ("donchian", "short")]
    tfs = ["10m", "30m", "1h", "4h"]
    for (eng, dr), tf, asset, win in itertools.product(engines, tfs, ASSETS, WINDOWS):
        out.append({
            "id": f"T3-SHORT-{eng}-{tf}-{asset}-{win}",
            "tier": 3, "engine": eng,
            "direction": dr, "timeframe": tf,
            "asset": asset, "window": win,
            "regime_filter": "none",
            "params": "canonical",
            "prior": 0.05,
            "rationale": "short variants de engines long-default",
        })
    return out[:80]


def tier3_keltner_zscore_deep() -> list[dict]:
    """60 — Keltner/zscore param grid 1h (reabertura com params restritivos)."""
    out = []
    # Keltner: atr_mult restritivo
    kparams = [(20, 14, 2.5), (20, 14, 3.0), (30, 14, 2.5), (30, 21, 3.0)]
    for (w, atr_p, mult), asset, win in itertools.product(kparams, ASSETS, WINDOWS):
        out.append({
            "id": f"T3-KELT-{w}-{atr_p}-{mult}-{asset}-{win}",
            "tier": 3, "engine": "keltner",
            "direction": "bi", "timeframe": "1h",
            "asset": asset, "window": win,
            "regime_filter": "none",
            "params": f"window={w},atr_p={atr_p},mult={mult}",
            "prior": 0.08,
            "rationale": "Keltner param reabertura 1h thresholds restritivos",
        })
    # zscore: threshold restritivo
    zparams = [(20, 2.5), (20, 3.0), (30, 2.5), (30, 3.0)]
    for (w, t), asset, win in itertools.product(zparams, ASSETS, WINDOWS):
        out.append({
            "id": f"T3-ZS-{w}-{t}-{asset}-{win}",
            "tier": 3, "engine": "zscore",
            "direction": "bi", "timeframe": "1h",
            "asset": asset, "window": win,
            "regime_filter": "none",
            "params": f"window={w},threshold={t}",
            "prior": 0.08,
            "rationale": "zscore param reabertura 1h thresholds restritivos",
        })
    return out[:60]


def tier3_asset_expansion() -> list[dict]:
    """60 — expandir para LINK/DOT/AVAX (requer ingest) stack top 4 combos."""
    out = []
    new_assets = ["LINK", "DOT", "AVAX"]
    combos = [
        ("v2_bol_long", "bollinger", "long", "1h", "window=30,num_std=1.5"),
        ("v3_rsi_short_width", "rsi", "short", "1h", "period=14,os=30,ob=70"),
        ("v7_rsi_long_width", "rsi", "long", "1h", "period=14,os=30,ob=70"),
        ("v6_rsi_short_trendhtf", "rsi", "short", "1h", "period=14,os=25,ob=75"),
    ]
    for (cn, eng, dr, tf, p), asset, win in itertools.product(combos, new_assets, WINDOWS):
        out.append({
            "id": f"T3-ASSET-{cn}-{asset}-{win}",
            "tier": 3, "engine": eng,
            "direction": dr, "timeframe": tf,
            "asset": asset, "window": win,
            "regime_filter": "stack_canonical",
            "params": p,
            "prior": 0.15,
            "rationale": "asset expansion stack top combos (requires ingest)",
        })
    return out[:60]


# =====================================================================
# TIER 4 (150+ entries) — long tail, exploration, sanity
# =====================================================================

def tier4_stress_adversarial() -> list[dict]:
    """40 — stack 13 combos × adversarial stress scenarios."""
    out = []
    scenarios = [
        "fee+50",
        "fee+100",
        "spread+20",
        "slippage+100",
        "latency+2bar_delay",
        "gap_injection_5pct",
        "fill_drop_10pct",
        "regime_shift_midfold",
    ]
    for sc, i in itertools.product(scenarios, range(5)):
        out.append({
            "id": f"T4-STRESS-{sc}-combo{i+1}",
            "tier": 4, "engine": "stack_combo",
            "direction": "n/a", "timeframe": "1h",
            "asset": "BTC", "window": "2024-H2",
            "regime_filter": "n/a",
            "params": f"stress={sc}",
            "prior": 0.40,  # high prior sobrevive mild stress
            "rationale": "adversarial stress scenarios on stack",
        })
    return out[:40]


def tier4_ablation() -> list[dict]:
    """30 — ablation dos filtros do stack (sem filtro, sem width, sem trend_htf)."""
    out = []
    ablations = ["no_width", "no_trend_htf", "no_filter", "tight_width", "loose_width"]
    for abl, asset, win in itertools.product(ablations, ASSETS, WINDOWS):
        out.append({
            "id": f"T4-ABL-{abl}-{asset}-{win}",
            "tier": 4, "engine": "stack_combo",
            "direction": "n/a", "timeframe": "1h",
            "asset": asset, "window": win,
            "regime_filter": f"ablation_{abl}",
            "params": "canonical",
            "prior": 0.15,
            "rationale": "ablation filter components",
        })
    return out[:30]


def tier4_exotic_signals() -> list[dict]:
    """~140 — exotic/experimental (precisa código novo; marcado com feature flag)."""
    out = []
    exotics = [
        "rsi_divergence",
        "volume_weighted_bb",
        "cvd_signal",
        "funding_rate_fade",
        "open_interest_shift",
        "orderbook_imbalance",
        "bid_ask_spread_shift",
        "session_of_day_bias",
        "day_of_week_bias",
        "liquidation_cascade_fade",
        "vwap_mean_revert",
        "price_action_pinbar",
        "breakout_false_fade",
        "gap_fill_intraday",
        "overnight_holding_bias",
        "round_number_pin",
    ]
    for ex, asset, win in itertools.product(exotics, ASSETS, WINDOWS):
        out.append({
            "id": f"T4-EXO-{ex}-{asset}-{win}",
            "tier": 4, "engine": "exotic_feature_flag",
            "direction": "exploratory", "timeframe": "1h",
            "asset": asset, "window": win,
            "regime_filter": "none",
            "params": f"feature={ex}",
            "prior": 0.05,
            "rationale": f"exotic exploratory: {ex} (requires new code)",
        })
    return out


def tier4_ml_experiments() -> list[dict]:
    """~40 — ML/statistical experiments (feature flag)."""
    out = []
    methods = [
        "ols_mean_reverting_residual",
        "kalman_pair_trade",
        "cointegration_eth_btc",
        "cointegration_sol_btc",
        "pca_factor_residual",
        "garch_vol_forecast_gating",
        "hmm_regime_classifier",
        "rl_bandits_param_select",
    ]
    for m, asset, win in itertools.product(methods, ["BTC", "ETH"], WINDOWS):
        out.append({
            "id": f"T4-ML-{m}-{asset}-{win}",
            "tier": 4, "engine": "ml_feature_flag",
            "direction": "adaptive", "timeframe": "1h",
            "asset": asset, "window": win,
            "regime_filter": "none",
            "params": f"method={m}",
            "prior": 0.05,
            "rationale": f"ML/stat experiment {m} (requires new code)",
        })
    return out


# =====================================================================
def build() -> list[dict]:
    blocks = [
        tier1_regime_detection_meta(),
        tier1_padrao50_extended(),
        tier1_padrao48_sol_regime(),
        tier1_portfolio_stack13(),
        tier1_stack_param_sensitivity(),
        tier2_bollinger_grid_1h(),
        tier2_rsi_grid_1h(),
        tier2_filter_combinations(),
        tier2_composite_mr_sweep(),
        tier3_tf_coverage(),
        tier3_short_variants(),
        tier3_keltner_zscore_deep(),
        tier3_asset_expansion(),
        tier4_stress_adversarial(),
        tier4_ablation(),
        tier4_exotic_signals(),
        tier4_ml_experiments(),
    ]
    all_entries = []
    for b in blocks:
        all_entries.extend(b)
    # enumerate index + pad to 1000 with parameter-further variations
    seen = set()
    deduped = []
    for e in all_entries:
        if e["id"] in seen:
            continue
        seen.add(e["id"])
        deduped.append(e)
    return deduped


def render_md(entries: list[dict]) -> str:
    lines = [
        "# Roadmap 1000 estratégias — TF10m exaustão + backlog",
        "",
        "**Date:** 2026-04-21",
        "**Status:** Draft",
        f"**Total entries:** {len(entries)}",
        "",
        "## Priority tiers",
        "",
        "- **Tier 1** (~250): high-EV extensions de achados atuais (Padrão 50 cross-era, Padrão 48 regime SOL, portfolio stack13, param sensitivity stack, regime detection meta).",
        "- **Tier 2** (~300): param grid sweeps engines stack canonical 1h (BB, RSI, composite, filter combos).",
        "- **Tier 3** (~300): coverage gaps (TFs non-MR, short variants, Keltner/zscore reabertura restritiva, asset expansion LINK/DOT/AVAX).",
        "- **Tier 4** (~150): long tail (stress adversarial, ablation, exotic signals requer código novo).",
        "",
        "## Execução",
        "",
        "Executar por **Fase** (bloco de 20-30 probes relacionadas), não por probe isolado. ~10min/probe → 1000 probes ≈ 170h compute (serial), ~5 semanas 24/7 ou distribuído.",
        "",
        "Recomendação: processar tier 1 primeiro (250 probes ≈ 42h) antes de mover para tier 2+.",
        "",
        "## Tabela completa",
        "",
        "| # | Tier | ID | Engine | Dir | TF | Asset | Window | Filter | Params | Prior | Rationale |",
        "|---:|---:|---|---|---|---|---|---|---|---|---:|---|",
    ]
    for i, e in enumerate(entries, 1):
        prior_pct = f"{int(e['prior']*100)}%"
        rat = e["rationale"][:60]
        lines.append(
            f"| {i} | T{e['tier']} | {e['id']} | {e['engine']} | {e['direction']} | "
            f"{e['timeframe']} | {e['asset']} | {e['window']} | "
            f"{e['regime_filter']} | {e['params']} | {prior_pct} | {rat} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    entries = build()
    # Cap to 1000
    entries = entries[:1000]
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text(render_md(entries), encoding="utf-8")
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(entries, indent=2), encoding="utf-8")
    tier_counts: dict[int, int] = {}
    for e in entries:
        tier_counts[e["tier"]] = tier_counts.get(e["tier"], 0) + 1
    print(f"Total entries: {len(entries)}")
    for t in sorted(tier_counts):
        print(f"  Tier {t}: {tier_counts[t]}")
    print(f"\nMarkdown: {OUT_MD}")
    print(f"JSON: {OUT_JSON}")


if __name__ == "__main__":
    main()
