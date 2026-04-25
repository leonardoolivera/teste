# AUDIT.md — P.3 Bollinger BTC 1h 2024 + composite AND

release_decision: canary_only

## release_decision

**`canary_only`** — 36º piloto. Cruza os 3 critérios ADR-0025; **melhor MC p5
do protocolo** (9995.84). **Dominado por P.2** em 3 eixos operacionais
(hit, fe, ratio) mas superior em MC p5. Trade-off: robustez estatística
marginal vs performance média.

| Gate                                    | Observado | Status |
| --------------------------------------- | --------: | ------ |
| Critério 1: hit_rate baseline ≥ 45%     |    71.23% |     OK |
| Critério 2: max_drawdown ≤ 35%          |     3.63% |     OK |
| Critério 3: spread+10 / baseline ≥ 0.95 |    0.9715 |     OK |

## Blockers

`canary-trade` inexistente.

## Findings

1. **AND(atr, sma) ≈ atr (isoladamente)** em BTC 2024-H2. Trade count P.2=72
   → P.3=73 (+1). Isto é contra-intuitivo (esperava-se AND sempre ≤ soma
   mínima) — ocorre porque o CompositeFilter pode forçar EXIT mid-trade
   e re-entrada em barras subsequentes (ADR-0023 finding de Série H.5),
   fragmentando trades. **Nenhum ganho material de composição.**
2. **MC p5 = 9995.84 é o melhor do protocolo** (+24.51 vs P.2, +74.11 vs
   J.2). Composição AND estreita distribuição inferior.
3. **fe baseline empata com J.2** dentro de 0.57 USDT — AND recupera
   frequência perdida pelo ATR mas com hit menor que ATR puro.
4. **Hit 71.23% < P.2 71.23% vs 73.61%**: −2.38 pp. Sinais adicionais vs
   P.2 são de qualidade média menor.
5. **ADR-0019 36ª confirmação** — primeira com `CompositeFilter(mode="and")`
   (bit-a-bit `fee+10 ≡ spread+10 = 9960.4985`).

## Lições

1. **Composição AND não domina família pura quando uma família já é
   eficaz isoladamente.** sma_slope quase não ativa em BTC 2024-H2 (P.1
   trade count ≈ J.2), então AND(ATR, sma) ≈ ATR com fragmentação
   marginal. Lição replica finding Série H.5 (AND Donchian long não
   superou H.3 SMA nem H.4 ATR) agora em mean-reversion.
2. **MC p5 como eixo de seleção pode sugerir P.3 sobre P.2, mas em
   protocolo operacional (ADR-0025) hit + fe + ratio têm peso maior
   (ADR-0024 default weights: `w_hit=2.0`, `w_fe=1.0`, `w_stress=1.0`,
   `w_p5=1.5`).** Score composto deve decidir.

## Recomendações

- **Manter P.2 como candidato primário a handoff** a menos que ranking
  composto mostre P.3 ≥ P.2. ADR-0024 prioriza hit > p5; esperado P.2 ≥ P.3
  em score.
- **Encerrar Série P em 3 pilotos.** Conclusão clara: `atr_regime` é o
  filtro dominante para Bollinger mean-reversion BTC 2024-H2; composição
  AND não adiciona valor material.
- **Série Q candidata:** replicar P.2 cross-asset (SOL + atr_regime; ETH
  + atr_regime) para validar universalidade do ganho.
