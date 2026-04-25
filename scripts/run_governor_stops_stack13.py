"""Replay dos 13 combos com governor de perdas (3/5/7-stop rules).

Regra de gerenciamento pedida pelo user ("3 stop diminui mao pra 50% no dia,
5 stop para o dia, 7 stop seguido para a semana"):

  - Após 3 perdas no dia (UTC): sizing cai para 50% pelo resto do dia.
  - Após 5 perdas no dia (UTC): não abre mais entradas pelo resto do dia.
  - Após 7 perdas **consecutivas** (sem win entre elas): não abre mais entradas
    pelo resto da semana ISO (próxima segunda-feira reabre).

"Perda" = trade fechado com pnl < 0 (engine não usa stop-loss por ADR-0030;
o EXIT vem da estratégia ou do regime filter).

Mecânica de replay:
  - Rodamos o backtest em modo FIXED_NOTIONAL fracao=1.0 alav=1.0 (notional
    10k/trade). O stream de trades é sizing-invariant (estratégia só lê
    preços), então dá para replay-ar cada trade com factor ∈ {0.0, 0.5, 1.0}
    e escalar a pnl linearmente.
  - Um trade skipado (factor=0) não conta na contagem de perdas — não
    aconteceu. Um trade com factor=0.5 tem pnl escalado; sinal do pnl
    preservado.
  - Contadores resetam no cruzamento de dia / semana ISO.

Saída: exports/diag/governor_stops_stack13_<date>.json.
"""
from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from alpha_forge.backtest.cost import CostModel
from alpha_forge.backtest.engine import run_backtest
from alpha_forge.data.loaders import load_dataset
from alpha_forge.regimes.filter import (
    BollingerWidthFilter,
    TrendHTFRegimeFilter,
)
from alpha_forge.risk.schemas import RiskBudget, SizingMode
from alpha_forge.strategies.families.bollinger import BollingerMeanReversionStrategy
from alpha_forge.strategies.families.rsi import RSIMeanReversionStrategy


CAPITAL = 10_000.0
BARS_PER_YEAR_1H = 24 * 365

COST = CostModel(
    taker_fee_bps=5.0,
    slippage_bps_per_unit_notional=2.0,
    spread_bps=0.0,
)

# Governor thresholds (variante rescalada p/ 1h: 2/3/5).
HALF_AT = 2        # 2+ perdas no dia → factor 0.5 pelo resto do dia
STOP_DAY_AT = 3    # 3+ perdas no dia → skip pelo resto do dia
STOP_WEEK_AT = 5   # 5+ perdas consecutivas → skip pelo resto da semana ISO

# Import combos list do script irmão (mesmos 13 combos; reaproveita).
from run_snowball_100_stack13 import COMBOS  # noqa: E402


def build_strategy(combo: dict):
    kind = combo["strategy_kind"]
    p = combo["strat_params"]
    long_only = combo["long_only"]
    if kind == "bollinger":
        return BollingerMeanReversionStrategy(
            window=p["window"], num_std=p["num_std"], long_only=long_only
        )
    if kind == "rsi":
        return RSIMeanReversionStrategy(
            period=p["period"],
            oversold=p["oversold"],
            overbought=p["overbought"],
            long_only=long_only,
        )
    raise ValueError(kind)


def build_regime_filter(combo: dict):
    spec = combo["regime"]
    if spec is None:
        return None
    name, kwargs = spec
    if name == "bb_width":
        return BollingerWidthFilter(**kwargs)
    if name == "trend_htf":
        return TrendHTFRegimeFilter(**kwargs)
    raise ValueError(name)


@dataclass
class GovernorState:
    day_key: tuple[int, int, int] | None = None
    week_key: tuple[int, int] | None = None
    losses_today: int = 0
    consecutive_losses: int = 0
    blocked_day: bool = False
    blocked_week: bool = False
    # Contadores p/ diagnóstico:
    skipped_day: int = 0
    skipped_week: int = 0
    halved: int = 0
    full: int = 0


def _dk(dt: datetime) -> tuple[int, int, int]:
    dt = dt.astimezone(timezone.utc)
    return (dt.year, dt.month, dt.day)


def _wk(dt: datetime) -> tuple[int, int]:
    dt = dt.astimezone(timezone.utc)
    y, w, _ = dt.isocalendar()
    return (y, w)


