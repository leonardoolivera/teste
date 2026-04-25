"""Regime filter — ADR-0022 minimal contract.

Filtro causal aplicado antes de ``Strategy.decide`` pelo engine (ADR-0022 §2).
Retorna ``True`` quando o regime permite emitir sinal; ``False`` força
``HOLD`` (se flat) ou ``EXIT`` (se posicionado) via coerção no engine.

Contrato idêntico ao de ``Strategy.decide``:

- ``window.iloc[-1]`` (barra ``t``) é ignorada por construção — filtro lê
  apenas ``window.iloc[:-1]`` (causal, ADR-0002).
- Stateless: ``is_active(window)`` é função pura de ``window`` e parâmetros.
- ``name: str`` identifica o filtro em ``run.json`` (ADR-0017).

Mudança de contrato entre ADR-0022 e futuras ADRs (ADR-0023+) é aditiva:
novos filtros implementam o mesmo Protocol sem mexer em engine/CLI.
"""

from __future__ import annotations

from typing import Literal, Protocol, Sequence, runtime_checkable

import pandas as pd


@runtime_checkable
class RegimeFilter(Protocol):
    """Filtro causal de regime (ADR-0022)."""

    name: str

    def is_active(self, window: pd.DataFrame) -> bool:
        """Decide sobre barra ``t`` baseado em ``window.iloc[:-1]``."""
        ...


class SMASlopeFilter:
    """Filtro de slope de SMA (ADR-0022 §3).

    Ativa sinal quando o slope percentual (em bps) da SMA de ``window``
    barras sobre ``close`` supera ``min_slope_bps`` em módulo. Slope é
    calculado entre a SMA atual (``sma[-1]``) e a SMA ``window`` barras
    antes (``sma[-window]``), relativo ao valor mais antigo:

        slope_bps = (sma[-1] - sma[-window]) / sma[-window] * 10000

    ``min_slope_bps=0`` aceita tudo (equivalente a ``regime_filter=None``
    com overhead mínimo).
    """

    name = "sma_slope"

    def __init__(self, window: int, min_slope_bps: float) -> None:
        if not isinstance(window, int) or isinstance(window, bool):
            raise TypeError(
                f"window deve ser int, recebeu {type(window).__name__}"
            )
        if window <= 0:
            raise ValueError(f"window deve ser > 0, recebeu {window}")
        if not isinstance(min_slope_bps, (int, float)) or isinstance(
            min_slope_bps, bool
        ):
            raise TypeError(
                f"min_slope_bps deve ser numérico, recebeu {type(min_slope_bps).__name__}"
            )
        if min_slope_bps < 0:
            raise ValueError(
                f"min_slope_bps deve ser >= 0, recebeu {min_slope_bps}"
            )

        self.window = window
        self.min_slope_bps = float(min_slope_bps)

    def is_active(self, window: pd.DataFrame) -> bool:
        # Ignora window.iloc[-1] (barra t) — causal por construção (ADR-0002).
        causal = window.iloc[:-1]
        if len(causal) < self.window + 1:
            # Warm-up: sem dados suficientes, filtro é inativo.
            return False

        closes = causal["close"]
        sma = closes.rolling(self.window).mean()
        sma_now = sma.iloc[-1]
        sma_prev = sma.iloc[-self.window - 1]
        if sma_prev == 0 or not (sma_prev == sma_prev):  # NaN-safe
            return False

        slope_bps = (sma_now - sma_prev) / sma_prev * 10000.0
        return abs(slope_bps) >= self.min_slope_bps


