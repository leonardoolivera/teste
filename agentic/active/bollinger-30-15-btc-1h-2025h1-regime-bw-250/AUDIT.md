# AUDIT.md - AZ.3

## Conformidade ADR

- ADR-0002 causal: OK.
- ADR-0019: OK (bit-identico).
- ADR-0022: OK.
- ADR-0025: hit 62.50% >= 45%; mdd 0.48% <= 35%; ratio 0.9864 >= 0.95.
- ADR-0026: OK.

## Blockers

Nenhum.

## Decisao de release

release_decision: canary_only

Passa ALL strict gates: p5 MC 10151.27 >= 10000, mdd p95 0.48% <= 10%, ratio 0.9864 >= 0.95, fee==spread. Strategy w=30 Pareto-domina w=20 cross-year (evidencia AW+AX).

## Contexto AZ

Formalizacao do achado AW: strategy bollinger window=30 + bollinger_width:250 cross-year gera 4/14 pilotos ALL-strict-gates vs 2/8 AK (w=20). Este e 1 dos 4.
