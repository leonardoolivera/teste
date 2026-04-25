# 0174 — Série KE Fase 3 closeout: Keltner 4h sparse (0/3 por trade count)

**Status:** Accepted — Keltner 4h arquivado (por sample insuficiente, não por edge ruim).
**Date:** 2026-04-20
**Deciders:** Usuário (piloto automático) + agente
**Relates to:** ADR-0173 (pré-reg), ADR-0172 (Keltner 1h refutado)

## Resultado

| Tag | Combo | Trades | Sh | PnL% | Pass |
|---|---|---:|---:|---:|:---:|
| KE.13 | BTC Keltner 4h 2025-H1 | 10 | 1.86 | 6.46 | ❌ (trades<30) |
| KE.14 | ETH Keltner 4h 2025-H1 | 7 | -0.55 | -3.57 | ❌ |
| KE.15 | SOL Keltner 4h 2025-H1 | 9 | 1.43 | 8.69 | ❌ (trades<30) |

0/3 pass gate. **BTC/SOL têm Sh promissor** mas sample (7-10 trades) é insuficiente para inferência.

## Interpretação

### 4h Keltner é sparse demais em 6 meses

Envelope ATR×2 em timeframe 4h é raramente rompido — ~1-2 eventos por mês em crypto 1h. 2025-H1 (180 dias) dá ~2160 barras 4h; signal fires ~5% do tempo = ~100 barras; trades por fold (36 barras test_window) = ~0.5. Mesmo com 5 folds totais = 5-10 trades por combo.

**Padrão estrutural de timeframe**: envelopes estatísticos em 4h precisam de **janelas longas (2+ anos)** para acumular trade count válido. Em 6 meses, sparse por design.

### Sharpe alto BTC/SOL é ruído

Com trade count 10, IC da Sharpe anual é enorme (±1.5 a ±2.0). BTC 1.86 pode ser lucky outlier; -0.55 em ETH com 7 trades idem. **Não promove**.

### Implicação para decisão

Não vale sweep de params (window menor, mult menor) em 4h. Ou:
- Ingestar 2 anos de 4h para ter sample — custo moderado, mas prior de edge já ruim baseado em 1h
- Arquivar 4h e seguir para próximo candidato — preferido no piloto automático

## Decisão

- **Keltner 4h arquivado**. Em timeframes 1h e 4h Keltner é não-deployable.
- Código Keltner ainda preservado. Hipóteses vivas: Keltner long-only (mas Padrão 40 seria testar em cross-era com 2024-H2, que já falhou em naked 1h).
- **Piloto automático avança para próxima hipótese**: zscore MR (Candidato A, ADR-0169).
- Nenhuma edição de manifest. Stack 13 combos inalterado.

## Próximo passo

ADR-0175 pré-reg + implementação zscore MR engine. Similar estrutura a Keltner:
- Novo engine `src/alpha_forge/strategies/families/zscore/`
- CLI wiring
- 3 runs probe BTC/ETH/SOL 2025-H1
- Gate Padrão 41 (≥2/3 ≥1.5)

Prior: pessimista (ADR-0169 estimou 90% redundante com BB). Mas dimensão não-testada + exit policy diferente (zero-crossing vs band-return) pode criar edge marginal.

## Não-alvo

- Não ingerir 2 anos 4h para salvar Keltner
- Não testar Keltner long-only cross-era (prior ruim)
- Não retry sweep params 4h
