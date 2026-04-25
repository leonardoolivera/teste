# 0177 — Série TF Fase 1 pré-reg: Bollinger+width 15m 2024-H2

**Status:** Accepted — probe em execução
**Date:** 2026-04-20
**Deciders:** Usuário (piloto automático) + agente
**Relates to:** ADR-0176 (zscore closeout), ADR-0096 (snapshot), Padrão 44 (timeframe)

## Motivação

Após Keltner e zscore refutados, restam 3 frentes cheap-probe:
- **Timeframes alternativos com engines aprovadas** ← escolhido (disponível só 15m 2024-H2)
- BB+RSI composite engine (requer dev de CLI hook)
- Portfolio/cross-sectional (requer engine novo)

Precedent timeframe: Padrão 44 (ADR-0096) — 4h foi sepultado, 1h é sweet spot em 2025. **15m nunca foi testado** com combo aprovado. Hipótese: se BB+width 1h funciona por captar reversion em consolidação, 15m pode dar mais trades mas com edge por trade menor (noise). Prior: incerto — pode passar por trade count ou falhar por fees/sinal ruim.

Dataset disponível: só `{btc,eth,sol}usdt_15m_20240705_20241231_binance_spot` (2024-H2). Cross-era validation (combos 1h aprovados foram validados em 2024-H2 também).

## Decisão (pré-reg)

Probe **TF.1-3**: Bollinger+width short 15m 2024-H2:

- `--strategy bollinger --bollinger-window 20 --bollinger-num-std 2.0 --no-long-only`
- `--regime-filter bollinger_width:window=30:num_std=1.5:min_width_bps=250`
- Mesmo budget/costs/stress que BK/BN/BO canônico
- 5 folds rolling, train 0.5, MC 1000 seed 42

**Gate Padrão 41:** ≥2/3 `annual_sharpe ≥ 1.5 AND trades ≥ 30`.

**Anual 15m:** `sqrt(96 × 365) ≈ 187` como factor.

## Decisão condicional

- **Pass (≥2/3):** ingerir 15m 2025-H1 + H2 + 2024-H1 para cross-window validation, depois Padrão 43 diversification check. Se sobrevive → export manifest.
- **Fail:** ADR closeout timeframe 15m, arquivar frente timeframes.
- **1/3 (Padrão 41):** considerar normalização por +filter adicional ou arquivar.

## Prior

**Pessimista-médio.** BB+width edge depende de consolidação persistente — 15m tem mais micro-noise e fees pesam mais por trade. Probabilidade de pass: ~35%.

## Não-alvo

- Não testar 30m (não ingerido)
- Não testar RSI+width 15m antes de ver BB+width (prior paralelo)
- Não tunar params 15m-specific antes de probe cego
