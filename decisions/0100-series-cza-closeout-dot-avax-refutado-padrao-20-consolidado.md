# 0100 — Série CZA closeout: DOT/AVAX 2025-H2 refutados ambas as engines (naked + filter) — Padrão 20 consolidado

**Status:** Accepted — closeout
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0099 (CZA pré-registro), ADR-0098 (CZ closeout), Padrão 12 + 19 + 20

## Resultado

**0/2 PASS.**

| Tag | Asset | Trades | PnL% | MDD% | Sh | Naked Sh | Delta | MCp5 | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| CZA.1 | DOT | 96 | +5.22 | 6.47 | 0.901 | 0.498 | +0.403 | 9071 | FAIL (Sh<1.0, MCp5<9500) |
| CZA.2 | AVAX | 90 | +1.76 | 8.18 | 0.377 | -0.054 | +0.431 | 8851 | FAIL (Sh<1.0, MCp5<9500, PnL<3%) |

### Análise de delta
- Filter **melhora** ambos (+0.40 e +0.43), mostrando que há algum efeito positivo.
- Mas delta **< +0.5** (threshold Padrão 12 para load-bearing) e Sh absoluto **< 1.0** (Gate 1).
- Não passa nem o gate de load-bearing nem o gate de PASS isolado.

### Comparação com outras tentativas de filter rescue
| Série | Asset | Window | Naked Sh | Filter Sh | Delta | Verdict |
|---|---|---|---|---|---|---|
| CW.2 | ETH | 2024-H2 | 0.651 | 1.774 | +1.12 | PASS (v7) |
| CW.1 | BTC | 2024-H2 | 0.89 | ~1.5 | — | FAIL trade count |
| CZA.1 | DOT | 2025-H2 | 0.498 | 0.901 | +0.40 | FAIL |
| CZA.2 | AVAX | 2025-H2 | -0.054 | 0.377 | +0.43 | FAIL |

Filter rescue funciona com **delta ≥ +1.0** (ETH 2024-H2 com +1.12). Delta menores (~+0.4) são consistentes com "filter efetivo em cortar ruído mas não revelar edge onde não há".

### Por que DOT/AVAX refutam mesmo com filter?
Três interpretações consistentes com os dados:
1. **Ausência de edge estrutural**: se naked Sh fica perto de zero (AVAX=-0.05), filter corta ruído mas não cria edge. ETH 2024-H2 tinha Sh=0.65 naked (edge presente mas diluído); DOT/AVAX tem Sh=0 (edge ausente).
2. **Regime unfavorável específico**: altcoins em 2025-H2 tiveram talvez trend sustentado que RSI short não captura, nem com filter.
3. **Mercado muito volátil, filter width não discrimina**: trade count pós-filter quase igual ao naked (96 vs 86 em DOT, 90 vs 95 em AVAX), sinalizando que width >300bps era quase sempre satisfeito — filter praticamente inativo. Diferente de majors 2025-H1 onde filter corta ~40-50% dos sinais.

Hipótese 3 é forte: se filter não filtra, não resgata. Testar width=600 ou 900 poderia ser próximo passo, mas o custo-benefício é baixo (hipótese especulativa sem prior forte).

## Padrão 20 consolidado

Acumulando CZ + CZA em 2025-H2 short-side:

| Asset | Naked | +width(300) |
|---|---|---|
| BTC | 1.64 PASS | — (herdado v4a-like) |
| ETH | ? (não testado) | 0.81 FAIL (CH.8, legado) |
| SOL | 2.30 PASS | 1.92 FAIL (filter prejudica) |
| DOT | 0.50 FAIL | 0.90 FAIL |
| AVAX | -0.05 FAIL | 0.38 FAIL |
| LINK | 1.76 PASS | ? (não testado) |

**3/6 ativos PASS em alguma configuração (BTC, SOL, LINK).** DOT, AVAX, ETH: refutados em 2025-H2 curto-side.

**Refino final Padrão 20:** crypto 1h short-side tem edge em **50-60% dos ativos** testados, seletivo por ativo. Filter não resgata asset sem edge naked. Padrão 12 (filter load-bearing) reconfirmado — filters só funcionam quando há edge latente para amplificar/revelar.

## Padrão 22 (NOVO) — Filter não cria edge onde não existe naked signal

**Enunciado:** Se Sh(naked) ≈ 0 (em qualquer direção), filter rescue é improvável de levar a PASS. Load-bearing rescue requer Sh(naked) ≥ ~0.5 como sinal latente para amplificar.

**Evidência (cross-serie):**
- ETH 2024-H2 long: naked 0.65 → filter 1.77 = +1.12 (PASS)
- SOL 2025-H1 short naked baixo → +trend 1.96 (PASS; mas com filter direcional correto, não width)
- DOT 2025-H2 naked 0.50 → filter 0.90 = +0.40 (FAIL, insuficiente)
- AVAX 2025-H2 naked -0.05 → filter 0.38 = +0.43 (FAIL, base zero)

**Implicação:** antes de investir em filter rescue, checar naked Sh. Se < 0.4, prior forte de FAIL mesmo com filter. Use CZA como prior negativo: delta ≤ +0.5 é comum quando naked é muito baixo.

## Decisão

### Não promove nada
Nenhum combo CZA entra em stack.

### DOT/AVAX 2025-H2 encerrado
Ambas engines testadas (naked + width filter). Outro filter (trend_htf) em backlog mas prior fraco (CR 0/2 em cross-asset com trend, Padrão 14).

### Stack inalterado
14 combos (5 long + 9 short). v8 continua como último release.

### Bridge
**Sem post** — signal-only, sem mudança de stack.

## Backlog atualizado

Ordenado por EV/custo:
1. **LINK seed stability** — CZ.3 rerun com seeds 1337+2024, 2 runs rápidos. Custo baixo, alto valor (valida se LINK não é fluke). **Recomendação**.
2. **LINK replicação cross-window** — RSI naked em LINK 2024-H2 ou 2025-H1 (datasets novos), 1-2 runs. Mid-EV.
3. **Meta-correlação expandida 2025-H2** — r(BTC, SOL, LINK) para v8, ~5min. Baixo custo.
4. CZB: Bollinger short + width em DOT/AVAX 2025-H2 — outra engine como rescue. Prior fraco dada CZA.
5. Normalizar schema v2 Bollinger long (débito técnico, 5min).

## Critério de sucesso desta ADR

1. ✅ Sweep CZA executado (2 runs)
2. ✅ Closeout documenta 0/2
3. ✅ Padrão 22 formalizado
4. ✅ Padrão 20 refinado final (seletivo ~50-60% cross-asset)
5. ✅ Sem promoção, stack inalterado
6. ⏳ STATE.md atualizado (próximo)