def replay_with_governor(trades: list) -> dict:
    """Consome trades em ordem cronológica, aplica governor, devolve stats.

    Equity curve é por-trade (só marca em exit_timestamp). Sharpe calcula
    sobre retornos por-trade anualizado usando ~bars-per-year equivalente.
    Para comparabilidade com Sharpe-1h usamos retornos por barra reconstruídos
    step-wise, mas como todos os trades têm exit_timestamp timestamp no mesmo
    grid, usamos aqui o modo conservador: Sharpe = mean(r)/std(r) * sqrt(N_year)
    com N_year = número de trades no ano extrapolado.
    """
    state = GovernorState()
    equity = CAPITAL
    equity_curve: list[tuple[datetime, float]] = []
    scaled_trades: list[dict] = []
    running_max = CAPITAL
    min_equity = CAPITAL
    max_dd = 0.0

    for t in sorted(trades, key=lambda tr: tr.entry_timestamp):
        entry_dt = t.entry_timestamp
        day = _dk(entry_dt)
        week = _wk(entry_dt)

        # Reset no cruzamento de dia.
        if state.day_key != day:
            state.day_key = day
            state.losses_today = 0
            state.blocked_day = False
        # Reset no cruzamento de semana.
        if state.week_key != week:
            state.week_key = week
            state.blocked_week = False

        # Decisão de factor.
        if state.blocked_week:
            factor = 0.0
            reason = "blocked_week"
            state.skipped_week += 1
        elif state.blocked_day:
            factor = 0.0
            reason = "blocked_day"
            state.skipped_day += 1
        elif state.losses_today >= HALF_AT:
            factor = 0.5
            reason = "halved"
            state.halved += 1
        else:
            factor = 1.0
            reason = "full"
            state.full += 1

        pnl_raw = t.pnl  # notional 10k/trade
        pnl_scaled = pnl_raw * factor
        equity += pnl_scaled
        running_max = max(running_max, equity)
        min_equity = min(min_equity, equity)
        if running_max > 0:
            dd = 1.0 - (equity / running_max)
            if dd > max_dd:
                max_dd = dd
        equity_curve.append((t.exit_timestamp, equity))

        scaled_trades.append(dict(
            entry=t.entry_timestamp.isoformat(),
            exit=t.exit_timestamp.isoformat(),
            side=t.side.value if hasattr(t.side, "value") else str(t.side),
            pnl_raw=pnl_raw,
            factor=factor,
            pnl_scaled=pnl_scaled,
            reason=reason,
            losses_today_before=state.losses_today,
            consecutive_before=state.consecutive_losses,
        ))

        # Atualiza contadores com base no pnl ESCALADO. Trade skipado não conta.
        if factor > 0.0:
            if pnl_scaled < 0.0:
                state.losses_today += 1
                state.consecutive_losses += 1
                if state.losses_today >= STOP_DAY_AT:
                    state.blocked_day = True
                if state.consecutive_losses >= STOP_WEEK_AT:
                    state.blocked_week = True
            elif pnl_scaled > 0.0:
                state.consecutive_losses = 0
            # pnl == 0: no-op (raro com custos).

    return dict(
        final_equity=round(equity, 2),
        min_equity=round(min_equity, 2),
        max_drawdown_pct=round(max_dd * 100.0, 3),
        trade_count_input=len(trades),
        trade_count_executed=state.full + state.halved,
        skipped_day=state.skipped_day,
        skipped_week=state.skipped_week,
        halved=state.halved,
        full=state.full,
        scaled_trades=scaled_trades,
        equity_curve=[(dt.isoformat(), v) for dt, v in equity_curve],
    )


def trade_sharpe_from_curve(
    equity_curve: list[tuple[datetime, float]], span_hours: float
) -> float | None:
    """Sharpe annualizado estimado a partir de retornos log por-trade.

    ``span_hours`` = período total em horas (fim - início do dataset).
    Usamos trades/ano escala para annualizar: total_return_annual = total_return
    escalado linearmente; Sharpe usa retornos por-trade e multiplica por
    sqrt(trades_per_year). É a definição clássica para Sharpe em série de
    trades independentes.
    """
    if len(equity_curve) < 3:
        return None
    rets: list[float] = []
    prev = CAPITAL
    for _, v in equity_curve:
        if prev <= 0:
            rets.append(0.0)
        else:
            rets.append((v - prev) / prev)
        prev = v
    if not rets:
        return None
    n = len(rets)
    mean = sum(rets) / n
    var = sum((r - mean) ** 2 for r in rets) / (n - 1 if n > 1 else 1)
    sd = math.sqrt(var)
    if sd <= 0:
        return None
    # Converter p/ taxa por hora: distribui N trades ao longo de span_hours.
    if span_hours <= 0:
        return None
    trades_per_year = n * (BARS_PER_YEAR_1H / span_hours)
    return (mean / sd) * math.sqrt(trades_per_year)


