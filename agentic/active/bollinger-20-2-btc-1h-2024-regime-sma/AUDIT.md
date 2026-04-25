# AUDIT.md — P.1 Bollinger BTC 1h 2024 + sma_slope

release_decision: canary_only

## release_decision

**`canary_only`** — 34º piloto. Cruza os 3 critérios ADR-0025 com folga;
**melhora MC p5 vs J.2** (+81 USDT), mas custo de −1.96 pp em hit e −68 USDT
em fe. Trade-off: robustez estatística ganha, edge médio perde.

| Gate                                    | Observado | Status |
| --------------------------------------- | --------: | ------ |
| Critério 1: hit_rate baseline ≥ 45%     |    66.28% |     OK |
| Critério 2: max_drawdown ≤ 35%          |     3.63% |     OK |
| Critério 3: spread+10 / baseline ≥ 0.95 |    0.9662 |     OK |

## Blockers

`canary-trade` inexistente.

## Findings

1. **Filtro `sma_slope` não reduz trade count em mean-reversion BTC 1h.**
   85 (J.2 sem filtro) → 86 (com filtro). Regimes de slope forte são raros
   no dataset 2024-H2 de BTC — filtro fica quase inativo.
2. **MC p5 sobe +81 USDT**; p50 sobe +7 USDT; p95 cai −55 USDT. Filtro
   redistribui cauda inferior para cima, estreitando distribuição.
3. **Hit baseline cai −1.96 pp** (68.24% → 66.28%). Os sinais filtrados
   eram marginalmente positivos.
4. **WF mais robusto:** 4/4 folds em 66.67%-75%. J.2 tinha 64.71% min.
5. **ADR-0019 34ª confirmação** (`fee+10 ≡ spread+10 = 9840.0884`).

## Lições

1. **Filtro direcional (slope) em regime lateral (BTC 2024-H2) fica
   mayormente inativo** — 1 trade de diferença confirma que mean-reversion
   BTC 1h 2024-H2 já opera predominantemente em lateralidade.
2. **Trade-off robustez vs edge médio identificado:** MC p5 +81 mas
   fe baseline −68 e hit −2pp. Para handoff, preferimos fe + hit + ratio
   altos (operacional); P.1 não domina J.2.

## Recomendações

- **Manter J.2 como handoff primário.** P.1 não supera em nenhum eixo
  operacional (hit, fe, ratio).
- **P.2 (`atr_regime`) é o candidato a observar** — filtro de volatilidade
  pode comportar-se diferente em BTC 2024-H2.
