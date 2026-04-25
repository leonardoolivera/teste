# 0104 — Série CZC closeout: DOT Bollinger rescue — tail fino real, não promove v9 (Padrão 24)

**Status:** Accepted — closeout
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0103 (CZC pré-registro), ADR-0102 (CZB closeout), Padrão 23

## Resultado

**Gate 1 PASS 3/3, Gate 2 FAIL, Gate 4 FAIL → PASS contextual seed-only, não promove.**

| Tag | Config | Trades | PnL% | MDD% | Sh | MCp5 | MCmed | costr | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| CZB.1 | seed=42 mc=1000 | 127 | 9.10 | 12.52 | 1.330 | 9295 | 11002 | 0.9421 | FAIL |
| CZC.1 | seed=1337 mc=1000 | 127 | 9.10 | 12.52 | 1.330 | 9178 | 10986 | 0.9421 | FAIL |
| CZC.2 | seed=2024 mc=1000 | 127 | 9.10 | 12.52 | 1.330 | 9220 | 10975 | 0.9421 | FAIL |
| CZC.3 | seed=42 mc=2000 | 127 | 9.10 | 12.52 | 1.330 | 9282 | 11008 | 0.9421 | FAIL |

### Achados

**1. Walk-forward + backtest determinísticos por dataset/params.** Trades (127), PnL (+9.10%), MDD (12.52%), Sh (1.330) **idênticos entre seeds**. Seed afeta apenas bootstrap do Monte Carlo. "Seed stability" virou quase tautológico neste setup — teste real de estabilidade exigiria variar dataset split (ex: rolling window start date) ou fold count.

**2. MC p5 estável em ~9200-9300 cross-seed, cross-resample-count.** Com 1000 samples: {9178, 9220, 9295}. Com 2000 samples (seed 42): 9282. Range 120pts, todos ~7% abaixo do gate 9500. **Tail fino é propriedade real da distribuição de retornos da estratégia, não ruído de bootstrap.**

**3. cost_r=0.9421 determinístico.** Mesmo dataset/params → mesmo resultado em cost stress. Fee+10bps spread+10bps reduz final_equity em ~5.8%. Estrutura de custo DOT liquidez 2025-H2 deprime edge abaixo do threshold 0.95.

### Interpretação do Gate matrix

ADR-0103 linha "PASS | FAIL | —": "PASS contextual seed-only, tail fino, não promove default."

**Decisão:** não promove v9. DOT Bollinger naked 2025-H2 fica em backlog documentado como "edge real mas tail risk + custo fragil".

## Padrão 24 (NOVO) — "Seed stability" vs "dataset stability" não são a mesma coisa

**Enunciado:** Em setup walk-forward + MC bootstrap, alterar `mc_seed` só muda variance do bootstrap, não os trades/PnL/Sh base. Portanto "seed stability test" nesta tooling testa **variance de MC**, não **variance de backtest**.

**Implicação:** Se o objetivo é testar robustez do backtest em si, o protocolo canônico v4b {42, 1337, 2024} não ajuda — Sh será idêntico cross-seed. Testes úteis de robustez do backtest:
- Rolling window start date (desloca ±1 semana)
- Fold count (5 → 3 ou 7)
- Train fraction (0.5 → 0.4 ou 0.6)
- Dataset subset (primeira metade vs segunda metade)

**Corolário:** v4b {42/1337/2024} era útil em v3 CG.6 SOL porque o sizing/execução tinha stochastic elements (aleatoriedade de preenchimento ou smoothing). Na tooling atual `alpha-forge validate`, essa aleatoriedade não existe fora do MC bootstrap.

**Ação:** atualizar seed stability protocol para incluir pelo menos 1 variação de dataset split, não apenas 3 seeds de MC.

## Padrão 23 (CZB) reconfirmado mas ortogonal

CZC não muda Padrão 23 — filter width destrutivo em DOT permanece válido. CZC confirmou apenas que naked edge existe (Sh=1.33 replicável); tail risk/custo continuam fragilidades independentes da engine filter.

## Decisão final DOT 2025-H2

**Backlog:** DOT Bollinger naked 2025-H2 documentado como "edge real fragil".
- Sh=1.33, 127 trades, MDD 12.5%, PnL +9.10% → **edge genuíno de mean-reversion**
- MC p5 9282 → tail left 5% termina ~-7% abaixo inicial → **risk tail fino legítimo**
- cost_r 0.9421 → **~6% do edge consumido por stress custo** (structural DOT liquidez)

**Não promove v9 porque:** combo v8 já publicada (BTC+SOL+LINK) passa todos gates; adicionar DOT com MC p5 fail e cost_r fail dilui qualidade da stack.

**Re-abrir se:** surgir dataset window diferente (ex: 2026-H1) onde mesma config passa Gate 2 e 4 — indicaria 2025-H2 foi janela desfavorável específica, não propriedade estrutural.

### Stack inalterado
14 combos. v8 continua canônica (BTC+SOL+LINK RSI short 2025-H2, deprecates v3 que tinha só BTC+SOL).

### Bridge
**Sem post** — signal-only. Decisão não muda stack ativa do bot.

## Débito técnico reconhecido

Protocolo de seed stability v4b deveria ser renomeado/reestruturado para capturar o que realmente testa (MC variance) vs o que se imagina (backtest variance). Aplicar Padrão 24 em decisions futuras — exigir dataset split variation quando quiser robustez real.

## Próximos passos

1. **LINK seed stability expandida** (ainda pendente do ADR-0098): aplicar Padrão 24 — testar com dataset window shift (rolling start ±1 semana), não só mc_seed
2. **LINK replicação cross-window** (2024-H2 ou 2025-H1) — permanece como item forte
3. **Meta-correlação v8** BTC+SOL+LINK 2025-H2 (correlação de retornos OOS entre os 3 combos)
4. **Normalizar schema v2 Bollinger long** (débito técnico ADR-0096)
5. STATE.md atualizado

## Critério de sucesso desta ADR

1. ✅ Sweep CZC executado (3 runs)
2. ✅ Closeout documenta 3/3 Gate 1 + Gate 2 FAIL robusto
3. ✅ Padrão 24 formalizado
4. ✅ Decisão de não-promoção justificada por gate matrix
5. ✅ DOT backlog atualizado com condições de re-abertura
6. ⏳ STATE.md atualizado (próximo)