class ATRRegimeFilter:
    """Filtro de ATR (Average True Range) normalizado — segunda família.

    Ativa sinal quando ATR(``window``) relativo ao close mais recente
    supera ``min_atr_bps``. Captura regimes de alta volatilidade onde
    rompimentos têm mais chance de follow-through; suprime regimes
    comprimidos onde Donchian breakout gera whipsaws.

    ATR clássico (Wilder 1978) com média simples (não smoothing) sobre
    true range:

        tr[i] = max(high[i]-low[i], abs(high[i]-close[i-1]), abs(low[i]-close[i-1]))
        atr = mean(tr[-window:])
        atr_bps = atr / close[-1] * 10000

    ``min_atr_bps=0`` aceita tudo. Causal por construção (ADR-0002):
    lê apenas ``window.iloc[:-1]``.
    """

    name = "atr_regime"

    def __init__(
        self,
        window: int,
        min_atr_bps: float,
        max_atr_bps: float = float("inf"),
    ) -> None:
        if not isinstance(window, int) or isinstance(window, bool):
            raise TypeError(
                f"window deve ser int, recebeu {type(window).__name__}"
            )
        if window <= 0:
            raise ValueError(f"window deve ser > 0, recebeu {window}")
        if not isinstance(min_atr_bps, (int, float)) or isinstance(
            min_atr_bps, bool
        ):
            raise TypeError(
                f"min_atr_bps deve ser numérico, recebeu {type(min_atr_bps).__name__}"
            )
        if min_atr_bps < 0:
            raise ValueError(
                f"min_atr_bps deve ser >= 0, recebeu {min_atr_bps}"
            )
        if not isinstance(max_atr_bps, (int, float)) or isinstance(
            max_atr_bps, bool
        ):
            raise TypeError(
                f"max_atr_bps deve ser numérico, recebeu {type(max_atr_bps).__name__}"
            )
        if max_atr_bps <= 0:
            raise ValueError(
                f"max_atr_bps deve ser > 0 (use inf para desabilitar), recebeu {max_atr_bps}"
            )
        if max_atr_bps < min_atr_bps:
            raise ValueError(
                f"max_atr_bps ({max_atr_bps}) deve ser >= min_atr_bps ({min_atr_bps})"
            )

        self.window = window
        self.min_atr_bps = float(min_atr_bps)
        self.max_atr_bps = float(max_atr_bps)

    def is_active(self, window: pd.DataFrame) -> bool:
        causal = window.iloc[:-1]
        # Precisa window+1 barras pra computar window true ranges
        # (cada TR usa close[i-1]).
        if len(causal) < self.window + 1:
            return False

        highs = causal["high"].to_numpy()
        lows = causal["low"].to_numpy()
        closes = causal["close"].to_numpy()

        prev_closes = closes[-self.window - 1 : -1]
        highs_w = highs[-self.window :]
        lows_w = lows[-self.window :]

        tr1 = highs_w - lows_w
        tr2 = abs(highs_w - prev_closes)
        tr3 = abs(lows_w - prev_closes)
        tr = tr1.copy()
        for i in range(len(tr)):
            if tr2[i] > tr[i]:
                tr[i] = tr2[i]
            if tr3[i] > tr[i]:
                tr[i] = tr3[i]

        atr = tr.mean()
        close_now = closes[-1]
        if close_now == 0 or not (close_now == close_now):
            return False

        atr_bps = atr / close_now * 10000.0
        return bool(self.min_atr_bps <= atr_bps <= self.max_atr_bps)


