"""CLI fina do Alpha Forge. Sem lógica escondida; apenas orquestra.

Subcomandos:
  - ``run-demo`` — carrega o dataset sintético seminal, roda uma estratégia
    selecionada pela flag ``--strategy`` (default ``ma_crossover``,
    ADR-0008) sob um RiskBudget e um CostModel declarados pelas flags, e
    imprime o resultado resumido (fills, rejections, equity, métricas
    mínimas). A estratégia ``dummy`` segue disponível como ferramenta de
    sanidade estrutural.
  - ``validate`` — roda pipeline completo de `validation/` (walk-forward +
    Monte Carlo + cost stress) sobre dataset + estratégia declarados pelas
    flags e persiste os artefatos em ``results/validation/<run_id>/``
    (ADR-0016 + ADR-0017, consome ADR-0003 + ADR-0014 + ADR-0015).
  - ``compare`` — lê dois diretórios ``results/validation/<run_id>/`` via
    ``load_*`` e imprime diff humano por seção (run_metadata, walk_forward,
    monte_carlo, cost_stress). Orquestração pura, sem código de domínio
    (ADR-0018).
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime, timezone
from typing import Sequence

import alpha_forge
from alpha_forge.backtest.cost import CostModel
from alpha_forge.backtest.engine import StrategyProtocol, run_backtest
from alpha_forge.backtest.schemas import BacktestMetrics, BacktestResult, Trade
from alpha_forge.data.loaders import DatasetIntegrityError, load_dataset
from alpha_forge.io.paths import validation_run_dir
from alpha_forge.regimes import RegimeFilter, canonical_string, parse_spec
from alpha_forge.risk.schemas import RiskBudget, SizingMode
from alpha_forge.strategies.families.bollinger import BollingerMeanReversionStrategy
from alpha_forge.strategies.families.composite import CompositeBBRSIStrategy
from alpha_forge.strategies.families.donchian import DonchianBreakoutStrategy
from alpha_forge.strategies.families.keltner import KeltnerMeanReversionStrategy
from alpha_forge.strategies.families.supertrend import SuperTrendStrategy
from alpha_forge.strategies.families.liquidity_trap import LiquidityTrapStrategy
from alpha_forge.strategies.families.zscore import ZScoreMeanReversionStrategy
from alpha_forge.strategies.families.dummy import DummyAlternatingStrategy
from alpha_forge.strategies.families.ma_crossover import MovingAverageCrossoverStrategy
from alpha_forge.strategies.families.rsi import RSIMeanReversionStrategy
from alpha_forge.ranking import (
    RankingError,
    discover_slugs,
    load_weights_toml,
    rank_pilots,
    save_leaderboard,
)
from alpha_forge.validation import (
    CostPerturbation,
    CostStressReport,
    MonteCarloSummary,
    RunMetadata,
    ValidationError,
    WalkForwardFold,
    cost_stress,
    load_cost_stress_report,
    load_monte_carlo_summary,
    load_run_metadata,
    load_walk_forward_folds,
    monte_carlo_trades,
    save_cost_stress_report,
    save_monte_carlo_summary,
    save_run_metadata,
    save_walk_forward_folds,
    walk_forward,
)


DEMO_DATASET_ID = "synthetic_btcusdt_1h_seed42"
AVAILABLE_STRATEGIES = ("ma_crossover", "dummy", "donchian", "bollinger", "rsi", "keltner", "zscore", "composite_bb_rsi", "supertrend", "liquidity_trap")
DEFAULT_STRATEGY = "ma_crossover"
LOG_LEVELS = ("silent", "info", "debug")
DEFAULT_LOG_LEVEL = "silent"
WALK_FORWARD_SCHEMES = ("rolling", "expanding")


def _configure_logging(level: str) -> None:
    if level == "silent":
        return
    py_level = logging.DEBUG if level == "debug" else logging.INFO
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(levelname)s %(name)s %(message)s"))
    log = logging.getLogger("alpha_forge")
    log.setLevel(py_level)
    if not any(isinstance(h, logging.StreamHandler) for h in log.handlers):
        log.addHandler(handler)
    log.propagate = False


def _add_shared_dataset_and_risk_flags(p: argparse.ArgumentParser) -> None:
    p.add_argument("--dataset-id", default=DEMO_DATASET_ID)
    p.add_argument("--capital", type=float, default=10_000.0)
    p.add_argument("--fracao", type=float, default=0.1)
    p.add_argument("--alavancagem", type=float, default=2.0)
    p.add_argument(
        "--sizing-mode",
        choices=["fixed_notional", "snowball", "pyramid_equity"],
        default="fixed_notional",
        help=(
            "ADR-0063/0180: fixed_notional (default) usa capital_inicial estatico; "
            "snowball capitaliza PnL realizado; pyramid_equity abre stack de tranches "
            "dimensionadas por equity mark-to-market (requer --pyramid-* flags)."
        ),
    )
    p.add_argument(
        "--pyramid-max-tranches",
        type=int,
        default=None,
        help="ADR-0180: maximo de tranches simultaneas em pyramid mode (1-10).",
    )
    p.add_argument(
        "--pyramid-tranche-equity-frac",
        type=float,
        default=None,
        help="ADR-0180: fracao do equity mark-to-market por tranche (0,1].",
    )
    p.add_argument(
        "--pyramid-rearm-cooldown-bars",
        type=int,
        default=None,
        help="ADR-0180: barras LTF de cooldown apos full exit antes de novo ENTER.",
    )
    p.add_argument(
        "--taker-fee-bps",
        type=float,
        default=5.0,
        help="Fee base em basis points (5.0 = 0.05%%). Passe 0.0 para sem fee.",
    )
    p.add_argument(
        "--slippage-bps-per-notional",
        type=float,
        default=2.0,
        help="Slippage em bps por unidade de (notional/capital_inicial).",
    )
    p.add_argument(
        "--spread-bps",
        type=float,
        default=0.0,
        help=(
            "Spread estrutural em bps aplicado contra o trader em cada fill "
            "(ADR-0019). Default 0.0 preserva comportamento ADR-0006."
        ),
    )


def _add_shared_strategy_flags(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--strategy",
        choices=AVAILABLE_STRATEGIES,
        default=DEFAULT_STRATEGY,
        help=(
            "Estratégia a executar. 'ma_crossover' (ADR-0008, default, long-only). "
            "'donchian' (ADR-0011, breakout long-only). "
            "'bollinger' (ADR-0026, mean-reversion long-only). "
            "'rsi' (ADR-0027, RSI mean-reversion long-only). "
            "'keltner' (ADR-0170, ATR envelope mean-reversion). "
            "'zscore' (ADR-0175, z-score mean-reversion com exit zero-crossing). "
            "'dummy' permanece para sanidade estrutural."
        ),
    )
    p.add_argument(
        "--short-window",
        type=int,
        default=20,
        help="Janela curta do MA crossover (usada só com --strategy ma_crossover).",
    )
    p.add_argument(
        "--long-window",
        type=int,
        default=50,
        help="Janela longa do MA crossover (usada só com --strategy ma_crossover).",
    )
    p.add_argument(
        "--long-only",
        action=argparse.BooleanOptionalAction,
        default=True,
        help=(
            "Controla direcionalidade (ADR-0012 ma_crossover, ADR-0013 donchian, ADR-0051 bollinger/rsi). "
            "--long-only (default): comportamento preservado. "
            "--no-long-only: sinal bearish/overbought emite ENTER_SHORT; "
            "reversões tratadas pelo engine (custo duplo no tick). "
            "Afeta --strategy {ma_crossover, donchian, bollinger, rsi}; ignorado em dummy."
        ),
    )
    p.add_argument(
        "--entry-window",
        type=int,
        default=20,
        help="Janela de entrada do Donchian breakout (usada só com --strategy donchian).",
    )
    p.add_argument(
        "--exit-window",
        type=int,
        default=10,
        help="Janela de saída do Donchian breakout (usada só com --strategy donchian).",
    )
    p.add_argument(
        "--bollinger-window",
        type=int,
        default=20,
        help="Janela da média móvel Bollinger (usada só com --strategy bollinger). ADR-0026.",
    )
    p.add_argument(
        "--bollinger-num-std",
        type=float,
        default=2.0,
        help=(
            "Número de desvios-padrão para a banda Bollinger "
            "(usada só com --strategy bollinger). ADR-0026."
        ),
    )
    p.add_argument(
        "--rsi-period",
        type=int,
        default=14,
        help="Período do RSI (usado só com --strategy rsi). ADR-0027.",
    )
    p.add_argument(
        "--rsi-oversold",
        type=float,
        default=30.0,
        help=(
            "Limiar de sobrevenda para entrada long (0 < oversold < 50). "
            "Usado só com --strategy rsi. ADR-0027."
        ),
    )
    p.add_argument(
        "--rsi-overbought",
        type=float,
        default=70.0,
        help=(
            "Limiar de sobrecompra (50 < overbought < 100). "
            "Usado só com --strategy rsi. ADR-0027."
        ),
    )
    p.add_argument(
        "--keltner-window",
        type=int,
        default=20,
        help="Span da EMA do Keltner (usado só com --strategy keltner). ADR-0170.",
    )
    p.add_argument(
        "--keltner-atr-period",
        type=int,
        default=14,
        help="Período do ATR no Keltner (usado só com --strategy keltner). ADR-0170.",
    )
    p.add_argument(
        "--keltner-mult",
        type=float,
        default=2.0,
        help=(
            "Multiplicador do ATR para largura do envelope Keltner "
            "(usado só com --strategy keltner). ADR-0170."
        ),
    )
    p.add_argument(
        "--zscore-window",
        type=int,
        default=20,
        help="Janela do z-score (usado só com --strategy zscore). ADR-0175.",
    )
    p.add_argument(
        "--zscore-threshold",
        type=float,
        default=2.0,
        help=(
            "Threshold em desvios-padrão para entry long/short zscore "
            "(usado só com --strategy zscore). ADR-0175."
        ),
    )
    p.add_argument(
        "--composite-bb-window",
        type=int,
        default=20,
        help="ADR-0189: janela BB do composite_bb_rsi.",
    )
    p.add_argument(
        "--composite-bb-num-std",
        type=float,
        default=2.0,
        help="ADR-0189: num_std BB do composite_bb_rsi.",
    )
    p.add_argument(
        "--composite-rsi-period",
        type=int,
        default=14,
        help="ADR-0189: period RSI do composite_bb_rsi.",
    )
    p.add_argument(
        "--composite-rsi-oversold",
        type=float,
        default=30.0,
        help="ADR-0189: oversold RSI do composite_bb_rsi.",
    )
    p.add_argument(
        "--composite-rsi-overbought",
        type=float,
        default=70.0,
        help="ADR-0189: overbought RSI do composite_bb_rsi.",
    )
    p.add_argument(
        "--supertrend-atr-period",
        type=int,
        default=10,
        help="ADR-0193: período ATR do supertrend (usado só com --strategy supertrend).",
    )
    p.add_argument(
        "--supertrend-atr-mult",
        type=float,
        default=3.0,
        help="ADR-0193: multiplicador ATR do supertrend (usado só com --strategy supertrend).",
    )
    p.add_argument(
        "--lq-lookback",
        type=int,
        default=20,
        help="ADR-0231 V2/RAIO Cycle 16: lookback bars para prev high/low (liquidity_trap).",
    )
    p.add_argument(
        "--lq-exit-mean-window",
        type=int,
        default=10,
        help="ADR-0231: SMA mid window para exit signal proxy VWAP (liquidity_trap).",
    )
    p.add_argument(
        "--time-stop-bars",
        type=int,
        default=0,
        help=(
            "ADR-0226 V2/RAIO Cycle 11: time-stop wrapper sobre qualquer strategy. "
            "Se > 0, força EXIT após N bars-in-position. 0 (default) desativa. "
            "Aplica-se acima do exit nativo da estratégia."
        ),
    )
    p.add_argument(
        "--atr-trail-period",
        type=int,
        default=0,
        help=(
            "ADR-0227 V2/RAIO Cycle 12: ATR trailing stop period (Wilder TR mean). "
            "Se > 0 E --atr-trail-mult > 0, ativa ATRTrailingWrapper. "
            "0 (default) desativa."
        ),
    )
    p.add_argument(
        "--atr-trail-mult",
        type=float,
        default=0.0,
        help=(
            "ADR-0227 V2/RAIO Cycle 12: ATR trailing stop multiplier. "
            "Se > 0 E --atr-trail-period > 0, ativa ATRTrailingWrapper. "
            "0 (default) desativa."
        ),
    )
    p.add_argument(
        "--be-atr-period",
        type=int,
        default=0,
        help=(
            "ADR-0229 V2/RAIO Cycle 14: período ATR do BEAfterMFEWrapper. "
            "Se > 0 E --be-mfe-trigger-atr > 0, ativa break-even após MFE atingir limiar. "
            "0 (default) desativa."
        ),
    )
    p.add_argument(
        "--be-mfe-trigger-atr",
        type=float,
        default=0.0,
        help=(
            "ADR-0229 V2/RAIO Cycle 14: MFE trigger em ATR units para arm break-even. "
            "Se > 0 E --be-atr-period > 0, ativa BEAfterMFEWrapper. "
            "0 (default) desativa."
        ),
    )


def _add_shared_log_level_flag(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--log-level",
        choices=LOG_LEVELS,
        default=DEFAULT_LOG_LEVEL,
        help=(
            "Observabilidade do engine. 'silent' (default): nenhum log. "
            "'info': start/end do backtest (uma linha cada). "
            "'debug': inclui fill.open/fill.close/rejection/reverse_on_signal "
            "por evento. Stream = stderr, não altera stdout do summary."
        ),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="alpha-forge")
    sub = parser.add_subparsers(dest="command")

    demo = sub.add_parser(
        "run-demo",
        help="Executa backtest mínimo sobre o dataset sintético seminal.",
    )
    _add_shared_dataset_and_risk_flags(demo)
    _add_shared_strategy_flags(demo)
    _add_shared_log_level_flag(demo)

    validate = sub.add_parser(
        "validate",
        help=(
            "Roda pipeline completo de validation/ (walk-forward + Monte Carlo "
            "+ cost stress) e persiste em results/validation/<run_id>/ (ADR-0016)."
        ),
    )
    validate.add_argument(
        "--run-id",
        required=True,
        help=(
            "Identificador opaco da corrida. Diretório "
            "results/validation/<run_id>/ é criado/sobrescrito. Convenção fica "
            "por conta do chamador (ADR-0015 §'Layout')."
        ),
    )
    _add_shared_dataset_and_risk_flags(validate)
    _add_shared_strategy_flags(validate)
    validate.add_argument(
        "--n-folds",
        type=int,
        default=5,
        help="Número de folds do walk-forward (ADR-0003). Default 5.",
    )
    validate.add_argument(
        "--scheme",
        choices=WALK_FORWARD_SCHEMES,
        default="rolling",
        help="Esquema do walk-forward: 'rolling' (default) ou 'expanding'.",
    )
    validate.add_argument(
        "--train-fraction",
        type=float,
        default=0.5,
        help="Fração do tamanho do test_window usada como train em scheme=rolling.",
    )
    validate.add_argument(
        "--min-test-bars",
        type=int,
        default=50,
        help="Mínimo de barras por test_window; folds menores disparam erro.",
    )
    validate.add_argument(
        "--mc-resamples",
        type=int,
        default=1000,
        help="Número de resamples do Monte Carlo sobre trades (ADR-0003). Default 1000.",
    )
    validate.add_argument(
        "--mc-seed",
        type=int,
        default=42,
        help="Semente do Monte Carlo. Reprodutibilidade é contrato (ADR-0003).",
    )
    validate.add_argument(
        "--stress",
        action="append",
        default=[],
        metavar="LABEL:FEE_DELTA_BPS:SLIP_DELTA_BPS[:SPREAD_DELTA_BPS]",
        help=(
            "Perturbação de custo para o cost_stress (ADR-0014/ADR-0019). "
            "Repetível. Formato: 'label:fee_delta_bps:slip_delta_bps' "
            "(3 partes) OU 'label:fee_delta_bps:slip_delta_bps:spread_delta_bps' "
            "(4 partes, ADR-0019). Labels únicos; valores não-negativos; pelo "
            "menos um strictly > 0 por perturbação. Ex: --stress fee+10:10:0 "
            "ou --stress spread+5:0:0:5"
        ),
    )
    validate.add_argument(
        "--skip-monte-carlo",
        action="store_true",
        help="Não roda Monte Carlo; monte_carlo.json não é gravado.",
    )
    validate.add_argument(
        "--skip-cost-stress",
        action="store_true",
        help="Não roda cost_stress; cost_stress.json não é gravado. Ignora --stress.",
    )
    validate.add_argument(
        "--regime-filter",
        default="none",
        metavar="SPEC",
        help=(
            "Filtro de regime causal aplicado antes de Strategy.decide (ADR-0022). "
            "Formato 'name:k=v:k=v'. 'none' (default) desativa. "
            "Exemplo: --regime-filter sma_slope:window=50:min_slope_bps=10"
        ),
    )
    _add_shared_log_level_flag(validate)

    compare = sub.add_parser(
        "compare",
        help=(
            "Compara duas corridas de `validate`, imprimindo diff humano por "
            "seção (run_metadata, walk_forward, monte_carlo, cost_stress). "
            "Orquestração pura sobre load_* (ADR-0018)."
        ),
    )
    compare.add_argument(
        "run_id_a",
        help="Identificador da primeira corrida (ADR-0015/0017).",
    )
    compare.add_argument(
        "run_id_b",
        help="Identificador da segunda corrida.",
    )
    compare.add_argument(
        "--skip-run-metadata",
        action="store_true",
        help="Pula a seção run_metadata mesmo que ambos run.json existam.",
    )
    compare.add_argument(
        "--skip-walk-forward",
        action="store_true",
        help="Pula a seção walk_forward.",
    )
    compare.add_argument(
        "--skip-monte-carlo",
        action="store_true",
        help="Pula a seção monte_carlo.",
    )
    compare.add_argument(
        "--skip-cost-stress",
        action="store_true",
        help="Pula a seção cost_stress.",
    )
    _add_shared_log_level_flag(compare)

    rank = sub.add_parser(
        "rank",
        help=(
            "Ordena pilotos validados por composite score (ADR-0024). "
            "Read-only sobre results/validation/<slug>/."
        ),
    )
    rank.add_argument(
        "--runs-dir",
        default="results/validation",
        help="Diretório raiz dos pilotos validados. Default results/validation.",
    )
    rank.add_argument(
        "--slug",
        action="append",
        default=[],
        dest="slugs",
        help=(
            "Slug específico (repetível). Se omitido, auto-discovery sobre --runs-dir. "
            "Combinar --slug e auto-discovery: --slug restringe."
        ),
    )
    rank.add_argument(
        "--weights-file",
        default=None,
        help="Arquivo TOML com [weights]. Default: DEFAULT_WEIGHTS (ADR-0024).",
    )
    rank.add_argument(
        "--eligibility",
        default="all",
        help=(
            "Filtro declarativo. v1: 'all' ou \"release_decision (==|!=) "
            "'fail|paper_only|canary_only'\". Default 'all'."
        ),
    )
    rank.add_argument(
        "--agentic-dir",
        default=None,
        help=(
            "Diretório onde estão os AUDIT.md para parse de release_decision. "
            "Default: <runs-dir>/../../agentic/active."
        ),
    )
    rank.add_argument(
        "--output",
        default=None,
        help=(
            "Caminho para escrever o leaderboard JSON. Default: "
            "results/ranking/<YYYYMMDDTHHMMSSZ>.json."
        ),
    )
    rank.add_argument(
        "--format",
        choices=("json", "table"),
        default="json",
        help="Formato de saída em stdout. Default json.",
    )
    _add_shared_log_level_flag(rank)

    return parser


def run(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "run-demo":
        _configure_logging(args.log_level)
        return _cmd_run_demo(
            dataset_id=args.dataset_id,
            capital=args.capital,
            fracao=args.fracao,
            alavancagem=args.alavancagem,
            sizing_mode=args.sizing_mode,
            pyramid_max_tranches=args.pyramid_max_tranches,
            pyramid_tranche_equity_frac=args.pyramid_tranche_equity_frac,
            pyramid_rearm_cooldown_bars=args.pyramid_rearm_cooldown_bars,
            taker_fee_bps=args.taker_fee_bps,
            slippage_bps_per_notional=args.slippage_bps_per_notional,
            spread_bps=args.spread_bps,
            strategy_name=args.strategy,
            short_window=args.short_window,
            long_window=args.long_window,
            long_only=args.long_only,
            entry_window=args.entry_window,
            exit_window=args.exit_window,
            bollinger_window=args.bollinger_window,
            bollinger_num_std=args.bollinger_num_std,
            rsi_period=args.rsi_period,
            rsi_oversold=args.rsi_oversold,
            rsi_overbought=args.rsi_overbought,
            keltner_window=args.keltner_window,
            keltner_atr_period=args.keltner_atr_period,
            keltner_mult=args.keltner_mult,
            zscore_window=args.zscore_window,
            zscore_threshold=args.zscore_threshold,
            composite_bb_window=args.composite_bb_window,
            composite_bb_num_std=args.composite_bb_num_std,
            composite_rsi_period=args.composite_rsi_period,
            composite_rsi_oversold=args.composite_rsi_oversold,
            composite_rsi_overbought=args.composite_rsi_overbought,
        )

    if args.command == "validate":
        _configure_logging(args.log_level)
        try:
            perturbations = parse_stress_specs(args.stress)
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        try:
            regime_filter = parse_spec(args.regime_filter)
        except ValueError as exc:
            parser.error(str(exc))
            return 2
        flags = _flags_from_namespace(args)
        # Canonicalize --regime-filter in flags so run.json carries the
        # parsed form ("sma_slope:min_slope_bps=10:window=50"), not the raw
        # CLI string, satisfying ADR-0022 persistence contract.
        flags["regime_filter"] = canonical_string(regime_filter)
        try:
            return _cmd_validate(
                run_id=args.run_id,
                dataset_id=args.dataset_id,
                capital=args.capital,
                fracao=args.fracao,
                alavancagem=args.alavancagem,
                sizing_mode=args.sizing_mode,
                pyramid_max_tranches=args.pyramid_max_tranches,
                pyramid_tranche_equity_frac=args.pyramid_tranche_equity_frac,
                pyramid_rearm_cooldown_bars=args.pyramid_rearm_cooldown_bars,
                taker_fee_bps=args.taker_fee_bps,
                slippage_bps_per_notional=args.slippage_bps_per_notional,
                spread_bps=args.spread_bps,
                strategy_name=args.strategy,
                short_window=args.short_window,
                long_window=args.long_window,
                long_only=args.long_only,
                entry_window=args.entry_window,
                exit_window=args.exit_window,
                bollinger_window=args.bollinger_window,
                bollinger_num_std=args.bollinger_num_std,
                rsi_period=args.rsi_period,
                rsi_oversold=args.rsi_oversold,
                rsi_overbought=args.rsi_overbought,
                keltner_window=args.keltner_window,
                keltner_atr_period=args.keltner_atr_period,
                keltner_mult=args.keltner_mult,
                zscore_window=args.zscore_window,
                zscore_threshold=args.zscore_threshold,
                composite_bb_window=args.composite_bb_window,
                composite_bb_num_std=args.composite_bb_num_std,
                composite_rsi_period=args.composite_rsi_period,
                composite_rsi_oversold=args.composite_rsi_oversold,
                composite_rsi_overbought=args.composite_rsi_overbought,
                supertrend_atr_period=args.supertrend_atr_period,
                supertrend_atr_mult=args.supertrend_atr_mult,
                lq_lookback=args.lq_lookback,
                lq_exit_mean_window=args.lq_exit_mean_window,
                time_stop_bars=args.time_stop_bars,
                atr_trail_period=args.atr_trail_period,
                atr_trail_mult=args.atr_trail_mult,
                be_atr_period=args.be_atr_period,
                be_mfe_trigger_atr=args.be_mfe_trigger_atr,
                n_folds=args.n_folds,
                scheme=args.scheme,
                train_fraction=args.train_fraction,
                min_test_bars=args.min_test_bars,
                mc_resamples=args.mc_resamples,
                mc_seed=args.mc_seed,
                perturbations=perturbations,
                skip_monte_carlo=args.skip_monte_carlo,
                skip_cost_stress=args.skip_cost_stress,
                regime_filter=regime_filter,
                flags=flags,
            )
        except (ValidationError, DatasetIntegrityError) as exc:
            print(f"erro: {exc}", file=sys.stderr)
            return 1

    if args.command == "compare":
        _configure_logging(args.log_level)
        try:
            return _cmd_compare(
                run_id_a=args.run_id_a,
                run_id_b=args.run_id_b,
                skip_run_metadata=args.skip_run_metadata,
                skip_walk_forward=args.skip_walk_forward,
                skip_monte_carlo=args.skip_monte_carlo,
                skip_cost_stress=args.skip_cost_stress,
            )
        except (ValidationError, FileNotFoundError) as exc:
            print(f"erro: {exc}", file=sys.stderr)
            return 1

    if args.command == "rank":
        _configure_logging(args.log_level)
        try:
            return _cmd_rank(
                runs_dir=args.runs_dir,
                slugs=args.slugs,
                weights_file=args.weights_file,
                eligibility=args.eligibility,
                agentic_dir=args.agentic_dir,
                output=args.output,
                output_format=args.format,
            )
        except RankingError as exc:
            print(f"erro: {exc}", file=sys.stderr)
            return 1

    parser.error(f"subcomando desconhecido: {args.command}")
    return 2


def _flags_from_namespace(ns: argparse.Namespace) -> dict[str, str]:
    """Coage Namespace → dict[str, str] para persistência em `run.json` (ADR-0017).

    `command` é descartado — vai em campo próprio da `RunMetadata`. Listas (ex.
    `--stress`) são serializadas via `repr` para manter as 3 partes visíveis.
    """
    out: dict[str, str] = {}
    for key, value in vars(ns).items():
        if key == "command":
            continue
        if isinstance(value, list):
            out[key] = repr(value)
        else:
            out[key] = str(value)
    return out


def parse_stress_specs(specs: Sequence[str]) -> list[CostPerturbation]:
    """Parseia specs 'label:fee:slip' (3 partes) ou 'label:fee:slip:spread' (4).

    ADR-0016 aceita 3 partes; ADR-0019 estende para 4 partes com
    `spread_delta_bps`. Formatos com 2 ou menos, ou 5+ partes, são rejeitados.
    Label não pode ser vazio; valores devem ser floats parseáveis e >= 0;
    labels duplicados dentro da lista rejeitam. Construção de `CostPerturbation`
    herda validação pydantic (fee_delta >= 0, slip_delta >= 0, spread_delta >= 0).

    Devolve lista vazia se `specs` for vazio — a CLI trata isso como
    "pular cost_stress".
    """
    out: list[CostPerturbation] = []
    seen: set[str] = set()
    for raw in specs:
        parts = raw.split(":")
        if len(parts) not in (3, 4):
            raise ValueError(
                f"--stress inválido {raw!r}: esperado "
                "'label:fee_delta_bps:slip_delta_bps' (3 partes) ou "
                "'label:fee_delta_bps:slip_delta_bps:spread_delta_bps' (4 partes)"
            )
        label = parts[0]
        fee_s = parts[1]
        slip_s = parts[2]
        spread_s = parts[3] if len(parts) == 4 else "0"
        if not label:
            raise ValueError(f"--stress inválido {raw!r}: label vazio")
        try:
            fee = float(fee_s)
            slip = float(slip_s)
            spread = float(spread_s)
        except ValueError as exc:
            raise ValueError(
                f"--stress inválido {raw!r}: fee_delta_bps, slip_delta_bps e "
                "spread_delta_bps devem ser números"
            ) from exc
        if label in seen:
            raise ValueError(f"--stress inválido: label duplicado {label!r}")
        seen.add(label)
        out.append(
            CostPerturbation(
                label=label,
                fee_delta_bps=fee,
                slip_delta_bps=slip,
                spread_delta_bps=spread,
            )
        )
    return out


def _build_strategy(
    name: str,
    *,
    short_window: int,
    long_window: int,
    long_only: bool,
    entry_window: int,
    exit_window: int,
    bollinger_window: int,
    bollinger_num_std: float,
    rsi_period: int,
    rsi_oversold: float,
    rsi_overbought: float,
    keltner_window: int,
    keltner_atr_period: int,
    keltner_mult: float,
    zscore_window: int,
    zscore_threshold: float,
    composite_bb_window: int = 20,
    composite_bb_num_std: float = 2.0,
    composite_rsi_period: int = 14,
    composite_rsi_oversold: float = 30.0,
    composite_rsi_overbought: float = 70.0,
    supertrend_atr_period: int = 10,
    supertrend_atr_mult: float = 3.0,
    lq_lookback: int = 20,
    lq_exit_mean_window: int = 10,
    time_stop_bars: int = 0,
    atr_trail_period: int = 0,
    atr_trail_mult: float = 0.0,
    be_atr_period: int = 0,
    be_mfe_trigger_atr: float = 0.0,
) -> StrategyProtocol:
    base = _build_strategy_base(
        name,
        short_window=short_window,
        long_window=long_window,
        long_only=long_only,
        entry_window=entry_window,
        exit_window=exit_window,
        bollinger_window=bollinger_window,
        bollinger_num_std=bollinger_num_std,
        rsi_period=rsi_period,
        rsi_oversold=rsi_oversold,
        rsi_overbought=rsi_overbought,
        keltner_window=keltner_window,
        keltner_atr_period=keltner_atr_period,
        keltner_mult=keltner_mult,
        zscore_window=zscore_window,
        zscore_threshold=zscore_threshold,
        composite_bb_window=composite_bb_window,
        composite_bb_num_std=composite_bb_num_std,
        composite_rsi_period=composite_rsi_period,
        composite_rsi_oversold=composite_rsi_oversold,
        composite_rsi_overbought=composite_rsi_overbought,
        supertrend_atr_period=supertrend_atr_period,
        supertrend_atr_mult=supertrend_atr_mult,
        lq_lookback=lq_lookback,
        lq_exit_mean_window=lq_exit_mean_window,
    )
    if time_stop_bars > 0:
        from alpha_forge.strategies.exit_layer import TimeStopWrapper
        base = TimeStopWrapper(base, max_bars_in_position=time_stop_bars)
    if atr_trail_period > 0 and atr_trail_mult > 0:
        from alpha_forge.strategies.exit_layer import ATRTrailingWrapper
        base = ATRTrailingWrapper(base, atr_period=atr_trail_period, atr_mult=atr_trail_mult)
    if be_atr_period > 0 and be_mfe_trigger_atr > 0:
        from alpha_forge.strategies.exit_layer import BEAfterMFEWrapper
        base = BEAfterMFEWrapper(base, atr_period=be_atr_period, mfe_trigger_atr=be_mfe_trigger_atr)
    return base


def _build_strategy_base(
    name: str,
    *,
    short_window: int,
    long_window: int,
    long_only: bool,
    entry_window: int,
    exit_window: int,
    bollinger_window: int,
    bollinger_num_std: float,
    rsi_period: int,
    rsi_oversold: float,
    rsi_overbought: float,
    keltner_window: int,
    keltner_atr_period: int,
    keltner_mult: float,
    zscore_window: int,
    zscore_threshold: float,
    composite_bb_window: int = 20,
    composite_bb_num_std: float = 2.0,
    composite_rsi_period: int = 14,
    composite_rsi_oversold: float = 30.0,
    composite_rsi_overbought: float = 70.0,
    supertrend_atr_period: int = 10,
    supertrend_atr_mult: float = 3.0,
    lq_lookback: int = 20,
    lq_exit_mean_window: int = 10,
) -> StrategyProtocol:
    if name == "ma_crossover":
        return MovingAverageCrossoverStrategy(
            short_window=short_window,
            long_window=long_window,
            long_only=long_only,
        )
    if name == "donchian":
        return DonchianBreakoutStrategy(
            entry_window=entry_window,
            exit_window=exit_window,
            long_only=long_only,
        )
    if name == "bollinger":
        return BollingerMeanReversionStrategy(
            window=bollinger_window,
            num_std=bollinger_num_std,
            long_only=long_only,
        )
    if name == "rsi":
        return RSIMeanReversionStrategy(
            period=rsi_period,
            oversold=rsi_oversold,
            overbought=rsi_overbought,
            long_only=long_only,
        )
    if name == "keltner":
        return KeltnerMeanReversionStrategy(
            window=keltner_window,
            atr_period=keltner_atr_period,
            atr_mult=keltner_mult,
            long_only=long_only,
        )
    if name == "zscore":
        return ZScoreMeanReversionStrategy(
            window=zscore_window,
            threshold=zscore_threshold,
            long_only=long_only,
        )
    if name == "composite_bb_rsi":
        return CompositeBBRSIStrategy(
            bb_window=composite_bb_window,
            bb_num_std=composite_bb_num_std,
            rsi_period=composite_rsi_period,
            rsi_oversold=composite_rsi_oversold,
            rsi_overbought=composite_rsi_overbought,
            long_only=long_only,
        )
    if name == "supertrend":
        return SuperTrendStrategy(
            atr_period=supertrend_atr_period,
            atr_mult=supertrend_atr_mult,
            long_only=long_only,
        )
    if name == "dummy":
        return DummyAlternatingStrategy()
    if name == "liquidity_trap":
        return LiquidityTrapStrategy(
            lookback=lq_lookback,
            exit_mean_window=lq_exit_mean_window,
            long_only=long_only,
        )
    raise ValueError(f"estratégia desconhecida: {name}")


def _strategy_param_label(
    name: str,
    *,
    short_window: int,
    long_window: int,
    long_only: bool,
    entry_window: int,
    exit_window: int,
    bollinger_window: int,
    bollinger_num_std: float,
    rsi_period: int,
    rsi_oversold: float,
    rsi_overbought: float,
    keltner_window: int,
    keltner_atr_period: int,
    keltner_mult: float,
    zscore_window: int,
    zscore_threshold: float,
    composite_bb_window: int = 20,
    composite_bb_num_std: float = 2.0,
    composite_rsi_period: int = 14,
    composite_rsi_oversold: float = 30.0,
    composite_rsi_overbought: float = 70.0,
    supertrend_atr_period: int = 10,
    supertrend_atr_mult: float = 3.0,
) -> str:
    if name == "ma_crossover":
        return f"short={short_window} long={long_window} long_only={long_only}"
    if name == "donchian":
        return f"entry={entry_window} exit={exit_window} long_only={long_only}"
    if name == "bollinger":
        return (
            f"window={bollinger_window} num_std={bollinger_num_std:.2f} "
            f"long_only={long_only}"
        )
    if name == "rsi":
        return (
            f"period={rsi_period} oversold={rsi_oversold:.2f} "
            f"overbought={rsi_overbought:.2f} long_only={long_only}"
        )
    if name == "keltner":
        return (
            f"window={keltner_window} atr_period={keltner_atr_period} "
            f"atr_mult={keltner_mult:.2f} long_only={long_only}"
        )
    if name == "zscore":
        return (
            f"window={zscore_window} threshold={zscore_threshold:.2f} "
            f"long_only={long_only}"
        )
    if name == "composite_bb_rsi":
        return (
            f"bb_w={composite_bb_window} bb_ns={composite_bb_num_std:.2f} "
            f"rsi_p={composite_rsi_period} os={composite_rsi_oversold:.1f} "
            f"ob={composite_rsi_overbought:.1f} long_only={long_only}"
        )
    if name == "supertrend":
        return (
            f"atr_period={supertrend_atr_period} "
            f"atr_mult={supertrend_atr_mult:.2f} long_only={long_only}"
        )
    return "(sem parâmetros)"


def _cmd_run_demo(
    *,
    dataset_id: str,
    capital: float,
    fracao: float,
    alavancagem: float,
    sizing_mode: str,
    pyramid_max_tranches: int | None,
    pyramid_tranche_equity_frac: float | None,
    pyramid_rearm_cooldown_bars: int | None,
    taker_fee_bps: float,
    slippage_bps_per_notional: float,
    spread_bps: float,
    strategy_name: str,
    short_window: int,
    long_window: int,
    long_only: bool,
    entry_window: int,
    exit_window: int,
    bollinger_window: int,
    bollinger_num_std: float,
    rsi_period: int,
    rsi_oversold: float,
    rsi_overbought: float,
    keltner_window: int,
    keltner_atr_period: int,
    keltner_mult: float,
    zscore_window: int,
    zscore_threshold: float,
) -> int:
    budget = RiskBudget(
        capital_inicial=capital,
        fracao_por_trade=fracao,
        alavancagem_max=alavancagem,
        sizing_mode=SizingMode(sizing_mode),
        pyramid_max_tranches=pyramid_max_tranches,
        pyramid_tranche_equity_fraction=pyramid_tranche_equity_frac,
        pyramid_rearm_cooldown_bars=pyramid_rearm_cooldown_bars,
    )
    cost_model = CostModel(
        taker_fee_bps=taker_fee_bps,
        slippage_bps_per_unit_notional=slippage_bps_per_notional,
        spread_bps=spread_bps,
    )
    prices = load_dataset(dataset_id)
    strategy = _build_strategy(
        strategy_name,
        short_window=short_window,
        long_window=long_window,
        long_only=long_only,
        entry_window=entry_window,
        exit_window=exit_window,
        bollinger_window=bollinger_window,
        bollinger_num_std=bollinger_num_std,
        rsi_period=rsi_period,
        rsi_oversold=rsi_oversold,
        rsi_overbought=rsi_overbought,
        keltner_window=keltner_window,
        keltner_atr_period=keltner_atr_period,
        keltner_mult=keltner_mult,
        zscore_window=zscore_window,
        zscore_threshold=zscore_threshold,
    )
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
        strategy_params=_strategy_param_label(
            strategy_name,
            short_window=short_window,
            long_window=long_window,
            long_only=long_only,
            entry_window=entry_window,
            exit_window=exit_window,
            bollinger_window=bollinger_window,
            bollinger_num_std=bollinger_num_std,
            rsi_period=rsi_period,
            rsi_oversold=rsi_oversold,
            rsi_overbought=rsi_overbought,
            keltner_window=keltner_window,
            keltner_atr_period=keltner_atr_period,
            keltner_mult=keltner_mult,
            zscore_window=zscore_window,
            zscore_threshold=zscore_threshold,
        ),
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
        f"slippage_bps/notional={cost_model.slippage_bps_per_unit_notional:.2f} "
        f"spread_bps={cost_model.spread_bps:.2f}"
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


def _now_utc() -> datetime:
    """Seam de timestamp: facil de monkeypatch em testes (ADR-0017)."""
    return datetime.now(timezone.utc)


def _cmd_validate(
    *,
    run_id: str,
    dataset_id: str,
    capital: float,
    fracao: float,
    alavancagem: float,
    sizing_mode: str,
    pyramid_max_tranches: int | None,
    pyramid_tranche_equity_frac: float | None,
    pyramid_rearm_cooldown_bars: int | None,
    taker_fee_bps: float,
    slippage_bps_per_notional: float,
    spread_bps: float,
    strategy_name: str,
    short_window: int,
    long_window: int,
    long_only: bool,
    entry_window: int,
    exit_window: int,
    bollinger_window: int,
    bollinger_num_std: float,
    rsi_period: int,
    rsi_oversold: float,
    rsi_overbought: float,
    keltner_window: int,
    keltner_atr_period: int,
    keltner_mult: float,
    zscore_window: int,
    zscore_threshold: float,
    composite_bb_window: int = 20,
    composite_bb_num_std: float = 2.0,
    composite_rsi_period: int = 14,
    composite_rsi_oversold: float = 30.0,
    composite_rsi_overbought: float = 70.0,
    supertrend_atr_period: int = 10,
    supertrend_atr_mult: float = 3.0,
    lq_lookback: int = 20,
    lq_exit_mean_window: int = 10,
    time_stop_bars: int = 0,
    atr_trail_period: int = 0,
    atr_trail_mult: float = 0.0,
    be_atr_period: int = 0,
    be_mfe_trigger_atr: float = 0.0,
    n_folds: int = 3,
    scheme: str = "rolling",
    train_fraction: float = 0.5,
    min_test_bars: int = 50,
    mc_resamples: int = 1000,
    mc_seed: int = 42,
    perturbations: Sequence[CostPerturbation] = (),
    skip_monte_carlo: bool = False,
    skip_cost_stress: bool = False,
    regime_filter: RegimeFilter | None = None,
    flags: dict[str, str] | None = None,
) -> int:
    budget = RiskBudget(
        capital_inicial=capital,
        fracao_por_trade=fracao,
        alavancagem_max=alavancagem,
        sizing_mode=SizingMode(sizing_mode),
        pyramid_max_tranches=pyramid_max_tranches,
        pyramid_tranche_equity_fraction=pyramid_tranche_equity_frac,
        pyramid_rearm_cooldown_bars=pyramid_rearm_cooldown_bars,
    )
    cost_model = CostModel(
        taker_fee_bps=taker_fee_bps,
        slippage_bps_per_unit_notional=slippage_bps_per_notional,
        spread_bps=spread_bps,
    )
    directory = validation_run_dir(run_id)

    timestamp = _now_utc()
    metadata = RunMetadata(
        alpha_forge_version=alpha_forge.__version__,
        timestamp_utc=timestamp,
        command="validate",
        run_id=run_id,
        flags=flags,
    )
    meta_path = save_run_metadata(metadata=metadata, directory=directory)

    prices = load_dataset(dataset_id)
    strategy = _build_strategy(
        strategy_name,
        short_window=short_window,
        long_window=long_window,
        long_only=long_only,
        entry_window=entry_window,
        exit_window=exit_window,
        bollinger_window=bollinger_window,
        bollinger_num_std=bollinger_num_std,
        rsi_period=rsi_period,
        rsi_oversold=rsi_oversold,
        rsi_overbought=rsi_overbought,
        keltner_window=keltner_window,
        keltner_atr_period=keltner_atr_period,
        keltner_mult=keltner_mult,
        zscore_window=zscore_window,
        zscore_threshold=zscore_threshold,
        composite_bb_window=composite_bb_window,
        composite_bb_num_std=composite_bb_num_std,
        composite_rsi_period=composite_rsi_period,
        composite_rsi_oversold=composite_rsi_oversold,
        composite_rsi_overbought=composite_rsi_overbought,
        supertrend_atr_period=supertrend_atr_period,
        supertrend_atr_mult=supertrend_atr_mult,
        lq_lookback=lq_lookback,
        lq_exit_mean_window=lq_exit_mean_window,
        time_stop_bars=time_stop_bars,
        atr_trail_period=atr_trail_period,
        atr_trail_mult=atr_trail_mult,
        be_atr_period=be_atr_period,
        be_mfe_trigger_atr=be_mfe_trigger_atr,
    )

    print(f"dataset          : {dataset_id}")
    print(
        f"strategy         : {strategy_name} "
        f"{_strategy_param_label(strategy_name, short_window=short_window, long_window=long_window, long_only=long_only, entry_window=entry_window, exit_window=exit_window, bollinger_window=bollinger_window, bollinger_num_std=bollinger_num_std, rsi_period=rsi_period, rsi_oversold=rsi_oversold, rsi_overbought=rsi_overbought, keltner_window=keltner_window, keltner_atr_period=keltner_atr_period, keltner_mult=keltner_mult, zscore_window=zscore_window, zscore_threshold=zscore_threshold, composite_bb_window=composite_bb_window, composite_bb_num_std=composite_bb_num_std, composite_rsi_period=composite_rsi_period, composite_rsi_oversold=composite_rsi_oversold, composite_rsi_overbought=composite_rsi_overbought, supertrend_atr_period=supertrend_atr_period, supertrend_atr_mult=supertrend_atr_mult)}"
    )
    print(f"run_id           : {run_id}")
    print(f"regime_filter    : {canonical_string(regime_filter)}")
    print(f"out_dir          : {directory}")
    print(
        f"run_metadata     : alpha_forge={metadata.alpha_forge_version}, "
        f"ts={metadata.timestamp_utc.isoformat()} -> {meta_path}"
    )

    folds = walk_forward(
        prices=prices,
        strategy=strategy,
        budget=budget,
        cost_model=cost_model,
        dataset_id=dataset_id,
        n_folds=n_folds,
        scheme=scheme,  # type: ignore[arg-type]
        train_fraction=train_fraction,
        min_test_bars=min_test_bars,
        regime_filter=regime_filter,
    )
    wf_path = save_walk_forward_folds(folds=folds, directory=directory)
    total_trades = sum(f.result.metrics.trade_count for f in folds if f.result.metrics is not None)
    print(
        f"walk_forward     : {len(folds)} fold(s), {total_trades} trade(s) "
        f"-> {wf_path}"
    )

    if skip_monte_carlo:
        print("monte_carlo      : pulado (--skip-monte-carlo)")
    else:
        all_trades: list[Trade] = []
        for f in folds:
            all_trades.extend(f.result.trades)
        if not all_trades:
            print(
                "monte_carlo      : pulado (nenhum trade agregado nos folds)",
                file=sys.stderr,
            )
        else:
            total_pnl = sum(t.pnl for t in all_trades)
            agg = BacktestResult(
                dataset_id=dataset_id,
                bars=sum(f.test_window.bars for f in folds),
                fills=[],
                rejections=[],
                trades=all_trades,
                final_equity=capital + total_pnl,
                max_equity=capital + total_pnl,
                min_equity=capital + total_pnl,
                equity_curve=[
                    (all_trades[0].entry_timestamp, capital),
                ],
                metrics=BacktestMetrics(
                    total_pnl=total_pnl,
                    trade_count=len(all_trades),
                    hit_rate=sum(1 for t in all_trades if t.pnl > 0) / len(all_trades),
                    max_drawdown=0.0,
                ),
            )
            mc = monte_carlo_trades(
                result=agg,
                capital_inicial=capital,
                n_resamples=mc_resamples,
                seed=mc_seed,
            )
            mc_path = save_monte_carlo_summary(summary=mc, directory=directory)
            print(
                f"monte_carlo      : {mc.n_resamples} resamples, seed={mc.seed}, "
                f"median_final={mc.final_equity_percentiles[50]:.2f} -> {mc_path}"
            )

    if skip_cost_stress or not perturbations:
        reason = "--skip-cost-stress" if skip_cost_stress else "sem --stress"
        print(f"cost_stress      : pulado ({reason})")
    else:
        stress = cost_stress(
            prices=prices,
            strategy=strategy,
            budget=budget,
            baseline_cost=cost_model,
            perturbations=perturbations,
            dataset_id=dataset_id,
            regime_filter=regime_filter,
        )
        cs_path = save_cost_stress_report(report=stress, directory=directory)
        print(
            f"cost_stress      : baseline + {len(stress.scenarios)} cenario(s) "
            f"-> {cs_path}"
        )

    return 0


def _fmt_delta(delta: float) -> str:
    """Formata delta numérico com sinal explícito e 4 casas (ADR-0018 §output)."""
    return f"{delta:+.4f}"


def _diff_run_metadata(a: RunMetadata, b: RunMetadata) -> list[str]:
    """Funcão pura de diff sobre `RunMetadata` (ADR-0018)."""
    lines: list[str] = []
    ver_tag = "igual" if a.alpha_forge_version == b.alpha_forge_version else "divergente"
    lines.append(
        f"  alpha_forge_version : a={a.alpha_forge_version}  b={b.alpha_forge_version}  ({ver_tag})"
    )

    ts_a = a.timestamp_utc.isoformat()
    ts_b = b.timestamp_utc.isoformat()
    ts_delta_s = (b.timestamp_utc - a.timestamp_utc).total_seconds()
    lines.append(
        f"  timestamp_utc       : a={ts_a}  b={ts_b}  (delta={ts_delta_s:+.1f}s)"
    )

    cmd_tag = "igual" if a.command == b.command else "divergente"
    lines.append(f"  command             : a={a.command}  b={b.command}  ({cmd_tag})")

    rid_tag = "igual" if a.run_id == b.run_id else "divergente"
    lines.append(f"  run_id              : a={a.run_id}  b={b.run_id}  ({rid_tag})")

    all_keys = sorted(set(a.flags.keys()) | set(b.flags.keys()))
    different: list[tuple[str, str, str]] = []
    equal_count = 0
    for key in all_keys:
        va = a.flags.get(key, "<ausente>")
        vb = b.flags.get(key, "<ausente>")
        if va == vb:
            equal_count += 1
        else:
            different.append((key, va, vb))

    if not different:
        lines.append(f"  flags               : {equal_count} chave(s), todas iguais")
    else:
        lines.append(f"  flags diff ({len(different)} chave(s); {equal_count} iguais):")
        for key, va, vb in different:
            lines.append(f"    {key:<18}: a={va}  b={vb}")
    return lines


def _diff_walk_forward(
    a: list[WalkForwardFold], b: list[WalkForwardFold]
) -> list[str]:
    """Diff agregado de walk-forward (ADR-0018)."""
    lines: list[str] = []

    def _totals(folds: list[WalkForwardFold]) -> tuple[int, int, int, float]:
        n = len(folds)
        trades = sum(
            f.result.metrics.trade_count
            for f in folds
            if f.result.metrics is not None
        )
        bars = sum(f.test_window.bars for f in folds)
        equity_sum = sum(f.result.final_equity for f in folds)
        return n, trades, bars, equity_sum

    na, ta, ba, ea = _totals(a)
    nb, tb, bb, eb = _totals(b)

    lines.append(f"  n_folds          : a={na}  b={nb}  (delta={nb - na:+d})")
    lines.append(f"  total_trades     : a={ta}  b={tb}  (delta={tb - ta:+d})")
    lines.append(f"  total_test_bars  : a={ba}  b={bb}  (delta={bb - ba:+d})")
    lines.append(
        f"  sum_final_equity : a={ea:.4f}  b={eb:.4f}  (delta={_fmt_delta(eb - ea)})"
    )
    return lines


def _diff_monte_carlo(a: MonteCarloSummary, b: MonteCarloSummary) -> list[str]:
    """Diff de `MonteCarloSummary` sobre percentis fixos (ADR-0018)."""
    lines: list[str] = []
    lines.append(f"  n_resamples      : a={a.n_resamples}  b={b.n_resamples}")
    lines.append(f"  seed             : a={a.seed}  b={b.seed}")

    for pct in (5, 25, 50, 75, 95):
        va = a.final_equity_percentiles[pct]
        vb = b.final_equity_percentiles[pct]
        lines.append(
            f"  p{pct:<2}_final       : a={va:.4f}  b={vb:.4f}  (delta={_fmt_delta(vb - va)})"
        )
    lines.append(
        f"  original_final   : a={a.original_final_equity:.4f}  "
        f"b={b.original_final_equity:.4f}  "
        f"(delta={_fmt_delta(b.original_final_equity - a.original_final_equity)})"
    )
    lines.append(
        f"  original_maxdd   : a={a.original_max_drawdown:.6f}  "
        f"b={b.original_max_drawdown:.6f}  "
        f"(delta={b.original_max_drawdown - a.original_max_drawdown:+.6f})"
    )
    return lines


def _diff_cost_stress(a: CostStressReport, b: CostStressReport) -> list[str]:
    """Diff de `CostStressReport` por label de cenário (ADR-0018)."""
    lines: list[str] = []
    ds_tag = "igual" if a.dataset_id == b.dataset_id else "divergente"
    lines.append(f"  dataset_id       : a={a.dataset_id}  b={b.dataset_id}  ({ds_tag})")

    lines.append(
        f"  baseline_final   : a={a.baseline.final_equity:.4f}  "
        f"b={b.baseline.final_equity:.4f}  "
        f"(delta={_fmt_delta(b.baseline.final_equity - a.baseline.final_equity)})"
    )

    a_by_label = {cell.label: cell for cell in a.scenarios}
    b_by_label = {cell.label: cell for cell in b.scenarios}
    all_labels = sorted(set(a_by_label.keys()) | set(b_by_label.keys()))

    lines.append(f"  scenarios ({len(all_labels)} label(s)):")
    for label in all_labels:
        if label in a_by_label and label in b_by_label:
            fa = a_by_label[label].final_equity
            fb = b_by_label[label].final_equity
            lines.append(
                f"    {label:<18}: a={fa:.4f}  b={fb:.4f}  (delta={_fmt_delta(fb - fa)})"
            )
        elif label in a_by_label:
            lines.append(f"    {label:<18}: presente em A, ausente em B")
        else:
            lines.append(f"    {label:<18}: ausente em A, presente em B")
    return lines


def _cmd_compare(
    *,
    run_id_a: str,
    run_id_b: str,
    skip_run_metadata: bool,
    skip_walk_forward: bool,
    skip_monte_carlo: bool,
    skip_cost_stress: bool,
) -> int:
    directory_a = validation_run_dir(run_id_a)
    directory_b = validation_run_dir(run_id_b)

    print(f"run_a            : {run_id_a} ({directory_a})")
    print(f"run_b            : {run_id_b} ({directory_b})")
    print()

    # run_metadata: ausência em qualquer dos lados é erro — `run.json` é
    # gravado sempre pela ADR-0017.
    print("--- run_metadata ---")
    if skip_run_metadata:
        print("  pulado (--skip-run-metadata)")
    else:
        meta_a = load_run_metadata(directory=directory_a)
        meta_b = load_run_metadata(directory=directory_b)
        for line in _diff_run_metadata(meta_a, meta_b):
            print(line)
    print()

    print("--- walk_forward ---")
    if skip_walk_forward:
        print("  pulado (--skip-walk-forward)")
    else:
        wf_a_exists = (directory_a / "walk_forward.json").exists()
        wf_b_exists = (directory_b / "walk_forward.json").exists()
        if wf_a_exists and wf_b_exists:
            folds_a = load_walk_forward_folds(directory=directory_a)
            folds_b = load_walk_forward_folds(directory=directory_b)
            for line in _diff_walk_forward(folds_a, folds_b):
                print(line)
        elif wf_a_exists:
            print("  presente em A, ausente em B")
        elif wf_b_exists:
            print("  ausente em A, presente em B")
        else:
            print("  ausente em ambos")
    print()

    print("--- monte_carlo ---")
    if skip_monte_carlo:
        print("  pulado (--skip-monte-carlo)")
    else:
        mc_a_exists = (directory_a / "monte_carlo.json").exists()
        mc_b_exists = (directory_b / "monte_carlo.json").exists()
        if mc_a_exists and mc_b_exists:
            mc_a = load_monte_carlo_summary(directory=directory_a)
            mc_b = load_monte_carlo_summary(directory=directory_b)
            for line in _diff_monte_carlo(mc_a, mc_b):
                print(line)
        elif mc_a_exists:
            print("  presente em A, ausente em B")
        elif mc_b_exists:
            print("  ausente em A, presente em B")
        else:
            print("  ausente em ambos")
    print()

    print("--- cost_stress ---")
    if skip_cost_stress:
        print("  pulado (--skip-cost-stress)")
    else:
        cs_a_exists = (directory_a / "cost_stress.json").exists()
        cs_b_exists = (directory_b / "cost_stress.json").exists()
        if cs_a_exists and cs_b_exists:
            stress_a = load_cost_stress_report(directory=directory_a)
            stress_b = load_cost_stress_report(directory=directory_b)
            for line in _diff_cost_stress(stress_a, stress_b):
                print(line)
        elif cs_a_exists:
            print("  presente em A, ausente em B")
        elif cs_b_exists:
            print("  ausente em A, presente em B")
        else:
            print("  ausente em ambos")

    return 0


def _cmd_rank(
    *,
    runs_dir: str,
    slugs: list[str],
    weights_file: str | None,
    eligibility: str,
    agentic_dir: str | None,
    output: str | None,
    output_format: str,
) -> int:
    """Executa `alpha-forge rank` (ADR-0024)."""
    from pathlib import Path

    runs_path = Path(runs_dir)
    agentic_path = Path(agentic_dir) if agentic_dir else None
    weights = load_weights_toml(Path(weights_file)) if weights_file else None

    effective_slugs: list[str]
    if slugs:
        effective_slugs = list(slugs)
    else:
        effective_slugs = discover_slugs(runs_path)

    leaderboard = rank_pilots(
        slugs=effective_slugs,
        runs_dir=runs_path,
        weights=weights,
        eligibility=eligibility,
        agentic_dir=agentic_path,
    )

    if output is None:
        ts = leaderboard.generated_at.replace(":", "").replace("-", "")
        output_path = Path("results/ranking") / f"{ts}.json"
    else:
        output_path = Path(output)
    save_leaderboard(leaderboard, output_path)

    if output_format == "json":
        import json as _json
        print(_json.dumps(leaderboard.model_dump(mode="json"), indent=2))
    else:
        print(f"ranked {len(leaderboard.rows)} pilotos  (saved: {output_path})")
        header = (
            "rank  slug                                                score    hit      fe        mdd      trades  decision"
        )
        print(header)
        print("-" * len(header))
        for r in leaderboard.rows:
            print(
                f"{r.rank:>4}  {r.slug:<50s}  "
                f"{r.composite_score:>6.3f}  "
                f"{r.hit_baseline:>6.4f}  "
                f"{r.fe_baseline:>8.2f}  "
                f"{r.mdd_baseline:>6.4f}  "
                f"{r.trade_count:>5d}  {r.release_decision}"
            )
    return 0


def main() -> int:
    return run()
