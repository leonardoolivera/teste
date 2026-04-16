# `regimes/` — módulo 3

## Responsabilidade

Classificar o mercado em regimes auditáveis e reutilizáveis. Expor regime como feature consumível por `backtest` e `validation`.

## O que ainda não existe

Tudo. Nenhum classificador implementado.

Regimes previstos em `vision/02-scope.md`:

- tendência forte de alta
- tendência forte de baixa
- lateral de baixa volatilidade
- lateral de alta volatilidade
- compressão
- expansão
- pânico
- euforia

A primeira versão usa **heurísticas auditáveis** (ATR, ADX, volatilidade realizada). Classificador via ML está em `deferred` (não agora).

## Depende de

`data`.

## Primeiro arquivo real esperado

`schemas.py` — enum `Regime` + modelo pydantic `RegimeClassification` (janela, regime, confiança, features usadas). Segundo passo: `heuristic.py` com o classificador baseado em indicadores.
