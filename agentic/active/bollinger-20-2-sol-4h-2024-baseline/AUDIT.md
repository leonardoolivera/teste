# AUDIT.md — M.1 Bollinger 20/2 SOL 4h 2024

release_decision: fail

## release_decision

**`fail`** — mas **por razão oposta à Série L**. Fe baseline < capital (9766.99 < 10000):
edge econômico não existe sem stress. Critério 1 passa (hit=57.14%), critério 3 passa
folgado (0.9915), mas piloto não gera retorno.

| Gate                                    | Observado | Status |
| --------------------------------------- | --------- | ------ |
| Critério 1: hit_rate baseline ≥ 45%     | 57.14%    | OK     |
| Critério 2: max_drawdown ≤ 35%          | 6.99%     | OK     |
| Critério 3: spread+10 / baseline ≥ 0.95 | **0.9915**| **OK** |
| Hipótese SPEC: fe > capital             | 9766.99   | **VIOLADO** |
| Corroboração WF fold min hit            | 0.00%     | VIOLADO |

## Blockers

- **Fe baseline abaixo de capital inicial.** Edge não cobre custos básicos H.1 mesmo com
  stress mínimo.
- **Amostra pequena** (21 trades, distribuídos 3+5+1+6 por fold). Fold 3 com 1 trade
  (hit=0%) amplifica variância.

## Findings

1. **Critério 3 passa folgado em 4h.** Confirma hipótese simétrica de L: timeframe menor
   → mais trades → mais custos; timeframe maior → menos trades → menos custos.
   Sensibilidade a spread é ~15× menor que em 15m (mesma razão 1:16 de trade count).
2. **Mas edge estatístico também desaparece.** Hit cai de 67.82% (J.1 1h) → 57.14% (M.1 4h).
   Redução de frequência de sinal reduz também o poder estatístico por amostra pequena.
3. **1h é o sweet spot em SOL Bollinger 20/2.** Trade-off simétrico identificado:
   - 15m: custos quebram edge (L.1 ratio 0.871)
   - 4h: amostra pequena quebra edge (M.1 fe 9766.99)
   - 1h: ambos preservados (J.1 ratio 0.967, fe 10684.24)
4. **ADR-0019 26ª confirmação** (`fee+10 ≡ spread+10 = 9683.54`).
5. **Monte Carlo corrobora:** p50=9931.68 < 10000 e p5=9300.91 — edge negativo na distribuição
   central, não só na amostra única.

## Lições

1. **Direção certa para Série M é lateral, não vertical.** Testar timeframes diferentes
   (4h) não resolveu porque edge requer frequência de sinal ≥ 1h nesta família/janela.
   Próxima exploração útil é:
   - **M.4-M.6:** segunda família mean-reversion (RSI) a 1h.
   - **M.7+:** regime filter + Bollinger 1h (melhorar edge no sweet spot em vez de mover
     timeframe).
2. **Parametrização de `min_test_bars` precisa escalar com timeframe.** 4 folds × 270 barras
   4h = 1080 barras → ~21 trades totais distribuídos. Amostra marginal para inferência.
3. **Combinação L+M delimita janela ótima formal.** Protocolo agora tem evidência de ambos
   os lados do sweet spot 1h.

## Recomendações

- **Nenhuma nova ADR necessária.** ADR-0025 capturou via hipótese SPEC.
- **Não expandir Série M em 4h.** M.2/M.3 provavelmente repetirão o padrão — completar
  trio para documentar simetria e fechar.
- **Priorizar RSI (segunda família mean-reversion, 1h)** para próxima rodada de pesquisa.