class BollingerWidthFilter:
    """Filtro de largura de Bollinger Band — terceira família (extensão aditiva ADR-0022).

    Ativa sinal quando a largura relativa da banda de Bollinger (em bps
    sobre a média) supera ``min_width_bps``. Captura regimes de volatilidade
    estrutural (spread entre bandas), ortogonal ao ATR que mede candle range.

    Cálculo causal (ADR-0002):

        ma = mean(close[-window:])
        sigma = std(close[-window:], ddof=0)
        width = 2 * num_std * sigma
        width_bps = width / ma * 10000

    ``min_width_bps=0`` aceita tudo. Lê apenas ``window.iloc[:-1]``.
    """

    name = "bollinger_width"

    def __init__(
        self,
        window: int,
        num_std: float,
        min_width_bps: float,
        max_width_bps: float = float("inf"),
    ) -> None:
        if not isinstance(window, int) or isinstance(window, bool):
            raise TypeError(
                f"window deve ser int, recebeu {type(window).__name__}"
            )
        if window <= 1:
            raise ValueError(f"window deve ser > 1, recebeu {window}")
        if not isinstance(num_std, (int, float)) or isinstance(num_std, bool):
            raise TypeError(
                f"num_std deve ser numérico, recebeu {type(num_std).__name__}"
            )
        if num_std <= 0:
            raise ValueError(f"num_std deve ser > 0, recebeu {num_std}")
        if not isinstance(min_width_bps, (int, float)) or isinstance(
            min_width_bps, bool
        ):
            raise TypeError(
                f"min_width_bps deve ser numérico, recebeu {type(min_width_bps).__name__}"
            )
        if min_width_bps < 0:
            raise ValueError(
                f"min_width_bps deve ser >= 0, recebeu {min_width_bps}"
            )
        if not isinstance(max_width_bps, (int, float)) or isinstance(
            max_width_bps, bool
        ):
            raise TypeError(
                f"max_width_bps deve ser numérico, recebeu {type(max_width_bps).__name__}"
            )
        if max_width_bps <= 0:
            raise ValueError(
                f"max_width_bps deve ser > 0 (use inf para desabilitar), recebeu {max_width_bps}"
            )
        if max_width_bps < min_width_bps:
            raise ValueError(
                f"max_width_bps ({max_width_bps}) deve ser >= min_width_bps ({min_width_bps})"
            )

        self.window = window
        self.num_std = float(num_std)
        self.min_width_bps = float(min_width_bps)
        self.max_width_bps = float(max_width_bps)

    def is_active(self, window: pd.DataFrame) -> bool:
        causal = window.iloc[:-1]
        if len(causal) < self.window:
            return False

        closes = causal["close"].to_numpy()[-self.window :]
        ma = closes.mean()
        if ma == 0 or not (ma == ma):
            return False
        sigma = closes.std(ddof=0)
        width = 2.0 * self.num_std * sigma
        width_bps = width / ma * 10000.0
        return bool(self.min_width_bps <= width_bps <= self.max_width_bps)


class TrendHTFRegimeFilter:
    """Filtro de bias HTF (higher-timeframe) — ADR-0043.

    Resample da janela LTF pra timeframe maior (4h/1d/1w) e compara
    ``close_htf[-1]`` com ``SMA(sma_window)`` do HTF. ``mode="long_only"``
    ativa quando preço > SMA; ``short_only`` quando preço < SMA;
    ``both_sides`` quando qualquer um (sanity/debug).

    Causalidade (ADR-0002): ignora ``window.iloc[-1]`` E descarta o último
    candle HTF resampled (bucket pode estar aberto). Custa 1 candle HTF
    de defasagem — aceitável vs risco de lookahead.

    ``short_only`` está na API mas só faz sentido com estratégia que
    suporta short; hoje todas são long-only. Reservado para quando short
    side existir.
    """

    name = "trend_htf"

    _ALLOWED_HTF = ("4h", "1d", "1W")
    _ALLOWED_MODES = ("long_only", "short_only", "both_sides")

    def __init__(self, htf: str, sma_window: int, mode: str) -> None:
        if not isinstance(htf, str):
            raise TypeError(f"htf deve ser str, recebeu {type(htf).__name__}")
        if htf not in self._ALLOWED_HTF:
            raise ValueError(
                f"htf deve ser um de {self._ALLOWED_HTF}, recebeu {htf!r}"
            )
        if not isinstance(sma_window, int) or isinstance(sma_window, bool):
            raise TypeError(
                f"sma_window deve ser int, recebeu {type(sma_window).__name__}"
            )
        if sma_window <= 0:
            raise ValueError(
                f"sma_window deve ser > 0, recebeu {sma_window}"
            )
        if not isinstance(mode, str):
            raise TypeError(f"mode deve ser str, recebeu {type(mode).__name__}")
        if mode not in self._ALLOWED_MODES:
            raise ValueError(
                f"mode deve ser um de {self._ALLOWED_MODES}, recebeu {mode!r}"
            )

        self.htf = htf
        self.sma_window = sma_window
        self.mode = mode

    def is_active(self, window: pd.DataFrame) -> bool:
        # Ignora window.iloc[-1] (barra t) — causal (ADR-0002).
        causal = window.iloc[:-1]
        if len(causal) == 0:
            return False

        # Resample precisa DatetimeIndex; se index não for datetime, tentar converter.
        idx = causal.index
        if not isinstance(idx, pd.DatetimeIndex):
            try:
                causal = causal.copy()
                causal.index = pd.to_datetime(idx)
            except (ValueError, TypeError):
                return False

        agg = {
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
        }
        # label="right", closed="right": bucket [t-period, t] rotulado em t.
        resampled = causal.resample(self.htf, label="right", closed="right").agg(agg)
        # Descarta último candle HTF: pode conter LTF bars incompletos.
        resampled = resampled.iloc[:-1].dropna(subset=["close"])

        if len(resampled) < self.sma_window + 1:
            return False

        closes_htf = resampled["close"].to_numpy()
        sma = closes_htf[-self.sma_window :].mean()
        close_now = closes_htf[-1]

        if sma == 0 or not (sma == sma):
            return False
        if not (close_now == close_now):
            return False

        if self.mode == "long_only":
            return close_now > sma
        if self.mode == "short_only":
            return close_now < sma
        # both_sides: ativa se qualquer um (efetivamente close_now != sma).
        return close_now != sma