def equity_curve_bar_sharpe(equity_curve_bar: list[float]) -> float | None:
    """Sharpe por barra (1h) equivalente ao usado em snowball/fixed_100."""
    if len(equity_curve_bar) < 3:
        return None
    rets = []
    for i in range(1, len(equity_curve_bar)):
        prev = equity_curve_bar[i - 1]
        cur = equity_curve_bar[i]
        if prev <= 0:
            rets.append(0.0)
        else:
            rets.append((cur - prev) / prev)
    if not rets:
        return None
    n = len(rets)
    mean = sum(rets) / n
    var = sum((r - mean) ** 2 for r in rets) / (n - 1 if n > 1 else 1)
    sd = math.sqrt(var)
    if sd <= 0:
        return None
    return (mean / sd) * math.sqrt(BARS_PER_YEAR_1H)


def build_bar_equity_from_scaled_trades(
    n_bars: int,
    bar_timestamps: list,
    trades_raw: list,
    scaled_trades: list[dict],
) -> list[float]:
    """Constrói equity por barra aplicando governor (mark-to-market open-next-bar).

    Para cada trade in-flight, unrealized = direction * size * (close[t] - entry_price).
    Factor escalona o size efetivo. Skipados não geram posição.
    """
    # Map idx por timestamp (ISO string).
    ts_index: dict[str, int] = {ts.isoformat(): i for i, ts in enumerate(bar_timestamps)}

    # Filter trades not skipped.
    active = []
    for raw, scaled in zip(
        sorted(trades_raw, key=lambda tr: tr.entry_timestamp),
        scaled_trades,
    ):
        if scaled["factor"] == 0.0:
            continue
        side_sign = 1 if (raw.side.value if hasattr(raw.side, "value") else str(raw.side)) == "LONG" else -1
        entry_iso = raw.entry_timestamp.isoformat()
        exit_iso = raw.exit_timestamp.isoformat()
        i_entry = ts_index.get(entry_iso)
        i_exit = ts_index.get(exit_iso)
        if i_entry is None or i_exit is None:
            continue
        active.append(dict(
            i_entry=i_entry,
            i_exit=i_exit,
            side_sign=side_sign,
            entry_price=raw.entry_price,
            size=raw.size * scaled["factor"],
            pnl_scaled=scaled["pnl_scaled"],
        ))

    # Map de pnl realizado em i_exit.
    realized_at_exit: dict[int, float] = {}
    for a in active:
        realized_at_exit[a["i_exit"]] = realized_at_exit.get(a["i_exit"], 0.0) + a["pnl_scaled"]

    # Varremos barras em ordem; uma posição pode estar in-flight entre i_entry+1 e i_exit.
    # Simplificação: equity por barra = capital + sum(realized até agora) + sum(unrealized in-flight).
    # Precisaríamos de close[t] — vou marcar apenas em i_exit (suficiente p/ MDD de equity por-trade).
    # Para MDD mais granular precisaria de closes; aqui usamos por-trade equity curve que o replay já
    # produz. Retornamos lista vazia para ignorar — usamos trade_sharpe.
    return []


def compute_span_hours(dataset_id: str) -> float:
    prices = load_dataset(dataset_id)
    if len(prices) < 2:
        return 0.0
    first = prices.index[0].to_pydatetime()
    last = prices.index[-1].to_pydatetime()
    return (last - first).total_seconds() / 3600.0


