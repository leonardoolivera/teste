"""Resolução de caminhos canônicos do Alpha Forge.

Todos os módulos devem usar essas funções em vez de construir caminhos
ad-hoc. Mantém a estrutura documentada em ADR-0005 como única fonte de
verdade.
"""

from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    """Raiz do repositório, inferida a partir deste arquivo.

    src/alpha_forge/io/paths.py → sobe 4 níveis para chegar na raiz.
    """
    return Path(__file__).resolve().parents[3]


def data_dir() -> Path:
    return project_root() / "data"


def data_raw_dir() -> Path:
    return data_dir() / "raw"


def data_processed_dir() -> Path:
    return data_dir() / "processed"


def datasets_manifest_path() -> Path:
    return data_dir() / "datasets.yaml"


def processed_dataset_path(symbol: str, timeframe: str, dataset_id: str) -> Path:
    """Caminho canônico de um Parquet processado.

    Estrutura: ``data/processed/<symbol>/<timeframe>/<dataset_id>.parquet``
    conforme ADR-0005. Não cria o arquivo; apenas devolve o Path.
    """
    return data_processed_dir() / symbol / timeframe / f"{dataset_id}.parquet"


def results_dir() -> Path:
    return project_root() / "results"


def results_runs_dir() -> Path:
    return results_dir() / "runs"