class BHDrawdownFilter:
    """Filtro Buy-and-Hold Drawdown — ADR-0220 (Padrão 58 mitigação).

    Bloqueia sinais quando o drawdown rolling do close (proxy buy-and-hold)
    excede ``max_dd_pct``. Útil para evitar que estratégias trend-following
    long-only operem durante bear absoluto (P52 V2/RAIO Cycle 5: catastrófico
    em 2022-H1+H2).

    ``lookback_bars``: janela rolling para calcular max histórico (e.g. 720 =
    30 dias em 1h). Drawdown = (max_lookback - close_now) / max_lookback.

    ``mode="block_below_max_dd"``: ativa filtro (sinal permitido) quando
    DD < max_dd_pct. Bloqueia (sinal vetado) quando DD >= max_dd_pct.

    Causal (ADR-0002): usa apenas window.iloc[:-1] para calcular max e DD.
    """

    name = "bh_drawdown"

    def __init__(self, lookback_bars: int, max_dd_pct: float) -> None:
        if not isinstance(lookback_bars, int) or isinstance(lookback_bars, bool):
            raise TypeError(f"lookback_bars deve ser int, recebeu {type(lookback_bars).__name__}")
        if lookback_bars <= 0:
            raise ValueError(f"lookback_bars deve ser > 0, recebeu {lookback_bars}")
        if not isinstance(max_dd_pct, (int, float)) or isinstance(max_dd_pct, bool):
            raise TypeError(f"max_dd_pct deve ser numérico, recebeu {type(max_dd_pct).__name__}")
        if max_dd_pct <= 0 or max_dd_pct >= 100:
            raise ValueError(f"max_dd_pct deve estar em (0, 100), recebeu {max_dd_pct}")

        self.lookback_bars = lookback_bars
        self.max_dd_pct = float(max_dd_pct)

    def is_active(self, window: pd.DataFrame) -> bool:
        # Causal — ignora barra t.
        causal = window.iloc[:-1]
        if len(causal) < self.lookback_bars:
            # Warm-up: sem dados suficientes para drawdown rolling, NÃO ativa
            # (conservador: bloqueia sinais até ter histórico suficiente).
            return False

        closes = causal["close"].to_numpy()
        recent = closes[-self.lookback_bars:]
        max_recent = recent.max()
        close_now = closes[-1]
        if max_recent <= 0 or not (max_recent == max_recent):
            return False
        if not (close_now == close_now):
            return False
        dd_pct = (max_recent - close_now) / max_recent * 100.0
        # Active (sinal permitido) quando DD ABAIXO do threshold.
        return dd_pct < self.max_dd_pct


