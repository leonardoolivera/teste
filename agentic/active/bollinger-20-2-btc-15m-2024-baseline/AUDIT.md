# AUDIT.md — L.2 Bollinger 20/2 BTC 15m 2024

release_decision: fail

## release_decision

**`fail`** — replica L.1. Critério 3 violado por margem ainda maior: `0.864 < 0.95`.
**Fe baseline < capital inicial** (9696.67 vs 10000) — edge econômico já negativo sem stress.

| Gate                                    | Observado | Status |
| --------------------------------------- | --------- | ------ |
| Critério 1: hit_rate baseline ≥ 45%     | 60.00%    | OK     |
| Critério 2: max_drawdown ≤ 35%          | 5.11%     | OK     |
| Critério 3: spread+10 / baseline ≥ 0.95 | **0.864** | **VIOLADO** |

## Blockers

Dois blockers simultâneos:
1. **Baseline negativo** (fe=9696.67 < 10000) — mesmo sem stress, BTC 15m não cobre custos H.1.
2. **Critério 3 violado** — +10 bps derruba 13.61% adicional.

## Findings

1. **Hit alto não salva edge econômico.** 60.00% é acima de 45% mas insuficiente em
   15m: cada trade paga mais custos relativos porque movimentos mean-reversion em 15m
   são menores (menor range) → hit×avg_win < (1-hit)×avg_loss + custos.
2. **BTC 15m é o pior caso.** Fe baseline negativo já contrasta com SOL 15m (+4.34%)
   e com BTC 1h (+2.52%). BTC 15m combina baixa volatilidade relativa ao custo.
3. **Replicação formal do achado L.1.** Mesmo padrão (spread ratio ~0.86-0.87) em
   outro asset confirma: fragilidade é propriedade do timeframe, não do underlying.
4. **ADR-0019 24ª confirmação** (`fee+10 ≡ spread+10 = 8376.61`).

## Lições

1. **15m destrói edge mean-reversion em BTC.** Asset mais líquido e "estável" do mercado,
   quando amostrado em 15m, tem range intra-barra insuficiente para cobrir spread+fee.
2. **Fe baseline < capital é sinal de stop imediato.** Piloto não precisa nem de stress
   — já falha antes. Para futuros pilotos, considerar pre-filtro (early-stop se fe<10000
   antes de rodar WF/MC/stress).
3. **Handoff 15m formalmente refutado em dois assets.** Junto com L.1, dobra a confiança
   na conclusão: BotBinance handoff deve ser 1h, não menor.

## Recomendações

- **Nenhuma nova ADR necessária.** ADR-0025 capturou o caso.
- **L.3 ETH 15m** para fechar o trio cross-asset (replicação tripla).
- **Série M** deve explorar timeframe **maior** (4h), não menor, ou famílias distintas.
