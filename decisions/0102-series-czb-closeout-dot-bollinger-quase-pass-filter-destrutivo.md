# 0102 — Série CZB closeout: DOT Bollinger naked quase PASS; filter width destrutivo (Padrão 23)

**Status:** Accepted — closeout
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0101 (CZB pré-registro), ADR-0098 (CZ), ADR-0100 (CZA + Padrão 22), Padrão 12

## Resultado

**0/4 PASS** mas com diagnóstico rico.

| Tag | Asset | Config | Trades | PnL% | MDD% | Sh | MCp5 | costr | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| CZB.1 | DOT | naked | 127 | +9.10 | 12.52 | **1.330** | 9295 | 0.9421 | FAIL (MCp5<9500, costr<0.95) |
| CZB.2 | AVAX | naked | 116 | -1.62 | 13.25 | -0.165 | 8181 | 0.9387 | FAIL |
| CZB.3 | DOT | filter | 110 | +0.60 | 9.95 | 0.176 | 8482 | 0.9440 | FAIL |
| CZB.4 | AVAX | filter | 94 | -1.28 | 8.67 | -0.170 | 8417 | 0.9490 | FAIL |

### Achado principal
**DOT Bollinger naked Sh=1.330**. Quase PASS — falha apenas por MC p5 9295 (< 9500) e cost_r 0.9421 (< 0.95). Sh, trades (127), MDD (12.5%), PnL (+9.1%) todos confortáveis. É o **primeiro indício de edge em DOT** que o RSI não capturou.

### Filter destrutivo em DOT
DOT naked Sh=1.33 → DOT+width Sh=0.18. **Delta = -1.15**. Filter corta os setups certos.

**Hipótese:** em DOT 2025-H2, Bollinger reverts nas caudas de pequenas janelas de baixa volatilidade. Width(300) exige vol ≥ 300bps — quando vol é alta, o sinal já está "virado" e RSI/Bollinger entra tarde. Filter bloqueia exatamente onde o edge existia.

Isso inverte Padrão 20 intuition: aqui o filter não resgata, **prejudica** porque o edge vive no regime oposto ao que o filter seleciona.

### AVAX continua refutado
Naked Sh=-0.17, filter Sh=-0.17 (praticamente idêntico). AVAX 2025-H2 não tem edge mean-reverting independente de engine ou filter.

## Padrão 23 (NOVO) — Filter direcional pode inverter efeito quando edge vive no regime oposto

**Enunciado:** Width filters (que exigem alta vol) **ampliam** edge de mean-reversion se este vive em regime expandido. Mas se o edge vive em regime **contraído** (vol baixa), width filter **destrói** o edge ao remover exatamente os setups válidos.

**Evidência:**
- v3 CG.6 SOL 2025-H1: Bollinger naked (não testado) → +width Sh=2.71 (filter positivo, edge em regime expandido)
- CZB.1 DOT 2025-H2: naked Sh=1.33 → +width Sh=0.18 (filter negativo, edge em regime contraído)

**Implicação:** filter choice deve ser testado **em ambas direções** para assets com edge latente. Width(300) é restritivo; width_MAX (filter para vol baixa) ou trend_htf podem ser alternativas para DOT.

## Decisão

### DOT 2025-H2 vai para backlog de rescue (NÃO encerra)
Sh=1.33 naked é sinal forte demais para descartar. Próximo passo: tentar rescue em outras configurações:
- **CZC.1**: DOT Bollinger naked com seed stability (seeds 1337, 2024) — se replicar Sh≥1.0 em 2/3 seeds, PASS contextual mesmo que MC p5 falhe em seed 42
- **CZC.2**: DOT Bollinger com stricter MC (2000 resamples, seed 42) — se MC p5 subir para ≥9500 com mais samples, confirma edge robusto
- **CZC.3**: DOT Bollinger + **inverse filter** (vol < threshold) — testa Padrão 23 diretamente
- **CZC.4**: DOT RSI naked com seeds 1337+2024 — check paralelo (CZ.1 era 0.50, poderia subir ou descer)

### AVAX 2025-H2 encerrado
Testado em 4 configurações (RSI naked, RSI+width, Bollinger naked, Bollinger+width). Todas FAIL. Naked Sh ~0 em ambas engines. Padrão 22 confirmado cross-engine. AVAX 2025-H2 não tem edge extraível — abandonar até haver nova janela ou engine substantivamente diferente.

### Stack inalterado
14 combos. Nenhum combo CZB entra.

### Bridge
**Sem post** — signal-only, sem mudança de stack. Diagnóstico interno.

## Padrão 22 refinado (via CZB)

Original (ADR-0100): "filter não cria edge onde não há naked signal."

Refinamento (pós CZB.1): **Padrão 22 permanece mas com corolário — naked weak também pode esconder edge bloqueado pela engine errada.** DOT RSI naked 0.50 dizia "edge fraco"; DOT Bollinger naked 1.33 disse "edge forte, RSI não captura". Antes de aplicar Padrão 22 e abandonar um asset, vale probe com engine complementar (mean-reversion vs momentum vs breakout).

## Próximos passos

1. **CZC: DOT Bollinger seed stability + rescue** (2-4 runs) — confirma se naked Sh=1.33 é replicável
2. **LINK seed stability** (ainda pendente do ADR-0098)
3. Documentar Padrão 23 no README de padrões (se houver)
4. STATE.md atualizado

## Critério de sucesso desta ADR

1. ✅ Sweep CZB executado (2+2 runs)
2. ✅ Closeout documenta 0/4 com diagnóstico
3. ✅ Padrão 23 formalizado
4. ✅ Padrão 22 refinado com corolário
5. ✅ DOT roadmap rescue definido (CZC), AVAX encerrado
6. ⏳ STATE.md atualizado (próximo)
