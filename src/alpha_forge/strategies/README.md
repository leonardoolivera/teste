# `strategies/` — módulo 2

## Responsabilidade

Catálogo de estratégias com interface comum e parâmetros auditáveis.

## O que ainda não existe

Tudo. Nenhuma família implementada, nenhum `base.py`, nenhum `registry.py`.

Capabilities previstas em `vision/02-scope.md`:

- interface padrão long/short
- stop fixo / ATR / trailing
- takes parcial e final
- break-even
- pyramiding opcional
- filtros configuráveis (tendência, volatilidade, sessão)
- 10 famílias iniciais (breakout, momentum, pullback, mean reversion, liquidity sweep, continuação, expansão de range, snowball, falha de rompimento, híbrida)

## Depende de

`data`. **Não depende de `regimes`** — regime é insumo opcional injetado via `backtest`/`validation` (ADR-0001).

## Primeiro arquivo real esperado

`base.py` — classe/protocolo abstrato `Strategy` com o contrato mínimo (input: OHLCV + parâmetros validados via pydantic; output: séries de sinais long/short, stops, takes, flags de filtro). Segundo passo: `registry.py` (registro de estratégias por nome).

Subpasta `families/` recebe uma subpasta por família; cada família declara hipótese, parâmetros, riscos, filtros, regimes proibidos e modo de falha no seu próprio README.
