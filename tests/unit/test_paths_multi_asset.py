"""Invariante multi-asset no pathing (ADR-0009 §2-bis).

`processed_dataset_path` trata `symbol` e `timeframe` como opacos. Nenhum
valor concreto (BTCUSDT, ETHUSDT, 1h, 1d) é privilegiado — o mesmo helper
gera paths corretos e mutuamente distintos para qualquer par
``(symbol, timeframe, dataset_id)``.

Este teste existe para impedir regressões que introduzam hardcode
específico de ativo em `io/paths.py`.
"""

from __future__ import annotations

from alpha_forge.io.paths import (
    data_processed_dir,
    processed_dataset_path,
)


def test_path_segue_padrao_symbol_timeframe_dataset_id() -> None:
    p = processed_dataset_path("ETHUSDT", "1h", "ethusdt_1h_demo")
    expected = data_processed_dir() / "ETHUSDT" / "1h" / "ethusdt_1h_demo.parquet"
    assert p == expected


def test_paths_de_simbolos_distintos_nao_colidem() -> None:
    p_eth = processed_dataset_path("ETHUSDT", "1h", "demo")
    p_sol = processed_dataset_path("SOLUSDT", "1h", "demo")
    p_btc = processed_dataset_path("BTCUSDT", "1h", "demo")
    assert len({p_eth, p_sol, p_btc}) == 3


def test_paths_de_timeframes_distintos_nao_colidem() -> None:
    p_1h = processed_dataset_path("ETHUSDT", "1h", "demo")
    p_4h = processed_dataset_path("ETHUSDT", "4h", "demo")
    p_1d = processed_dataset_path("ETHUSDT", "1d", "demo")
    assert len({p_1h, p_4h, p_1d}) == 3


def test_symbol_opaco_permite_forma_canonica_arbitraria() -> None:
    p_a = processed_dataset_path("BTCUSDT", "1h", "x")
    p_b = processed_dataset_path("BTC_USDT", "1h", "x")
    assert p_a != p_b
    assert p_a.parts[-3] == "BTCUSDT"
    assert p_b.parts[-3] == "BTC_USDT"
