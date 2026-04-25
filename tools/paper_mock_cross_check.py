"""Paper-mock cross-check: compara engine AF canonical vs log runtime do bot.

Acionado pelo ADR-0036 (incidente 2026-04-19 RiskDecision crash).

Modos:
  - A (preferível): candles 1h reais do bot em parquet/CSV + log de eventos do bot
    em JSONL. AF roda engine canonical sobre os mesmos candles e compara signal/fill/exit
    tick-a-tick.
  - B (fallback): só log de eventos do bot; AF replica candle stream via Binance public
    API e cruza por timestamp.

Uso:
    python tools/paper_mock_cross_check.py --feed-mode A --symbol SOLUSDT
    python tools/paper_mock_cross_check.py --feed-mode B --symbol ETHUSDT --start 2026-04-19T10:00:00Z

Source of truth de paths:
    c:/Users/leo-a/agents_bridge/paper_mock_feed/{SYMBOL}_1h.parquet   (Opção A)
    c:/Users/leo-a/agents_bridge/paper_mock_feed/{SYMBOL}_events.jsonl (Opções A ou B)
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from alpha_forge.backtest.schemas import Signal
from alpha_forge.regimes.filter import BollingerWidthFilter
from alpha_forge.strategies.families.bollinger import BollingerMeanReversionStrategy


BRIDGE_FEED_DIR = Path("c:/Users/leo-a/agents_bridge/paper_mock_feed")

# Parâmetros canonizados do manifest v2 (engine.params + engine.params.regime_filter)
# IMPORTANTE: regime_filter é window=30, num_std=1.5 conforme manifest aprovado
# (ADR-0028, ADR-0029). Defaults BollingerWidthFilter (20/2) NÃO se aplicam aqui.
ENGINE_PARAMS = dict(window=30, num_std=1.5, long_only=True)
REGIME_PARAMS = dict(window=30, num_std=1.5, min_width_bps=250.0)
MANIFEST_NOTIONAL_USD = 2000.0


@dataclass
class BotEvent:
    ts: pd.Timestamp
    symbol: str
    event: str
    payload: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_jsonl_line(cls, line: str) -> "BotEvent":
        d = json.loads(line)
        return cls(
            ts=pd.Timestamp(d["ts"]),
            symbol=d["symbol"],
            event=d["event"],
            payload=d.get("payload", {}),
        )


@dataclass
class AFPrediction:
    ts: pd.Timestamp
    signal: Signal
    regime_active: bool
    close_tm1: float
    mu_now: float
    lower_now: float


def load_candles(symbol: str) -> pd.DataFrame:
    """Carrega feed CSV ou parquet do bridge. Bot exporta CSV por default."""
    csv_p = BRIDGE_FEED_DIR / f"{symbol}_1h.csv"
    pq_p = BRIDGE_FEED_DIR / f"{symbol}_1h.parquet"
    if csv_p.exists():
        df = pd.read_csv(csv_p, parse_dates=["timestamp_utc"])
        df = df.set_index("timestamp_utc").sort_index()
    elif pq_p.exists():
        df = pd.read_parquet(pq_p).sort_index()
    else:
        raise FileNotFoundError(f"esperado {csv_p} ou {pq_p}")
    required = {"open", "high", "low", "close", "volume"}
    if not required.issubset(df.columns):
        raise ValueError(f"feed faltando colunas: {required - set(df.columns)}")
    return df


def load_bot_events(symbol: str) -> list[BotEvent]:
    p = BRIDGE_FEED_DIR / f"{symbol}_events.jsonl"
    if not p.exists():
        return []
    events = []
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        events.append(BotEvent.from_jsonl_line(line))
    return [e for e in events if e.symbol == symbol]


def run_af_engine(df: pd.DataFrame) -> list[AFPrediction]:
    """Emite predições AF bar-a-bar (causal: usa iloc[:t+1] por t)."""
    strat = BollingerMeanReversionStrategy(**ENGINE_PARAMS)
    regime = BollingerWidthFilter(**REGIME_PARAMS)
    preds: list[AFPrediction] = []
    ts = df.index.to_series().reset_index(drop=True)
    body = df.reset_index(drop=True)
    for t in range(len(body)):
        window = body.iloc[: t + 1]
        sig = strat.decide(window)
        if sig not in (Signal.ENTER_LONG, Signal.EXIT):
            continue
        active = regime.is_active(window)
        closes = window["close"].iloc[:-1]
        now_slice = closes.iloc[-strat.window:]
        mu_now = float(now_slice.mean())
        sigma_now = float(now_slice.std(ddof=0))
        lower_now = mu_now - strat.num_std * sigma_now
        preds.append(AFPrediction(
            ts=ts.iloc[t],
            signal=sig,
            regime_active=active,
            close_tm1=float(closes.iloc[-1]),
            mu_now=mu_now,
            lower_now=lower_now,
        ))
    return preds


def cross_check(symbol: str, feed_mode: str, bot_active_since: pd.Timestamp | None = None) -> dict[str, Any]:
    if feed_mode == "A":
        df = load_candles(symbol)
    elif feed_mode == "B":
        raise NotImplementedError("Modo B (Binance public API) será implementado "
                                  "se @botbinance optar por essa entrega")
    else:
        raise ValueError(f"feed_mode inválido: {feed_mode}")

    events = load_bot_events(symbol)
    if not events:
        print(f"[warn] {symbol}: nenhum evento do bot carregado. Paper-mock so tera predicoes AF.", file=sys.stderr)

    af_preds = run_af_engine(df)
    af_signals = [p for p in af_preds if p.regime_active]
    if bot_active_since is not None:
        # Pré-ativação não conta — bot estava offline pra esta engine
        af_signals = [p for p in af_signals if p.ts >= bot_active_since]

    # Mapeia eventos do bot por tipo
    bot_signals = [e for e in events if e.event == "SIGNAL_CREATED"]
    bot_fills = [e for e in events if e.event == "POSITION_OPENED"]
    bot_closes = [e for e in events if e.event == "POSITION_CLOSED"]

    # Diff por timestamp de signal — bot loga no real-time do candle close,
    # AF indexa pelo open. Floor bot ts para hora antes de comparar.
    divergences: list[str] = []
    af_signal_ts = {p.ts for p in af_signals}
    bot_signal_ts = {e.ts.floor("1h") for e in bot_signals}

    only_af = af_signal_ts - bot_signal_ts
    only_bot = bot_signal_ts - af_signal_ts

    for ts in sorted(only_af):
        divergences.append(f"AF emitiu signal em {ts} que bot NÃO emitiu")
    for ts in sorted(only_bot):
        divergences.append(f"Bot emitiu signal em {ts} que AF NÃO emitiu")

    # Fills: comparar fill_price do bot vs open[t+1] esperado pela ADR-0030
    for fill in bot_fills:
        entry_ts = fill.payload.get("entry_ts") or fill.payload.get("ts")
        expected_bar_ts = pd.Timestamp(entry_ts)
        # open do candle em entry_ts é o preço teoricamente executado (market@open[t+1])
        if expected_bar_ts in df.index:
            expected_open = float(df.loc[expected_bar_ts, "open"])
            actual_fill = float(fill.payload.get("fill_price", 0))
            if abs(actual_fill - expected_open) / expected_open > 0.001:  # >10bps
                divergences.append(
                    f"{fill.ts}: fill_price={actual_fill} difere de open[t+1]={expected_open}"
                )

    report = {
        "symbol": symbol,
        "feed_mode": feed_mode,
        "n_candles": len(df),
        "n_af_predictions": len(af_preds),
        "n_af_regime_active_signals": len(af_signals),
        "n_bot_signals": len(bot_signals),
        "n_bot_fills": len(bot_fills),
        "n_bot_closes": len(bot_closes),
        "divergences": divergences,
        "divergence_count": len(divergences),
        "verdict": "CLEAN" if not divergences else "DIVERGENCE_DETECTED",
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", required=True, choices=["ETHUSDT", "SOLUSDT"])
    parser.add_argument("--feed-mode", default="A", choices=["A", "B"])
    parser.add_argument("--out", default=None, help="path pra salvar report JSON")
    parser.add_argument("--bot-active-since", default="2026-04-19T00:00:00Z",
                        help="ISO ts; AF signals antes desse instante são ignorados (bot estava offline pra engine)")
    args = parser.parse_args()

    bot_active_since = pd.Timestamp(args.bot_active_since) if args.bot_active_since else None
    report = cross_check(args.symbol, args.feed_mode, bot_active_since=bot_active_since)
    print(json.dumps(report, indent=2, default=str))

    if args.out:
        Path(args.out).write_text(json.dumps(report, indent=2, default=str))

    return 0 if report["verdict"] == "CLEAN" else 2


if __name__ == "__main__":
    sys.exit(main())
