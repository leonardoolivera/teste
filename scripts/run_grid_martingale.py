"""Grid martingale multi-ativo com equity pooled.

Spec:
  - equity inicial 10k USDT, alavancagem 20x
  - tranche = 1% do equity (margin); notional efetivo = 1% * 20 = 20% do equity
  - entrada: primeira tranche a mercado no bar 0; depois, cada queda de 1% vs ultima compra dispara nova tranche
  - saida: cada tranche sai independentemente a entry * 1.005 (TP +0.5%)
  - custo: fee 5bps + slip 2bps por notional (aplicados contra o trader em entrada e saida)
  - circuit breaker: por ativo, se close cair >= 5% vs max dos ultimos 24 bars -> modo CRASH -> pausa entries
    (TP continua). Sai do CRASH quando close >= SMA(24).
  - liquidacao: se mtm_equity <= total_notional * 0.005 (maint margin 20x), forca close all.

Execucao: sinais em close[t], fills em open[t+1], ADR-0030 runtime_contract.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

from alpha_forge.data.loaders import load_dataset

WINDOWS = [
    ("2022h1", "20220105_20220704"),
    ("2022h2", "20220705_20221231"),
    ("2023h2", "20230705_20231231"),
    ("2024h1", "20240105_20240704"),
    ("2024h2", "20240705_20241231"),
    ("2025h1", "20250105_20250704"),
    ("2025h2", "20250705_20251231"),
]

ALL_SYMBOLS = ["BTCUSDT"]

CAPITAL = 10_000.0
LEVERAGE = 20.0
TRANCHE_MARGIN_PCT = 0.01
DROP_TRIGGER = 0.01
TP_FAST = 0.005           # 75% das units saem aqui
TP_SLOW = 0.20            # 25% restantes seguram ate +20%
FAST_FRAC = 0.75
BE_ARM = 0.03             # ao passar de +3%, arma stop no breakeven
STREAK_BOOST_AT = 3       # a partir de 3 TPs seguidos no simbolo, dobra o tamanho
STREAK_BOOST_MULT = 2.0
FEE_BPS = 5.0
SLIP_BPS = 2.0
BASE_TIMEFRAME = "5m"     # fonte ingerida
TARGET_TIMEFRAME = "10m"  # agregado (2 bars 5m = 1 bar 10m)
AGG_FACTOR = 2
BARS_PER_HOUR = 6         # 10m
TREND_LOOKBACK = 200 * BARS_PER_HOUR  # mantem semantica de 200h
CRASH_DROP = 0.05
CRASH_LOOKBACK = 24 * BARS_PER_HOUR   # mantem 24h


def dsid(symbol: str, window_tag: str) -> str:
    return f"{symbol.lower()}_{BASE_TIMEFRAME}_{window_tag}_binance_spot"


def resample_to_target(df: pd.DataFrame) -> pd.DataFrame:
    if AGG_FACTOR <= 1:
        return df
    rule = TARGET_TIMEFRAME.replace("m", "min").replace("h", "H")
    agg = df.resample(rule, label="left", closed="left").agg({
        "open": "first", "high": "max", "low": "min", "close": "last",
        "volume": "sum",
    }).dropna(how="any")
    return agg


def load_aligned(symbols: list[str], window_tag: str) -> dict[str, pd.DataFrame]:
    frames: dict[str, pd.DataFrame] = {}
    for s in symbols:
        try:
            raw = load_dataset(dsid(s, window_tag))
            frames[s] = resample_to_target(raw)
        except Exception:
            pass
    if not frames:
        return {}
    idx = None
    for df in frames.values():
        idx = df.index if idx is None else idx.intersection(df.index)
    return {s: df.loc[idx].sort_index() for s, df in frames.items()}


def simulate(data: dict[str, pd.DataFrame]) -> dict:
    symbols = list(data.keys())
    common_idx = list(next(iter(data.values())).index)
    n = len(common_idx)

    equity = CAPITAL
    tranches: dict[str, list[dict]] = {s: [] for s in symbols}
    last_buy_price: dict[str, float | None] = {s: None for s in symbols}
    crash_state: dict[str, bool] = {s: False for s in symbols}
    entries_skipped_crash = {s: 0 for s in symbols}
    entries_skipped_trend = {s: 0 for s in symbols}
    entries_taken = {s: 0 for s in symbols}
    consec_tp = {s: 0 for s in symbols}
    boosted_entries = {s: 0 for s in symbols}
    trades: list[dict] = []
    equity_curve: list[dict] = []
    crash_bars = {s: 0 for s in symbols}
    blowup = False
    blowup_ts: str | None = None

    closes = {s: data[s]["close"].to_numpy() for s in symbols}
    opens = {s: data[s]["open"].to_numpy() for s in symbols}
    sma200 = {s: pd.Series(closes[s]).rolling(TREND_LOOKBACK, min_periods=TREND_LOOKBACK).mean().to_numpy() for s in symbols}
    tss = [t for t in common_idx]

    for t in range(n - 1):
        ts_exec = tss[t + 1]
        # crash state per symbol usando close[t] e lookback [t-23..t]
        lb_start = max(0, t - CRASH_LOOKBACK + 1)
        for s in symbols:
            window = closes[s][lb_start : t + 1]
            recent_high = window.max()
            drop_from_high = closes[s][t] / recent_high - 1.0
            if not crash_state[s] and drop_from_high <= -CRASH_DROP:
                crash_state[s] = True
            elif crash_state[s]:
                sma = window.mean()
                if closes[s][t] >= sma:
                    crash_state[s] = False
            if crash_state[s]:
                crash_bars[s] += 1

        # Exits: TP (fast @+0.5% / slow @+20%) e stop-breakeven (armado em +3%)
        for s in symbols:
            survivors = []
            for tr in tranches[s]:
                exit_kind = None
                if closes[s][t] >= tr["entry_price"] * (1 + tr["tp"]):
                    exit_kind = tr["kind"]
                else:
                    if not tr.get("be_armed") and closes[s][t] >= tr["entry_price"] * (1 + BE_ARM):
                        tr["be_armed"] = True
                    if tr.get("be_armed") and closes[s][t] <= tr["entry_price"]:
                        exit_kind = "be_stop"
                if exit_kind is not None:
                    exit_price_raw = opens[s][t + 1]
                    fill_price = exit_price_raw * (1 - SLIP_BPS / 1e4)
                    gross = (fill_price - tr["entry_price"]) * tr["units"]
                    fee_exit = fill_price * tr["units"] * FEE_BPS / 1e4
                    pnl = gross - fee_exit
                    equity += pnl
                    trades.append({
                        "symbol": s, "kind": exit_kind,
                        "entry_ts": tr["entry_ts"], "exit_ts": ts_exec.isoformat(),
                        "entry_price": tr["entry_price"], "exit_price": fill_price,
                        "units": tr["units"], "notional": tr["notional"], "pnl": pnl,
                    })
                    if exit_kind in ("tp_fast", "tp_slow"):
                        consec_tp[s] += 1
                    elif exit_kind == "be_stop":
                        consec_tp[s] = 0
                else:
                    survivors.append(tr)
            tranches[s] = survivors

        # entries
        for s in symbols:
            if equity <= 0:
                break
            should_enter = False
            if last_buy_price[s] is None:
                should_enter = True
            elif closes[s][t] <= last_buy_price[s] * (1 - DROP_TRIGGER):
                should_enter = True

            sma_val = sma200[s][t]
            trend_ok = sma_val == sma_val and closes[s][t] >= sma_val  # NaN-safe
            if should_enter and not trend_ok:
                entries_skipped_trend[s] += 1
                continue

            if should_enter and crash_state[s]:
                entries_skipped_crash[s] += 1
                continue

            if should_enter:
                raw_price = opens[s][t + 1]
                entry_price = raw_price * (1 + SLIP_BPS / 1e4)
                current_leverage = LEVERAGE * (equity / CAPITAL)
                sma_now = sma200[s][t]
                sma_prev_bars = 24 * BARS_PER_HOUR
                sma_prev = sma200[s][t - sma_prev_bars] if t >= sma_prev_bars else float("nan")
                sma_rising = (sma_now == sma_now) and (sma_prev == sma_prev) and (sma_now > sma_prev)
                size_mult = STREAK_BOOST_MULT if (consec_tp[s] >= STREAK_BOOST_AT and sma_rising) else 1.0
                if size_mult > 1.0:
                    boosted_entries[s] += 1
                margin = equity * TRANCHE_MARGIN_PCT * size_mult
                notional = margin * current_leverage
                units_total = notional / entry_price
                fee_entry = notional * FEE_BPS / 1e4
                equity -= fee_entry
                units_fast = units_total * FAST_FRAC
                units_slow = units_total - units_fast
                notional_fast = notional * FAST_FRAC
                notional_slow = notional - notional_fast
                tranches[s].append({
                    "entry_ts": ts_exec.isoformat(), "kind": "tp_fast", "tp": TP_FAST,
                    "entry_price": entry_price, "units": units_fast, "notional": notional_fast,
                })
                tranches[s].append({
                    "entry_ts": ts_exec.isoformat(), "kind": "tp_slow", "tp": TP_SLOW,
                    "entry_price": entry_price, "units": units_slow, "notional": notional_slow,
                })
                last_buy_price[s] = entry_price
                entries_taken[s] += 1

        # mark-to-market + check liquidation
        unrealized = 0.0
        total_notional = 0.0
        total_open = 0
        for s in symbols:
            for tr in tranches[s]:
                unrealized += (closes[s][t] - tr["entry_price"]) * tr["units"]
                total_notional += tr["notional"]
                total_open += 1
        mtm = equity + unrealized

        maint = total_notional * 0.005
        if total_notional > 0 and mtm <= maint:
            blowup = True
            blowup_ts = ts_exec.isoformat()
            for s in symbols:
                for tr in tranches[s]:
                    fill_price = closes[s][t] * (1 - SLIP_BPS / 1e4)
                    gross = (fill_price - tr["entry_price"]) * tr["units"]
                    fee_exit = fill_price * tr["units"] * FEE_BPS / 1e4
                    pnl = gross - fee_exit
                    equity += pnl
                    trades.append({
                        "symbol": s, "kind": "forced_liq",
                        "entry_ts": tr["entry_ts"], "exit_ts": blowup_ts,
                        "entry_price": tr["entry_price"], "exit_price": fill_price,
                        "units": tr["units"], "notional": tr["notional"], "pnl": pnl,
                    })
                tranches[s] = []
            equity_curve.append({"ts": ts_exec.isoformat(), "equity": equity, "mtm": equity,
                                  "n_open": 0, "notional": 0.0})
            break

        equity_curve.append({
            "ts": ts_exec.isoformat(), "equity": equity, "mtm": mtm,
            "n_open": total_open, "notional": total_notional,
        })

    # final mark-to-market close-out se nao deu blowup
    if not blowup:
        final_ts = tss[n - 1].isoformat()
        for s in symbols:
            last_close = closes[s][n - 1]
            for tr in tranches[s]:
                fill_price = last_close * (1 - SLIP_BPS / 1e4)
                gross = (fill_price - tr["entry_price"]) * tr["units"]
                fee_exit = fill_price * tr["units"] * FEE_BPS / 1e4
                pnl = gross - fee_exit
                equity += pnl
                trades.append({
                    "symbol": s, "kind": "mark_close",
                    "entry_ts": tr["entry_ts"], "exit_ts": final_ts,
                    "entry_price": tr["entry_price"], "exit_price": fill_price,
                    "units": tr["units"], "notional": tr["notional"], "pnl": pnl,
                })
            tranches[s] = []

    # metrics
    peak = CAPITAL
    mdd = 0.0
    for row in equity_curve:
        v = row["mtm"]
        peak = max(peak, v)
        if peak > 0:
            mdd = max(mdd, (peak - v) / peak)

    wins = sum(1 for t in trades if t["pnl"] > 0)
    losses = len(trades) - wins
    tp_trades = [t for t in trades if t["kind"] in ("tp_fast", "tp_slow")]
    tp_fast_trades = [t for t in trades if t["kind"] == "tp_fast"]
    tp_slow_trades = [t for t in trades if t["kind"] == "tp_slow"]
    be_trades = [t for t in trades if t["kind"] == "be_stop"]
    liq_trades = [t for t in trades if t["kind"] == "forced_liq"]
    markclose = [t for t in trades if t["kind"] == "mark_close"]

    return {
        "n_bars": n,
        "symbols": symbols,
        "final_equity": round(equity, 2),
        "final_pnl_pct": round((equity / CAPITAL - 1) * 100, 3),
        "blowup": blowup,
        "blowup_ts": blowup_ts,
        "mdd_pct": round(mdd * 100, 3),
        "n_trades": len(trades),
        "tp_trades": len(tp_trades),
        "tp_fast_trades": len(tp_fast_trades),
        "tp_slow_trades": len(tp_slow_trades),
        "be_stop_trades": len(be_trades),
        "forced_liq_trades": len(liq_trades),
        "mark_close_trades": len(markclose),
        "hit_rate": round(wins / len(trades), 3) if trades else None,
        "entries_taken_per_symbol": entries_taken,
        "boosted_entries_per_symbol": boosted_entries,
        "entries_skipped_by_trend_per_symbol": entries_skipped_trend,
        "entries_skipped_by_crash_per_symbol": entries_skipped_crash,
        "crash_bars_per_symbol": crash_bars,
        "max_open_tranches": max((r["n_open"] for r in equity_curve), default=0),
        "max_notional_abs": round(max((r["notional"] for r in equity_curve), default=0), 2),
        "max_notional_mult_equity": round(
            max((r["notional"] / max(r["mtm"], 1e-9) for r in equity_curve), default=0), 2),
    }


def main() -> int:
    out = {"params": {
        "capital": CAPITAL, "leverage": LEVERAGE, "tranche_margin_pct": TRANCHE_MARGIN_PCT,
        "drop_trigger": DROP_TRIGGER,
        "tp_fast": TP_FAST, "tp_slow": TP_SLOW, "fast_frac": FAST_FRAC,
        "be_arm": BE_ARM,
        "streak_boost_at": STREAK_BOOST_AT, "streak_boost_mult": STREAK_BOOST_MULT,
        "trend_lookback": TREND_LOOKBACK,
        "fee_bps": FEE_BPS, "slip_bps": SLIP_BPS,
        "crash_drop": CRASH_DROP, "crash_lookback": CRASH_LOOKBACK,
    }, "results": []}

    for tag, window_str in WINDOWS:
        data = load_aligned(ALL_SYMBOLS, window_str)
        if not data:
            print(f"[{tag}] sem dados"); continue
        r = simulate(data)
        r["window"] = tag
        out["results"].append(r)
        verdict = "BLOWUP" if r["blowup"] else f"pnl={r['final_pnl_pct']:+.2f}%"
        print(f"[{tag}] symbols={r['symbols']} bars={r['n_bars']} "
              f"trades={r['n_trades']} tp_fast={r['tp_fast_trades']} tp_slow={r['tp_slow_trades']} "
              f"be={r['be_stop_trades']} liq={r['forced_liq_trades']} "
              f"mdd={r['mdd_pct']}% max_open={r['max_open_tranches']} "
              f"max_notional_mult={r['max_notional_mult_equity']}x  {verdict}")

    Path("results/grid_martingale_summary.json").write_text(
        json.dumps(out, indent=2, default=str), encoding="utf-8")
    print("\nsummary -> results/grid_martingale_summary.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
