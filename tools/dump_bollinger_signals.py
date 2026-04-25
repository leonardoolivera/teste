"""Dump bollinger signals for ETH 2025-H1 para comparar com standalone do bot.

Uso:
    python tools/dump_bollinger_signals.py
Gera: exports/diag/bollinger_eth_2025h1_signals.csv
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from alpha_forge.backtest.schemas import Signal
from alpha_forge.regimes.filter import BollingerWidthFilter
from alpha_forge.strategies.families.bollinger import BollingerMeanReversionStrategy


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    parquet = root / "data" / "processed" / "ETHUSDT" / "1h" / "ethusdt_1h_20250105_20250704_binance_spot.parquet"
    df = pd.read_parquet(parquet).sort_index()
    ts = df.index.to_series().reset_index(drop=True)
    df = df.reset_index(drop=True)

    strat = BollingerMeanReversionStrategy(window=30, num_std=1.5, long_only=True)
    regime = BollingerWidthFilter(window=30, num_std=1.5, min_width_bps=250.0)

    rows = []
    n = len(df)
    for t in range(n):
        window = df.iloc[: t + 1]
        sig = strat.decide(window)
        if sig in (Signal.ENTER_LONG, Signal.EXIT):
            regime_active = regime.is_active(window)
            closes = window["close"].iloc[:-1]
            now_slice = closes.iloc[-strat.window:]
            prev_slice = closes.iloc[-strat.window - 1 : -1]
            mu_now = float(now_slice.mean())
            sigma_now = float(now_slice.std(ddof=0))
            mu_prev = float(prev_slice.mean())
            sigma_prev = float(prev_slice.std(ddof=0))
            lower_now = mu_now - strat.num_std * sigma_now
            lower_prev = mu_prev - strat.num_std * sigma_prev
            c_tm1 = float(closes.iloc[-1])
            c_tm2 = float(closes.iloc[-2])
            rows.append({
                "t": t,
                "ts_signal": str(ts.iloc[t]),
                "ts_exec_next_open": str(ts.iloc[t + 1]) if t + 1 < n else "",
                "signal": sig.name,
                "regime_active": regime_active,
                "close_tm1": c_tm1,
                "close_tm2": c_tm2,
                "mu_now": mu_now,
                "sigma_now": sigma_now,
                "mu_prev": mu_prev,
                "sigma_prev": sigma_prev,
                "lower_now": lower_now,
                "lower_prev": lower_prev,
            })

    out_dir = root / "exports" / "diag"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "bollinger_eth_2025h1_signals.csv"
    pd.DataFrame(rows).to_csv(out_path, index=False)

    n_enter = sum(1 for r in rows if r["signal"] == "ENTER_LONG")
    n_exit = sum(1 for r in rows if r["signal"] == "EXIT")
    n_enter_gated = sum(1 for r in rows if r["signal"] == "ENTER_LONG" and r["regime_active"])
    n_exit_gated = sum(1 for r in rows if r["signal"] == "EXIT" and r["regime_active"])
    print(f"raw signals: {n_enter} ENTER_LONG, {n_exit} EXIT")
    print(f"regime-gated (bw_250): {n_enter_gated} ENTER_LONG, {n_exit_gated} EXIT")
    print(f"wrote {len(rows)} rows -> {out_path}")


if __name__ == "__main__":
    main()
