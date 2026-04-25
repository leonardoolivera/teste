# AUDIT.md — L.3 Bollinger 20/2 ETH 15m 2024

release_decision: fail

## release_decision

**`fail`** — terceiro consecutivo. Trio L completo em 3/3 `fail` com mesma assinatura.

| Gate                                    | Observado | Status |
| --------------------------------------- | --------- | ------ |
| Critério 1: hit_rate baseline ≥ 45%     | 61.76%    | OK     |
| Critério 2: max_drawdown ≤ 35%          | 9.32%     | OK     |
| Critério 3: spread+10 / baseline ≥ 0.95 | **0.855** | **VIOLADO** |

## Blockers

- Baseline negativo (fe=9769.61 < 10000).
- Critério 3 violado pela maior margem do trio (0.855).
- ETH 15m tem **maior mdd do trio** (9.32% vs 5.11-5.53%) — mais vulnerável a gaps intra-dia.

## Findings

1. **Trio L fecha com padrão uniforme.** Spread+10/baseline = {0.871, 0.864, 0.855}
   — range de 16 bps. Propriedade estrutural do timeframe.
2. **ETH é o pior asset em 15m.** Combina fe negativo, pior mdd, e pior ratio de stress.
3. **Hit rate preservado em todos (60-63%).** Edge estatístico existe e é consistente
   cross-asset; falha é puramente econômica.
4. **Fe baseline ~capital inicial (±3%)** — o piloto nem "ganha" sem custos extras.
   Contrasta com 1h onde fe > capital em todos os 10 `canary_only` anteriores.
5. **ADR-0019 25ª confirmação** (`fee+10 ≡ spread+10 = 8357.51`).
6. **ADR-0025 funcionou como projetado.** Sem critério 3, os 3 pilotos L teriam
   passado por hit>45% — exatamente o que o critério visa evitar.

## Lições

1. **Mean-reversion em 15m é estatística mas não operacional.** Edge existe na
   distribuição de retornos, mas é menor que o custo de entrada+saída com spread
   real de liquidez.
2. **Handoff BotBinance 15m definitivamente refutado** — 3 assets, mesmo asset,
   ambos H2-2024 consistentes. Não é asset-specific, não é regime-specific.
3. **Série L é um resultado válido e informativo.** Três `fail` documentados valem
   mais que três `canary_only` redundantes — refuta uma hipótese real.
4. **ADR-0025 critério 3 é o filtro mais seletivo do protocolo.** 22/22 pilotos
   anteriores passaram critérios 1-2; 3 pilotos L falham só o 3.

## Recomendações

- **Nenhuma nova ADR.** Protocolo capturou o caso.
- **Handoff BotBinance:** permanecer em J.2 BTC 1h 2024 ou J.1 SOL 1h 2024.
- **Série M candidatos (em ordem de prioridade):**
  1. **M.1-M.3: Bollinger 4h cross-asset** — testa direção oposta (trade-off menos trades).
  2. **M.4-M.6: RSI oversold/overbought 1h cross-asset** — segunda família mean-reversion
     (requer nova ADR + implementação de família).
  3. **M.7+: regime filter + Bollinger 1h** — filtro de volatilidade para preservar edge
     em laterais e evitar trend regime.
