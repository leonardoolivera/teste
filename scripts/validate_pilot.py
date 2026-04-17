"""Validação séria do piloto — sensibilidade a fees e slippage + sanidade.

Uso:
    python scripts/validate_pilot.py --strategy donchian \
        --dataset-id btcusdt_1h_20250705_20251231_binance_spot \
        --entry-window 20 --exit-window 10

Produz:
  - stdout: tabela de sensibilidade (fees × slippage) sobre métricas.
  - results/validation/<timestamp>_<strategy>.json — artefato reproduzível.

Escopo deliberadamente mínimo:
  - Grid cartesiano pequeno (fee × slippage).
  - Métricas já expostas por BacktestMetrics (ADR-0007).
  - Checagem de lookahead pelo property-based existente (chamado externamente).

Não pretende substituir `validation/` quando o módulo nascer. É camada
instrumental do laboratório agentic para alimentar BACKTEST.md / AUDIT.md.

LIVE_TRADING é estrutural: False sempre. Este script NÃO envia ordem a
nenhuma exchange e não importa nenhum SDK de venue real.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from alpha_forge.backtest.cost import CostModel
from alpha_forge.backtest.engine import run_backtest
from alpha_forge.data.loaders import load_dataset
from alpha_forge.io.paths import project_root
from alpha_forge.risk.schemas import RiskBudget
from alpha_forge.strategies.families.donchian import DonchianBreakoutStrategy
from alpha_forge.strategies.families.ma_crossover import MovingAverageCrossoverStrategy

LIVE_TRADING: bool = False
"""Constante estrutural: nunca True neste repositório. Ver CLAUDE.md §2."""

FEE_GRID_BPS = (0.0, 5.0, 10.0, 20.0)
SLIP_GRID_BPS = (0.0, 2.0, 5.0, 10.0)


@dataclass(frozen=True)
class Row:
    taker_fee_bps: float
    slippage_bps_per_notional: float
    total_pnl: float
    trade_count: int
    hit_rate: float | None
    max_drawdown: float
    final_equity: float


def _build_strategy(name: str, *, short: int, long: int, entry: int, exit_: int):
    if name == "ma_crossover":
        return MovingAverageCrossoverStrategy(short_window=short, long_window=long)
    if name == "donchian":
        return DonchianBreakoutStrategy(entry_window=entry, exit_window=exit_)
    raise SystemExit(f"estratégia desconhecida para validação: {name}")


def _one_run(
    *, prices, strategy, budget: RiskBudget, cost_model: CostModel, dataset_id: str
) -> Row:
    result = run_backtest(
        prices=prices,
        strategy=strategy,
        budget=budget,
        cost_model=cost_model,
        dataset_id=dataset_id,
    )
    m = result.metrics
    assert m is not None, "engine sempre preenche metrics (ADR-0007)"
    return Row(
        taker_fee_bps=cost_model.taker_fee_bps,
        slippage_bps_per_notional=cost_model.slippage_bps_per_unit_notional,
        total_pnl=m.total_pnl,
        trade_count=m.trade_count,
        hit_rate=m.hit_rate,
        max_drawdown=m.max_drawdown,
        final_equity=result.final_equity,
    )


def _sensitivity_grid(
    *, dataset_id, strategy_name, short, long, entry, exit_, capital, fracao, alavancagem
) -> list[Row]:
    prices = load_dataset(dataset_id)
    budget = RiskBudget(
        capital_inicial=capital,
        fracao_por_trade=fracao,
        alavancagem_max=alavancagem,
    )
    rows: list[Row] = []
    for fee in FEE_GRID_BPS:
        for slip in SLIP_GRID_BPS:
            strat = _build_strategy(
                strategy_name, short=short, long=long, entry=entry, exit_=exit_
            )
            cm = CostModel(
                taker_fee_bps=fee,
                slippage_bps_per_unit_notional=slip,
            )
            rows.append(
                _one_run(
                    prices=prices,
                    strategy=strat,
                    budget=budget,
                    cost_model=cm,
                    dataset_id=dataset_id,
                )
            )
    return rows


def _check_monotonic_cost(rows: list[Row]) -> list[str]:
    """Sanidade: com fee e slip zerados, final_equity deve ser >= casos com custo.

    Não é o property-based formal (ADR-0010); é um checo grosseiro do grid.
    """
    problems: list[str] = []
    baseline = next(
        (
            r
            for r in rows
            if r.taker_fee_bps == 0.0 and r.slippage_bps_per_notional == 0.0
        ),
        None,
    )
    if baseline is None:
        return ["grid não contém (fee=0, slip=0) como baseline"]
    for r in rows:
        if r is baseline:
            continue
        if r.final_equity > baseline.final_equity + 1e-6:
            problems.append(
                f"violação de monotonicidade esperada: "
                f"fee={r.taker_fee_bps} slip={r.slippage_bps_per_notional} "
                f"final_equity={r.final_equity:.2f} > baseline zero={baseline.final_equity:.2f}"
            )
    return problems


def _print_table(rows: list[Row]) -> None:
    header = (
        "fee(bps) slip(bps)  trades  hit_rate  max_dd   final_equity   total_pnl"
    )
    print(header)
    print("-" * len(header))
    for r in sorted(
        rows, key=lambda x: (x.taker_fee_bps, x.slippage_bps_per_notional)
    ):
        hit = f"{r.hit_rate * 100:6.2f}%" if r.hit_rate is not None else "   N/A"
        print(
            f"{r.taker_fee_bps:7.2f} {r.slippage_bps_per_notional:9.2f} "
            f"{r.trade_count:7d}  {hit}  {r.max_drawdown * 100:6.2f}% "
            f"{r.final_equity:13.2f}  {r.total_pnl:+10.2f}"
        )


def _dump_artifact(
    *,
    strategy_name: str,
    dataset_id: str,
    rows: list[Row],
    problems: list[str],
    params: dict[str, int | float | str],
) -> Path:
    out_dir = project_root() / "results" / "validation"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = out_dir / f"{ts}_{strategy_name}.json"
    payload = {
        "live_trading": LIVE_TRADING,
        "release_mode": "backtest_only",
        "strategy": strategy_name,
        "dataset_id": dataset_id,
        "params": params,
        "grid": [asdict(r) for r in rows],
        "monotonicity_problems": problems,
        "timestamp_utc": ts,
    }
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return path


def main() -> int:
    if LIVE_TRADING:
        raise SystemExit(
            "LIVE_TRADING é True — abortando. Este repositório não executa ordens reais."
        )

    p = argparse.ArgumentParser(
        prog="validate_pilot",
        description="Sensibilidade de custos + sanidade do piloto Alpha Forge.",
    )
    p.add_argument("--strategy", default="donchian", choices=("donchian", "ma_crossover"))
    p.add_argument(
        "--dataset-id",
        default="btcusdt_1h_20250705_20251231_binance_spot",
        help="id do manifesto. Use synthetic_btcusdt_1h_seed42 em ambiente limpo.",
    )
    p.add_argument("--entry-window", type=int, default=20)
    p.add_argument("--exit-window", type=int, default=10)
    p.add_argument("--short-window", type=int, default=20)
    p.add_argument("--long-window", type=int, default=50)
    p.add_argument("--capital", type=float, default=10_000.0)
    p.add_argument("--fracao", type=float, default=0.1)
    p.add_argument("--alavancagem", type=float, default=2.0)
    args = p.parse_args()

    try:
        rows = _sensitivity_grid(
            dataset_id=args.dataset_id,
            strategy_name=args.strategy,
            short=args.short_window,
            long=args.long_window,
            entry=args.entry_window,
            exit_=args.exit_window,
            capital=args.capital,
            fracao=args.fracao,
            alavancagem=args.alavancagem,
        )
    except FileNotFoundError as exc:
        print(f"[validate_pilot] dataset não encontrado: {exc}", file=sys.stderr)
        print(
            "Ingeste via `python scripts/ingest_binance_vision.py --symbols BTCUSDT "
            "--timeframe 1h --start 2025-07-05 --end 2025-12-31` ou use o sintético.",
            file=sys.stderr,
        )
        return 3

    problems = _check_monotonic_cost(rows)
    _print_table(rows)
    if problems:
        print("\n[monotonicidade] PROBLEMAS DETECTADOS:")
        for pr in problems:
            print(f"  - {pr}")
    else:
        print("\n[monotonicidade] OK (custo maior -> final_equity menor ou igual).")

    params = {
        "entry_window": args.entry_window,
        "exit_window": args.exit_window,
        "short_window": args.short_window,
        "long_window": args.long_window,
        "capital": args.capital,
        "fracao": args.fracao,
        "alavancagem": args.alavancagem,
    }
    path = _dump_artifact(
        strategy_name=args.strategy,
        dataset_id=args.dataset_id,
        rows=rows,
        problems=problems,
        params=params,
    )
    print(f"\nartefato: {path}")
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