class CompositeFilter:
    """Combinador lógico de filtros de regime (ADR-0023).

    ``mode="and"`` → ativa quando **todos** os filtros ativam.
    ``mode="or"``  → ativa quando **qualquer** filtro ativa.

    Ordenação canônica: filtros internos são ordenados por
    ``canonical_string`` ao serializar (`canonical_string`), garantindo
    que `CompositeFilter([f1,f2], "and")` e `CompositeFilter([f2,f1], "and")`
    produzam a mesma string (comutatividade canônica).

    Escopo inicial (ADR-0023 §Decision): apenas 1 nível — aninhamento
    (`and(or(...),...)`) é rejeitado no parser. ``len(filters) >= 2``
    e filtros com mesmo ``canonical_string`` são rejeitados (sem duplicatas).
    """

    name = "composite"

    def __init__(
        self, filters: Sequence[RegimeFilter], mode: Literal["and", "or"]
    ) -> None:
        if mode not in ("and", "or"):
            raise ValueError(f"mode deve ser 'and' ou 'or', recebeu {mode!r}")
        filters_list = list(filters)
        if len(filters_list) < 2:
            raise ValueError(
                f"CompositeFilter exige >= 2 filtros, recebeu {len(filters_list)}"
            )
        seen: set[str] = set()
        for f in filters_list:
            if isinstance(f, CompositeFilter):
                raise ValueError(
                    "CompositeFilter não aceita aninhamento (ADR-0023 §escopo inicial)"
                )
            key = canonical_string(f)
            if key in seen:
                raise ValueError(
                    f"CompositeFilter rejeita duplicatas: '{key}' aparece > 1 vez"
                )
            seen.add(key)
        self.filters = tuple(filters_list)
        self.mode = mode

    def is_active(self, window: pd.DataFrame) -> bool:
        if self.mode == "and":
            return all(f.is_active(window) for f in self.filters)
        return any(f.is_active(window) for f in self.filters)


def canonical_string(regime_filter: RegimeFilter | None) -> str:
    """Serializa filtro para ``run.json`` (ADR-0017 §flags).

    ``None`` → ``"none"``. Filtro concreto → ``"name:k=v:k=v"`` (ordem
    alfabética dos parâmetros). ``CompositeFilter`` → ``"mode(f1,f2,...)"``
    com filtros internos ordenados lexicograficamente (ADR-0023).
    """
    if regime_filter is None:
        return "none"
    if isinstance(regime_filter, SMASlopeFilter):
        return (
            f"{regime_filter.name}"
            f":min_slope_bps={regime_filter.min_slope_bps:g}"
            f":window={regime_filter.window}"
        )
    if isinstance(regime_filter, ATRRegimeFilter):
        max_part = (
            f":max_atr_bps={regime_filter.max_atr_bps:g}"
            if regime_filter.max_atr_bps != float("inf")
            else ""
        )
        return (
            f"{regime_filter.name}"
            f"{max_part}"
            f":min_atr_bps={regime_filter.min_atr_bps:g}"
            f":window={regime_filter.window}"
        )
    if isinstance(regime_filter, BollingerWidthFilter):
        max_part = (
            f":max_width_bps={regime_filter.max_width_bps:g}"
            if regime_filter.max_width_bps != float("inf")
            else ""
        )
        return (
            f"{regime_filter.name}"
            f"{max_part}"
            f":min_width_bps={regime_filter.min_width_bps:g}"
            f":num_std={regime_filter.num_std:g}"
            f":window={regime_filter.window}"
        )
    if isinstance(regime_filter, TrendHTFRegimeFilter):
        return (
            f"{regime_filter.name}"
            f":htf={regime_filter.htf}"
            f":mode={regime_filter.mode}"
            f":sma_window={regime_filter.sma_window}"
        )
    if isinstance(regime_filter, BHDrawdownFilter):
        return (
            f"{regime_filter.name}"
            f":lookback_bars={regime_filter.lookback_bars}"
            f":max_dd_pct={regime_filter.max_dd_pct:g}"
        )
    if isinstance(regime_filter, CompositeFilter):
        inner = sorted(canonical_string(f) for f in regime_filter.filters)
        return f"{regime_filter.mode}({','.join(inner)})"
    return regime_filter.name


