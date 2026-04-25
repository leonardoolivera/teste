# 0189 — Série CP (Composite BB+RSI) engine pré-reg Fase 1

**Status:** Proposed
**Date:** 2026-04-21
**Deciders:** Usuário ("vamo pra próxima estratégia") + agente
**Relates to:** ADR-0026 (Bollinger), ADR-0027 (RSI), ADR-0051 (short side), ADR-0183 §frente 2, ADR-0188 (PY refutado, autopilot avança)

## Contexto

Pyramid v4 refutado em 3 Fases (7 runs, Padrão 48 refutado, ADR-0188). Frentes cheap 1h fixed_notional exauridas na sessão. Próxima frente: **engine composite signal-level**, combinando dois engines proven (BB mean-rev + RSI mean-rev) com AND-at-entry e BB EXIT.

## Hipótese

Engines BB e RSI são mean-rev mas usam **indicadores não-correlacionados**: BB usa preço relativo a volatilidade (banda), RSI usa momentum de ganhos/perdas. Entry AND entre os dois **filtra false signals** onde um indicador dispara sem o outro (ex: banda tocada em momento neutro, ou RSI extreme sem preço fora do range). Expectativa: menos trades, Sharpe maior, trade-off em trade count.

Comparação principal: composite vs **BB sozinho** (baseline mais forte em SOL 2025-H1 short = Sh=2.71 com width filter; BTC long = Sh=1.70 proven combos). Se composite lifta Sharpe cross-era sem derrubar trade count abaixo de 30, promover.

## Escopo Fase 1

3 runs em 2025-H1 short (mesma janela que BB proven):

| Tag | Dataset | Strategy | Filter |
|---|---|---|---|
| CP.1 | BTC 2025-H1 | composite_bb_rsi 20/1.5 + rsi 14/35/65 short | bollinger_width:30:1.5:300 |
| CP.2 | ETH 2025-H1 | idem | idem |
| CP.3 | SOL 2025-H1 | idem | idem |

Parametrização:
- BB: window=20, num_std=1.5 (mesmo que combos proven v2 short)
- RSI: period=14, oversold=35, overbought=65 (thresholds menos extremos que 25/75; se AND falha com 25/75, too restrictive; 35/65 é middle-ground)
- Filter anexado: mesmo que BB+width baselines, para apples-to-apples
- `--no-long-only`, `--sizing-mode fixed_notional`, `--alavancagem 2.0`
- n-folds=3 rolling, mc_resamples=1000

## Gate pré-registrado (Padrão 4 + 41)

### Fase 1 pass criteria (≥2/3 assets):
- Sharpe ≥ 1.5 **AND**
- trades ≥ 30 **AND**
- Sharpe composite ≥ Sharpe BB-only baseline do mesmo asset+window (se baseline existe)

Baselines 2025-H1 short BB+width (ADR-0176 §Fase 3 / padrão stack):
- BTC: não temos baseline explícito 2025-H1 BB short + width para comparação direta — gate pass só se Sh≥1.5 + trades≥30.
- ETH: baseline 2.40 → gate: Sh ≥ 2.40 × 1.0 (não adicionar fator) — mas Padrão 41 é Sh≥1.5 absoluto. Vou aplicar gate duplo: **Sh ≥ 1.5 AND Sh ≥ 0.9 × baseline** onde baseline existe.
- SOL: baseline 2.71 → Sh ≥ 2.44 para edge preservation.

### Fase 2 (se Fase 1 pass ≥2/3):
Cross-era em 2025-H2 + 2024-H2, 6 runs. Gate = ≥4/6 pass mesmo critério.

### Refutação se Fase 1 fail:
Fase 1 0/3 ou 1/3 → composite refutado, closeout ADR-0190. Não escalar Fase 2.

## Prior e não-alvo

**Prior**: ~20% de passar Fase 1 cross-asset. Engines correlacionados (ambas mean-rev de preço) têm menos decorrelação do que esperaria em teoria — alta chance de AND cair muito trade count sem amplificar Sharpe.

**Não-alvo:**
- Não testar parametrizações alternativas de RSI threshold (25/75, 20/80) nesta Fase 1 — Padrão 4 evita fishing.
- Não testar composite long-side em Fase 1 (focus short é onde BB+width já consolidou edges).
- Não adicionar testes unit novos — engine segue mesmo template de BB e RSI já testados. Smoke test importação OK.
- Não emitir manifest se Fase 1 pass mas Fase 2 fail.

## Relação com handoff bot

Manifest v3 faithful compatível (sizing=fixed_notional, sem pyramid). Se promover, manifest é direto sem custo para bot. v4 stand-down permanece (ortogonal).

## Próximos passos

1. Tools `run_cb_sweep.py` + `summarize_cb.py`.
2. Fase 1 CP.1-3.
3. Summarize + ADR-0190.
4. Se pass: Fase 2 pré-reg emenda neste ADR.
5. Se fail: closeout + próxima frente (frente 3 cross-sectional, ou pausa Padrão 47 round 3).
