# `backtest/` — módulo 5

## Responsabilidade

Simulação causal e realista da execução da estratégia. Motor central de execução que respeita custos, slippage, funding e a política anti-lookahead.

## O que ainda não existe

Tudo. Nenhuma simulação implementada. Nenhum adapter para `vectorbt`.

Capabilities previstas em `vision/02-scope.md`:

- ordens market / stop / limit simplificada
- maker/taker fees
- slippage
- funding
- spread sintético
- expiração de sinal
- latência opcional
- leverage até 10x
- enforcement anti-lookahead
- integração opcional com `regimes`

## Depende de

`data`, `strategies`, `risk`, `regimes`. Orquestra os quatro.

## Primeiro arquivo real esperado

`schemas.py` — `BacktestConfig` (fees, slippage, funding, spread, latência, leverage) e `BacktestResult` (trades, equity curve, métricas brutas). Segundo passo: `engine.py` (adapter sobre vectorbt) e `lookahead_guard.py` (infra anti-lookahead enforçada antes de rodar qualquer backtest).

Referências: ADR-0002 (anti-lookahead, a escrever), ADR-0001 (escolha de vectorbt).