def _parse_terminal(spec: str) -> RegimeFilter:
    """Parse de filtro terminal ``name:k=v:k=v`` (helper de ``parse_spec``)."""
    parts = spec.split(":")
    name = parts[0]
    kwargs: dict[str, str] = {}
    for part in parts[1:]:
        if "=" not in part:
            raise ValueError(
                f"--regime-filter esperava 'k=v' em cada parte, recebeu '{part}'"
            )
        key, value = part.split("=", 1)
        if key in kwargs:
            raise ValueError(
                f"--regime-filter parâmetro duplicado: '{key}'"
            )
        kwargs[key] = value

    if name == "sma_slope":
        try:
            return SMASlopeFilter(
                window=int(kwargs["window"]),
                min_slope_bps=float(kwargs["min_slope_bps"]),
            )
        except KeyError as err:
            raise ValueError(
                f"--regime-filter sma_slope exige window e min_slope_bps, faltou {err}"
            ) from err

    if name == "atr_regime":
        try:
            return ATRRegimeFilter(
                window=int(kwargs["window"]),
                min_atr_bps=float(kwargs["min_atr_bps"]),
                max_atr_bps=(
                    float(kwargs["max_atr_bps"])
                    if "max_atr_bps" in kwargs
                    else float("inf")
                ),
            )
        except KeyError as err:
            raise ValueError(
                f"--regime-filter atr_regime exige window e min_atr_bps, faltou {err}"
            ) from err

    if name == "bollinger_width":
        try:
            return BollingerWidthFilter(
                window=int(kwargs["window"]),
                num_std=float(kwargs["num_std"]),
                min_width_bps=float(kwargs["min_width_bps"]),
                max_width_bps=(
                    float(kwargs["max_width_bps"])
                    if "max_width_bps" in kwargs
                    else float("inf")
                ),
            )
        except KeyError as err:
            raise ValueError(
                f"--regime-filter bollinger_width exige window, num_std e min_width_bps, faltou {err}"
            ) from err

    if name == "trend_htf":
        try:
            return TrendHTFRegimeFilter(
                htf=kwargs["htf"],
                sma_window=int(kwargs["sma_window"]),
                mode=kwargs["mode"],
            )
        except KeyError as err:
            raise ValueError(
                f"--regime-filter trend_htf exige htf, sma_window e mode, faltou {err}"
            ) from err

    if name == "bh_drawdown":
        try:
            return BHDrawdownFilter(
                lookback_bars=int(kwargs["lookback_bars"]),
                max_dd_pct=float(kwargs["max_dd_pct"]),
            )
        except KeyError as err:
            raise ValueError(
                f"--regime-filter bh_drawdown exige lookback_bars e max_dd_pct, faltou {err}"
            ) from err

    raise ValueError(f"--regime-filter nome desconhecido: '{name}'")


def parse_spec(spec: str) -> RegimeFilter | None:
    """Parse de ``--regime-filter`` (ADR-0022 §4 + ADR-0023).

    Formas aceitas:

    - ``"none"`` ou string vazia → ``None``.
    - ``name:k=v:k=v`` → filtro terminal (ADR-0022).
    - ``and(f1,f2,...)`` ou ``or(f1,f2,...)`` → ``CompositeFilter``
      (ADR-0023). Filtros internos são parseados como terminais;
      aninhamento (``and(or(...),...)``) é rejeitado.

    Levanta ``ValueError`` para: nome desconhecido, kwargs duplicados,
    sintaxe composta mal-formada, aninhamento, ``< 2`` filtros internos,
    duplicatas.
    """
    if not spec or spec == "none":
        return None

    for mode in ("and", "or"):
        prefix = f"{mode}("
        if spec.startswith(prefix):
            if not spec.endswith(")"):
                raise ValueError(
                    f"--regime-filter '{mode}(...)' precisa terminar em ')'"
                )
            inner = spec[len(prefix) : -1]
            if not inner:
                raise ValueError(f"--regime-filter '{mode}(...)' vazio")
            # aninhamento é rejeitado — se qualquer f_i começa com and(/or(, erra
            raw_filters = inner.split(",")
            filters: list[RegimeFilter] = []
            for raw in raw_filters:
                raw = raw.strip()
                if raw.startswith(("and(", "or(")):
                    raise ValueError(
                        "CompositeFilter não aceita aninhamento (ADR-0023 §escopo inicial)"
                    )
                filters.append(_parse_terminal(raw))
            return CompositeFilter(filters, mode=mode)  # type: ignore[arg-type]

    return _parse_terminal(spec)