def run_one(combo: dict) -> dict:
    # FIXED_NOTIONAL 100% — baseline do replay.
    budget = RiskBudget(
        capital_inicial=CAPITAL,
        fracao_por_trade=1.0,
        alavancagem_max=1.0,
        sizing_mode=SizingMode.FIXED_NOTIONAL,
    )
    prices = load_dataset(combo["dataset_id"])
    strategy = build_strategy(combo)
    regime_filter = build_regime_filter(combo)
    result = run_backtest(
        prices=prices,
        strategy=strategy,
        budget=budget,
        cost_model=COST,
        dataset_id=combo["dataset_id"],
        regime_filter=regime_filter,
    )

    raw_trades = list(result.trades)
    # Baseline sem governor: apenas soma pnl linear.
    baseline_final = CAPITAL + sum(tr.pnl for tr in raw_trades)
    baseline_losses = sum(1 for tr in raw_trades if tr.pnl < 0)
    baseline_wins = sum(1 for tr in raw_trades if tr.pnl > 0)

    # Replay com governor.
    gov = replay_with_governor(raw_trades)

    # Sharpe por-trade annualizado.
    span_h = (prices.index[-1].to_pydatetime() - prices.index[0].to_pydatetime()).total_seconds() / 3600.0
    gov_curve = [(datetime.fromisoformat(ts), v) for ts, v in gov["equity_curve"]]
    sharpe_gov = trade_sharpe_from_curve(gov_curve, span_hours=span_h)

    baseline_curve: list[tuple[datetime, float]] = []
    eq = CAPITAL
    for tr in sorted(raw_trades, key=lambda x: x.entry_timestamp):
        eq += tr.pnl
        baseline_curve.append((tr.exit_timestamp, eq))
    sharpe_baseline = trade_sharpe_from_curve(baseline_curve, span_hours=span_h)

    return dict(
        baseline_fixed_100=dict(
            final_equity=round(baseline_final, 2),
            pnl_pct=round((baseline_final / CAPITAL - 1.0) * 100.0, 3),
            trade_count=len(raw_trades),
            wins=baseline_wins,
            losses=baseline_losses,
            sharpe_annual_pertrade=round(sharpe_baseline, 3) if sharpe_baseline is not None else None,
        ),
        governor=dict(
            final_equity=gov["final_equity"],
            pnl_pct=round((gov["final_equity"] / CAPITAL - 1.0) * 100.0, 3),
            min_equity=gov["min_equity"],
            max_drawdown_pct=gov["max_drawdown_pct"],
            trade_count_executed=gov["trade_count_executed"],
            full_size=gov["full"],
            halved=gov["halved"],
            skipped_day=gov["skipped_day"],
            skipped_week=gov["skipped_week"],
            sharpe_annual_pertrade=round(sharpe_gov, 3) if sharpe_gov is not None else None,
        ),
    )


def main() -> int:
    out: list[dict] = []
    for i, combo in enumerate(COMBOS, 1):
        label = f"{combo['manifest']}/{combo['symbol']}/{combo['window_tag']}"
        print(f"[{i:02d}/{len(COMBOS)}] {label} ...", flush=True)
        try:
            row = run_one(combo)
        except Exception as exc:  # noqa: BLE001
            print(f"    FAIL: {exc}", flush=True)
            out.append(dict(combo=label, error=str(exc)))
            continue
        b = row["baseline_fixed_100"]
        g = row["governor"]
        print(
            f"    base: Sh={b['sharpe_annual_pertrade']} PnL%={b['pnl_pct']} "
            f"tr={b['trade_count']} (W={b['wins']} L={b['losses']}) | "
            f"gov: Sh={g['sharpe_annual_pertrade']} PnL%={g['pnl_pct']} "
            f"MDD={g['max_drawdown_pct']}% min_eq={g['min_equity']} "
            f"exec={g['trade_count_executed']} "
            f"full={g['full_size']} half={g['halved']} "
            f"skip_d={g['skipped_day']} skip_w={g['skipped_week']}",
            flush=True,
        )
        out.append(dict(
            manifest=combo["manifest"],
            symbol=combo["symbol"],
            window_tag=combo["window_tag"],
            dataset_id=combo["dataset_id"],
            strategy_kind=combo["strategy_kind"],
            long_only=combo["long_only"],
            regime=combo["regime"],
            **row,
        ))

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    payload = dict(
        adr_prereg="decisions/0204-snowball-100pct-per-entry-stack13-prereg.md",
        adr_closeout="decisions/0207-governor-stops-stack13-closeout.md",
        capital_inicial=CAPITAL,
        cost_model=dict(
            taker_fee_bps=COST.taker_fee_bps,
            slippage_bps_per_unit_notional=COST.slippage_bps_per_unit_notional,
            spread_bps=COST.spread_bps,
        ),
        sizing_baseline=dict(
            fracao=1.0, alav=1.0, mode="fixed_notional",
            effective_notional_per_trade_usd=10_000,
        ),
        governor_rules=dict(
            half_at_losses_day=HALF_AT,
            stop_at_losses_day=STOP_DAY_AT,
            stop_at_consecutive_losses_week=STOP_WEEK_AT,
            day_boundary="UTC midnight",
            week_boundary="ISO week (Monday 00:00 UTC)",
            skipped_trade_counts=False,
            half_trade_counts_if_loss=True,
        ),
        generated_at=datetime.now(timezone.utc).isoformat(),
        combos=out,
    )
    out_path = Path(
        f"exports/diag/governor_stops_stack13_{HALF_AT}{STOP_DAY_AT}{STOP_WEEK_AT}_{stamp}.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(f"\nwrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
