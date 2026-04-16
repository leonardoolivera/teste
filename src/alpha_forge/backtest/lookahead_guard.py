"""Guardião de causalidade (ADR-0002).

`assert_causal` é chamado pelo engine em toda execução, sem flag de
desativação. A regra é estrutural: sinal emitido em `t` deve ser computável
a partir de ``prices[:t+1]`` apenas. O guardião não prova causalidade — ele
detecta os padrões mais comuns de violação (peek perfeito, dependência do
close futuro).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


class LookaheadViolation(AssertionError):
    """Sinal correlaciona perfeitamente com informação futura."""


def _align(signals: pd.Series, prices: pd.Series) -> tuple[pd.Series, pd.Series]:
    if not signals.index.equals(prices.index):
        common = signals.index.intersection(prices.index)
        if len(common) == 0:
            raise LookaheadViolation(
                "signals e prices não compartilham nenhum timestamp"
            )
        signals = signals.loc[common]
        prices = prices.loc[common]
    return signals, prices


def assert_causal(signals: pd.Series, prices: pd.Series) -> None:
    """Levanta ``LookaheadViolation`` se detectar padrão incompatível com causalidade.

    Heurística:
    - Sinais são codificados numericamente: ``+1`` (enter_long), ``-1`` (enter_short),
      ``0`` (hold/exit). Strings são aceitas e mapeadas.
    - Se o sinal em `t` prevê com acurácia > 95% o retorno fechamento `t → t+1`
      olhando apenas os sinais não-zero, é tratado como evidência de peek.
    - Se o sinal é idêntico a uma função direta de ``prices.shift(-k)`` para k>=1,
      é violação estrutural.
    """
    signals, prices = _align(signals, prices)
    if len(signals) < 3:
        return

    numeric = _to_numeric(signals)

    forward_returns = prices.pct_change(fill_method=None).shift(-1)

    active_mask = numeric != 0
    active_count = int(active_mask.sum())
    if active_count >= 10:
        aligned_signal = numeric[active_mask]
        aligned_future = forward_returns[active_mask]
        valid = aligned_future.notna()
        if valid.sum() >= 10:
            signed_returns = aligned_signal[valid] * aligned_future[valid]
            hit_rate = float((signed_returns > 0).mean())
            if hit_rate > 0.95:
                raise LookaheadViolation(
                    f"sinal prevê retorno de t→t+1 com hit rate {hit_rate:.2%} "
                    f"(>95%); padrão consistente com peek"
                )

    for k in range(1, 4):
        shifted = prices.shift(-k).pct_change(fill_method=None)
        aligned = shifted.reindex(numeric.index)
        mask = aligned.notna() & (numeric != 0)
        if int(mask.sum()) < 10:
            continue
        corr = float(np.corrcoef(numeric[mask].to_numpy(), aligned[mask].to_numpy())[0, 1])
        if not np.isnan(corr) and abs(corr) > 0.95:
            raise LookaheadViolation(
                f"sinal correlaciona {corr:+.2f} com retorno futuro t+{k} "
                f"(|corr| > 0.95); violação estrutural de causalidade"
            )


def _to_numeric(signals: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(signals):
        return signals.astype(float).fillna(0.0)
    mapping = {
        "enter_long": 1.0,
        "enter_short": -1.0,
        "exit": 0.0,
        "hold": 0.0,
    }
    return signals.map(lambda v: mapping.get(str(v), 0.0)).astype(float)
