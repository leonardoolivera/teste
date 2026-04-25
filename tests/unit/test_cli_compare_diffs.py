"""Unit das funções puras `_diff_*` da CLI `compare` (ADR-0018).

Testa as quatro funções puras de diff (sem filesystem, sem tmp_path):
`_diff_run_metadata`, `_diff_walk_forward`, `_diff_monte_carlo`,
`_diff_cost_stress`. Validamos presença de marcadores estruturais (linhas,
tags "igual"/"divergente", deltas com sinal) em vez de exigir match exato — isso
mantém o teste robusto a pequenos ajustes de formatação mas fixa o contrato
semântico declarado na ADR-0018.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from alpha_forge.backtest.cost import CostModel
from alpha_forge.backtest.schemas import (
    BacktestMetrics,
    BacktestResult,
    Side,
    Trade,
)
from alpha_forge.cli.app import (
    _diff_cost_stress,
    _diff_monte_carlo,
    _diff_run_metadata,
    _diff_walk_forward,
)
from alpha_forge.validation import (
    CostStressCell,
    CostStressReport,
    MonteCarloSummary,
    RunMetadata,
    WalkForwardFold,
    WalkForwardWindow,
)


def _utc(y: int, m: int, d: int, h: int = 0) -> datetime:
    return datetime(y, m, d, h, tzinfo=timezone.utc)


def _result(dataset_id: str = "ds", final_equity: float = 10_005.0, trade_count: int = 1) -> BacktestResult:
    trade = Trade(
        side=Side.LONG,
        entry_timestamp=_utc(2025, 1, 1),
        exit_timestamp=_utc(2025, 1, 2),
        entry_price=100.0,
        exit_price=105.0,
        size=1.0,
        pnl=5.0,
    )
    return BacktestResult(
        dataset_id=dataset_id,
        bars=24,
        fills=[],
        rejections=[],
        trades=[trade] * trade_count,
        final_equity=final_equity,
        max_equity=final_equity,
        min_equity=10_000.0,
        equity_curve=[(_utc(2025, 1, 1), 10_000.0), (_utc(2025, 1, 2), final_equity)],
        metrics=BacktestMetrics(
            total_pnl=final_equity - 10_000.0,
            trade_count=trade_count,
            hit_rate=1.0,
            max_drawdown=0.0,
        ),
    )


def _fold(index: int, bars: int = 384, final_equity: float = 10_005.0, trade_count: int = 1) -> WalkForwardFold:
    return WalkForwardFold(
        fold_index=index,
        train_window=WalkForwardWindow(
            start=_utc(2025, 1, 1), end=_utc(2025, 1, 15), bars=360
        ),
        test_window=WalkForwardWindow(
            start=_utc(2025, 1, 16), end=_utc(2025, 1, 31), bars=bars
        ),
        result=_result(
            dataset_id=f"ds#fold{index}",
            final_equity=final_equity,
            trade_count=trade_count,
        ),
    )


def _mc(
    *,
    n_resamples: int = 1000,
    seed: int = 42,
    p50_final: float = 10_000.0,
    original_final: float = 10_050.0,
    original_maxdd: float = 0.04,
) -> MonteCarloSummary:
    return MonteCarloSummary(
        n_resamples=n_resamples,
        seed=seed,
        final_equity_percentiles={
            5: 9_500.0,
            25: 9_800.0,
            50: p50_final,
            75: 10_200.0,
            95: 10_500.0,
        },
        max_drawdown_percentiles={5: 0.01, 25: 0.02, 50: 0.05, 75: 0.08, 95: 0.12},
        original_final_equity=original_final,
        original_max_drawdown=original_maxdd,
    )


def _report(
    *,
    dataset_id: str = "ds",
    baseline_final: float = 10_005.0,
    scenarios: list[tuple[str, float]] | None = None,
) -> CostStressReport:
    scenarios = scenarios if scenarios is not None else [("fee+5", 10_000.0)]
    baseline_cell = CostStressCell(
        scenario_index=0,
        label="baseline",
        cost=CostModel(taker_fee_bps=0.0, slippage_bps_per_unit_notional=0.0),
        result=_result(final_equity=baseline_final),
        final_equity=baseline_final,
        final_equity_delta_vs_baseline=0.0,
    )
    stress_cells = [
        CostStressCell(
            scenario_index=idx + 1,
            label=label,
            cost=CostModel(taker_fee_bps=5.0, slippage_bps_per_unit_notional=0.0),
            result=_result(dataset_id=f"ds#{label}", final_equity=final),
            final_equity=final,
            final_equity_delta_vs_baseline=final - baseline_final,
        )
        for idx, (label, final) in enumerate(scenarios)
    ]
    return CostStressReport(
        dataset_id=dataset_id,
        baseline=baseline_cell,
        scenarios=stress_cells,
    )


def _meta(
    *,
    version: str = "0.1.0",
    ts: datetime | None = None,
    command: str = "validate",
    run_id: str = "abcd1234",
    flags: dict[str, str] | None = None,
) -> RunMetadata:
    return RunMetadata(
        alpha_forge_version=version,
        timestamp_utc=ts if ts is not None else _utc(2026, 4, 17, 10),
        command=command,
        run_id=run_id,
        flags=flags if flags is not None else {"input": "sample.csv", "seed": "42"},
    )


class TestDiffRunMetadata:
    def test_tudo_igual_marca_igual(self) -> None:
        a = _meta()
        b = _meta()
        lines = _diff_run_metadata(a, b)
        texto = "\n".join(lines)
        assert "(igual)" in texto
        # versão/comando/run_id todos iguais → três tags "igual" + flags iguais
        assert texto.count("(igual)") == 3
        assert "todas iguais" in texto
        # delta de timestamp é 0.0s
        assert "(delta=+0.0s)" in texto

    def test_versao_divergente_marca_divergente(self) -> None:
        a = _meta(version="0.1.0")
        b = _meta(version="0.2.0")
        lines = _diff_run_metadata(a, b)
        # linha de version deve ter tag divergente
        version_line = next(ln for ln in lines if "alpha_forge_version" in ln)
        assert "(divergente)" in version_line
        assert "a=0.1.0" in version_line
        assert "b=0.2.0" in version_line

    def test_timestamp_delta_em_segundos_com_sinal(self) -> None:
        ts_a = _utc(2026, 4, 17, 10)
        ts_b = ts_a + timedelta(seconds=125)
        lines = _diff_run_metadata(_meta(ts=ts_a), _meta(ts=ts_b))
        ts_line = next(ln for ln in lines if "timestamp_utc" in ln)
        assert "(delta=+125.0s)" in ts_line

    def test_flags_divergentes_lista_cada_chave(self) -> None:
        a = _meta(flags={"input": "a.csv", "seed": "42", "walk": "3"})
        b = _meta(flags={"input": "b.csv", "seed": "42", "walk": "5"})
        lines = _diff_run_metadata(a, b)
        texto = "\n".join(lines)
        assert "2 chave(s); 1 iguais" in texto
        # chaves aparecem ordenadas (input antes de walk)
        idx_input = next(i for i, ln in enumerate(lines) if "input" in ln and "a=a.csv" in ln)
        idx_walk = next(i for i, ln in enumerate(lines) if "walk" in ln and "a=3" in ln)
        assert idx_input < idx_walk

    def test_flag_ausente_em_um_lado_marca_ausente(self) -> None:
        a = _meta(flags={"input": "a.csv"})
        b = _meta(flags={"input": "a.csv", "extra": "x"})
        lines = _diff_run_metadata(a, b)
        texto = "\n".join(lines)
        assert "<ausente>" in texto
        assert "b=x" in texto


class TestDiffWalkForward:
    def test_listas_iguais_delta_zero(self) -> None:
        folds = [_fold(0), _fold(1)]
        lines = _diff_walk_forward(folds, folds)
        texto = "\n".join(lines)
        assert "n_folds          : a=2  b=2  (delta=+0)" in texto
        assert "(delta=+0.0000)" in texto  # sum_final_equity delta

    def test_n_folds_divergente_mostra_delta_inteiro(self) -> None:
        a = [_fold(0)]
        b = [_fold(0), _fold(1), _fold(2)]
        lines = _diff_walk_forward(a, b)
        texto = "\n".join(lines)
        assert "n_folds          : a=1  b=3  (delta=+2)" in texto

    def test_sum_final_equity_com_sinal(self) -> None:
        a = [_fold(0, final_equity=10_000.0)]
        b = [_fold(0, final_equity=10_123.4567)]
        lines = _diff_walk_forward(a, b)
        sum_line = next(ln for ln in lines if "sum_final_equity" in ln)
        assert "a=10000.0000" in sum_line
        assert "b=10123.4567" in sum_line
        assert "delta=+123.4567" in sum_line

    def test_total_trades_somados_dos_folds(self) -> None:
        a = [_fold(0, trade_count=1), _fold(1, trade_count=2)]
        b = [_fold(0, trade_count=4)]
        lines = _diff_walk_forward(a, b)
        trades_line = next(ln for ln in lines if "total_trades" in ln)
        assert "a=3" in trades_line
        assert "b=4" in trades_line
        assert "(delta=+1)" in trades_line

    def test_total_test_bars_somados(self) -> None:
        a = [_fold(0, bars=100), _fold(1, bars=200)]
        b = [_fold(0, bars=50)]
        lines = _diff_walk_forward(a, b)
        bars_line = next(ln for ln in lines if "total_test_bars" in ln)
        assert "a=300" in bars_line
        assert "b=50" in bars_line
        assert "(delta=-250)" in bars_line


class TestDiffMonteCarlo:
    def test_identicos_delta_zero(self) -> None:
        a = _mc()
        b = _mc()
        lines = _diff_monte_carlo(a, b)
        texto = "\n".join(lines)
        assert "n_resamples      : a=1000  b=1000" in texto
        assert "seed             : a=42  b=42" in texto
        assert "(delta=+0.0000)" in texto

    def test_percentis_fixos_aparecem_todos(self) -> None:
        a = _mc()
        b = _mc()
        lines = _diff_monte_carlo(a, b)
        texto = "\n".join(lines)
        for pct in (5, 25, 50, 75, 95):
            assert f"p{pct}" in texto

    def test_p50_diverge_delta_com_sinal(self) -> None:
        a = _mc(p50_final=10_000.0)
        b = _mc(p50_final=9_875.0)
        lines = _diff_monte_carlo(a, b)
        p50_line = next(ln for ln in lines if "p50" in ln)
        assert "a=10000.0000" in p50_line
        assert "b=9875.0000" in p50_line
        assert "delta=-125.0000" in p50_line

    def test_original_maxdd_seis_casas_com_sinal(self) -> None:
        a = _mc(original_maxdd=0.040000)
        b = _mc(original_maxdd=0.041500)
        lines = _diff_monte_carlo(a, b)
        maxdd_line = next(ln for ln in lines if "original_maxdd" in ln)
        assert "a=0.040000" in maxdd_line
        assert "b=0.041500" in maxdd_line
        assert "+0.001500" in maxdd_line

    def test_seed_divergente_mostra_ambas(self) -> None:
        a = _mc(seed=42)
        b = _mc(seed=99)
        lines = _diff_monte_carlo(a, b)
        seed_line = next(ln for ln in lines if "seed" in ln)
        assert "a=42" in seed_line
        assert "b=99" in seed_line


class TestDiffCostStress:
    def test_identicos_tudo_igual(self) -> None:
        a = _report()
        b = _report()
        lines = _diff_cost_stress(a, b)
        texto = "\n".join(lines)
        assert "dataset_id       : a=ds  b=ds  (igual)" in texto
        assert "(delta=+0.0000)" in texto
        assert "fee+5" in texto

    def test_dataset_divergente(self) -> None:
        a = _report(dataset_id="ds-a")
        b = _report(dataset_id="ds-b")
        lines = _diff_cost_stress(a, b)
        ds_line = next(ln for ln in lines if "dataset_id" in ln)
        assert "(divergente)" in ds_line

    def test_baseline_delta_com_sinal(self) -> None:
        a = _report(baseline_final=10_000.0)
        b = _report(baseline_final=10_050.5)
        lines = _diff_cost_stress(a, b)
        bl_line = next(ln for ln in lines if "baseline_final" in ln)
        assert "a=10000.0000" in bl_line
        assert "b=10050.5000" in bl_line
        assert "delta=+50.5000" in bl_line

    def test_labels_so_em_a_marca_ausente_em_b(self) -> None:
        a = _report(scenarios=[("fee+5", 10_000.0), ("fee+10", 9_950.0)])
        b = _report(scenarios=[("fee+5", 9_999.0)])
        lines = _diff_cost_stress(a, b)
        texto = "\n".join(lines)
        assert "presente em A, ausente em B" in texto
        # label específico que está só em A
        fee10_line = next(ln for ln in lines if "fee+10" in ln)
        assert "presente em A, ausente em B" in fee10_line

    def test_labels_so_em_b_marca_ausente_em_a(self) -> None:
        a = _report(scenarios=[("fee+5", 10_000.0)])
        b = _report(scenarios=[("fee+5", 9_999.0), ("fee+20", 9_800.0)])
        lines = _diff_cost_stress(a, b)
        fee20_line = next(ln for ln in lines if "fee+20" in ln)
        assert "ausente em A, presente em B" in fee20_line

    def test_labels_ordenados_alfabeticamente(self) -> None:
        a = _report(scenarios=[("fee+20", 9_900.0), ("fee+05", 9_950.0)])
        b = _report(scenarios=[("fee+20", 9_900.0), ("fee+05", 9_950.0)])
        lines = _diff_cost_stress(a, b)
        idx_05 = next(i for i, ln in enumerate(lines) if "fee+05" in ln)
        idx_20 = next(i for i, ln in enumerate(lines) if "fee+20" in ln)
        assert idx_05 < idx_20
