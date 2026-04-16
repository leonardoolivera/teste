"""CLI fina do Alpha Forge. Sem lógica escondida; apenas orquestra.

Subcomandos:
  - ``run-demo`` — carrega o dataset sintético seminal, roda uma estratégia
    selecionada pela flag ``--strategy`` (default ``ma_crossover``,
    ADR-0008) sob um RiskBudget e um CostModel declarados pelas flags, e
    imprime o resultado resumido (fills, rejections, equity, métricas
    mínimas). A estratégia ``dummy`` segue disponível como ferramenta de
    sanidade estrutural.
"""

from __future__ import annotations

import argparse
from typing import Sequence

from alpha_forge.backtest.cost import CostModel
from alpha_forge.backtest.engine import StrategyProtocol, run_backtest
from alpha_forge.backtest.schemas import BacktestResult
from alpha_forge.data.loaders import load_dataset
from alpha_forge.risk.schemas import RiskBudget
from alpha_forge.strategies.families.dummy import DummyAlternatingStrategy
from alpha_forge.strategies.families.ma_crossover import MovingAverageCrossoverStrategy


DEMO_DATASET_ID = "synthetic_btcusdt_1h_seed42"
AVAILABLE_STRATEGIES = ("ma_crossover", "dummy")
DEFAULT_STRATEGY = "ma_crossover"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="alpha-forge")
    sub = parser.add_subparsers(dest="command")

    demo = sub.add_parser(
        "run-demo",
        help="Executa backtest mínimo sobre o dataset sintético seminal.",
    )
    demo.add_argument("--dataset-id", default=DEMO_DATASET_ID)
    demo.add_argument("--capital", type=float, default=10_000.0)
    demo.add_argument("--fracao", type=float, default=0.1)
    demo.add_argument("--alavancagem", type=float, default=2.0)
    demo.add_argument(
        "--taker-fee-bps",
        type=float,
        default=5.0,
        help="Fee base em basis points (5.0 = 0.05%%). Passe 0.0 para sem fee.",
    )
    demo.add_argument(
        "--slippage-bps-per-notional",
        type=float,
        default=2.0,
        help="Slippage em bps por unidade de (notional/capital_inicial).",
    )
    demo.add_argument(
        "--strategy",
        choices=AVAILABLE_STRATEGIES,
        default=DEFAULT_STRATEGY,
        help=(
            "Estratégia a executar. 'ma_crossover' é a primeira estratégia real "
            "(ADR-0008, long-only). 'dummy' permanece para sanidade estrutural."
        ),
    )
    demo.add_argument(
        "--short-window",
        type=int,
        default=20,
        help="Janela curta do MA crossover (ignorada por outras estratégias).",
    )
    demo.add_argument(
        "--long-window",
        type=int,
        default=50,
        help="Janela longa do MA crossover (ignorada por outras estratégias).",
    )

    return parser


def run(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "run-demo":
        return _cmd_run_demo(
            dataset_id=args.dataset_id,
            capital=args.capital,
            fracao=args.fracao,
            alavancagem=args.alavancagem,
            taker_fee_bps=args.taker_fee_bps,
            slippage_bps_per_notional=args.slippage_bps_per_notional,
            strategy_name=args.strategy,
            short_window=args.short_window,
            long_window=args.long_window,
        )

    parser.error(f"subcomando desconhecido: {args.command}")
    return 2


def _build_strategy(
    name: str, short_window: int, long_window: int
) -> StrategyProtocol:
    if name == "ma_crossover":
        return MovingAverageCrossoverStrategy(
            short_window=short_window, long_window=long_window
        )
    if name == "dummy":
        return DummyAlternatingStrategy()
    raise ValueError(f"estratégia desconhecida: {name}")


def _strategy_param_label(name: str, short_window: int, long_window: int) -> str:
    if name == "ma_crossover":
        return f"short={short_window} long={long_window}"
    return "(sem parâmetros)"


def _cmd_run_demo(
    *,
    dataset_id: str,
    capital: float,
    fracao: float,
    alavancagem: float,
    taker_fee_bps: float,
    slippage_bps_per_notional: float,
    strategy_name: str,
    short_window: int,
    long_window: int,
) -> int:
    budget = RiskBudget(
        capital_inicial=capital,
        fracao_por_trade=fracao,
        alavancagem_max=alavancagem,
    )
    cost_model = CostModel(
        taker_fee_bps=taker_fee_bps,
        slippage_bps_per_unit_notional=slippage_bps_per_notional,
    )
    prices = load_dataset(dataset_id)
    strategy = _build_strategy(strategy_name, short_window, long_window)
    result = run_backtest(
        prices=prices,
        strategy=strategy,
        budget=budget,
        cost_model=cost_model,
        dataset_id=dataset_id,
    )
    _print_summary(
        result,
        budget,
        cost_model,
        strategy_name=strategy_name,
        strategy_params=_strategy_param_label(strategy_name, short_window, long_window),
    )
    return 0


def _print_summary(
    result: BacktestResult,
    budget: RiskBudget,
    cost_model: CostModel,
    *,
    strategy_name: str,
    strategy_params: str,
) -> None:
    print(f"dataset          : {result.dataset_id}")
    print(f"strategy         : {strategy_name} {strategy_params}")
    print(f"barras           : {result.bars}")
    print(
        f"budget           : capital={budget.capital_inicial:.2f} "
        f"fracao={budget.fracao_por_trade:.3f} "
        f"alavancagem_max={budget.alavancagem_max:.2f}"
    )
    print(
        f"cost_model       : taker_fee_bps={cost_model.taker_fee_bps:.2f} "
        f"slippage_bps/notional={cost_model.slippage_bps_per_unit_notional:.2f}"
    )
    print(f"fills            : {len(result.fills)}")
    print(f"rejections       : {len(result.rejections)}")
    print(f"equity inicial   : {budget.capital_inicial:.2f}")
    print(f"equity final     : {result.final_equity:.2f}")
    print(f"equity max       : {result.max_equity:.2f}")
    print(f"equity min       : {result.min_equity:.2f}")
    if result.rejections:
        reasons: dict[str, int] = {}
        for r in result.rejections:
            reasons[r.reason.value] = reasons.get(r.reason.value, 0) + 1
        print(f"rejections_by    : {reasons}")

    m = result.metrics
    if m is not None:
        pnl_pct = (m.total_pnl / budget.capital_inicial) * 100 if budget.capital_inicial else 0.0
        hit = f"{m.hit_rate * 100:.2f}%" if m.hit_rate is not None else "N/A"
        print("--- metrics ---")
        print(f"total_pnl        : {m.total_pnl:+.2f} ({pnl_pct:+.2f}%)")
        print(f"trade_count      : {m.trade_count}")
        print(f"hit_rate         : {hit}")
        print(f"max_drawdown     : {m.max_drawdown * 100:.2f}%")


def main() -> int:
    return run()
