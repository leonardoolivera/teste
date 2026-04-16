# `validation/` — módulo 6

## Responsabilidade

Validar robustez estatística e resistência da estratégia. **Nada sobe para o ranking sem passar por aqui** (Definition of success em `vision/01-product.md`).

## O que ainda não existe

Tudo. Nenhum validador implementado.

Capabilities previstas em `vision/02-scope.md`:

- walk-forward
- out-of-sample
- Monte Carlo
- perturbação de fees/slippage
- parameter stability
- robustness score
- flags de fragilidade (`CURVE FIT PROVÁVEL`, `FRÁGIL`, `NÃO GENERALIZA`)
- grid search
- random search

## Depende de

`backtest`.

## Primeiro arquivo real esperado

`schemas.py` — `ValidationConfig` (splits de walk-forward, nº de simulações Monte Carlo com seed obrigatório, magnitudes de perturbação) e `ValidationReport` (scores por fold, flags, estabilidade paramétrica). Segundo passo: `walk_forward.py` e `monte_carlo.py`.

Referência: ADR-0003 (protocolo de validação, a escrever) formaliza o pipeline completo.
