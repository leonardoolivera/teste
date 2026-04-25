"""regimes — classificação de regime de mercado (ADR-0022).

Por enquanto: apenas o contrato mínimo ``RegimeFilter`` + implementação
concreta ``SMASlopeFilter`` (ADR-0022). Os 8 regimes enumerados em
``vision/02-scope.md`` permanecem deferred até haver consumidor concreto.
"""

from alpha_forge.regimes.filter import (
    ATRRegimeFilter,
    BollingerWidthFilter,
    CompositeFilter,
    RegimeFilter,
    SMASlopeFilter,
    TrendHTFRegimeFilter,
    canonical_string,
    parse_spec,
)

__all__ = [
    "ATRRegimeFilter",
    "BollingerWidthFilter",
    "CompositeFilter",
    "RegimeFilter",
    "SMASlopeFilter",
    "TrendHTFRegimeFilter",
    "canonical_string",
    "parse_spec",
]
