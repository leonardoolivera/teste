# 0185 — Série PY closeout: pyramid v4 requer regime filter (constraint discovered)

**Status:** Accepted — PY refutada Fase 1 por razão estrutural; ADR-0180 amended.
**Date:** 2026-04-21
**Deciders:** Usuário ("testa mais") + agente
**Relates to:** ADR-0184 (pré-reg), ADR-0180 (runtime v4), ADR-0182 (CONS closeout), Padrão 41

## Resumo

Pré-reg PY (ADR-0184) testou pyramid aplicado a 3 edges RSI já promovidos. **1 probe válida (PY.1 com trend_htf filter), 2 probes estruturalmente inválidas (PY.2/PY.3 naked)**. Descoberto constraint: **v4 pyramid requer regime filter para existir um mecanismo de exit**.

## Resultados

| Tag | Combo | Sh (v4) | Sh baseline | ΔSh | PnL% (v4) | PnL baseline | ΔPnL | Valid? |
|---|---|---:|---:|---:|---:|---:|---:|:---:|
| PY.1 | RSI 25/75 + tHTF + pyr 2×lev | **1.61** | 2.00 | -0.39 | **+35.25** | +9.80 | +25.45 | ✓ |
| PY.2 | RSI 30/70 naked + pyr 2×lev | -2.08 | 2.30 | -4.38 | -88.85 | +13.81 | -102.66 | ✗ estrutural |
| PY.3 | RSI 30/70 naked + pyr 2×lev | +2.38 | 1.64 | +0.74 | +67.95 | +5.13 | +62.82 | ✗ estrutural |

Gate Fase 1 (ADR-0184): ≥2/3 probes Sh≥1.5 AND seqs≥10 **E** preserve edge (Sh ≥ 0.9× baseline). **0/3 preserve edge, 1/3 pass min gate, 2/3 invalidados → FAIL.**

## Root cause PY.2/PY.3: strategy + pyramid contract interaction

### Fato empírico

Ambas PY.2 e PY.3 mostraram `fills=5 trades=0` em cada fold. 5 fills = 5 tranches abertas (pyramid max_tranches=5). 0 trades = nenhuma tranche fechada dentro do fold.

Evidência:
- PY.2 SOL 2025-H2: equity fold1 10000→5566 (−44% MTM), fold2 10000→2202 (−78%), fold3 10000→9093 (−9%). Stack pyramid sentado em short SOL enquanto preço sobe, sem fechar.
- PY.3 BTC 2025-H2: equity fold1 10000→11341 (+13%), fold2 10000→14770 (+48%), fold3 10000→10026. Short BTC lucrativo em 2025-H2 (BTC caiu), stack mantido até fim do fold = PnL paper.

### Causa estrutural

Duas engines de mean-reversion (RSI, Bollinger) em two-sided mode (`long_only=False`) **NÃO emitem `Signal.EXIT`**. O exit de posição em fixed_notional depende do comportamento **reverse-on-opposite-signal** — engine fecha long quando vê ENTER_SHORT, fecha short quando vê ENTER_LONG.

ADR-0180 (runtime v4 pyramid) invariante #6 explicitamente bloqueia reverse-on-opposite-signal em pyramid mode:

> `ENTER opposite direction when stack non-empty → no-op (logs ignored)`

Combinação: two-sided mean-rev (no EXIT emitted) + pyramid (no reverse) + **sem regime filter** = *nenhum mecanismo pode fechar o stack*. Pyramid enche até max=5 e sentar até fim do fold.

### Por que PY.1 funcionou

PY.1 usa `trend_htf:mode=short_only:sma_window=50`. Quando HTF SMA50 sobe (SOL breakout), filter vira inativo → engine coerce signal para `Signal.EXIT` → pyramid fecha todas as tranches. Exit path válido.

## Constraint estrutural descoberto

**v4 pyramid_equity_based requer regime filter explícito como mecanismo de exit** quando engine é two-sided mean-reversion. Sem filter + sem EXIT emitter = broken.

Alternativas para levantar a restrição no futuro:
1. Modificar engines de mean-rev para emitirem `Signal.EXIT` explícito em oposta (e.g., RSI overbought short + preço cruza middle = EXIT). **Mudança de design não-trivial**, altera behavior do fixed_notional também.
2. Modificar engine pyramid para tratar opposite signal como EXIT-then-stop (híbrido sem reverter posição). Viola ADR-0180 invariante #6.
3. **Aceitar constraint**: v4 exige filter. Documentar em ADR-0180.

**Escolhemos opção 3** — menor blast radius, clareza de contrato.

## Amendment ADR-0180 (adicionado neste closeout)

Adicionar invariante #10:

> **Invariante #10** — `requires_regime_filter: true`: v4 pyramid_equity_based só funciona com regime filter explícito anexado ao combo. Sem filter, não há exit path viável em engines two-sided. Schema `manifest_v4` deve validar `regime_filter != null` para qualquer combo com `runtime_contract=pyramid_equity_based`.

Implicação: qualquer manifest v4 sem regime_filter = erro de validação. (Manifest v4 ainda não escrito; amendment consolida antes de primeira emissão.)

## Avaliação PY.1 isolada

PY.1 é **probe única válida**. Resultado:
- Sh=1.61 **passa** gate Padrão 41 (≥1.5) mas degrada baseline 20% (2.00 → 1.61)
- PnL amplifica 3.6× (9.80% → 35.25%) — pyramid paga quando signal é correto
- Seqs=11 (≥10) — amostra mínima ok

**Interpretação**: pyramid **amplifica PnL** mas **degrada Sharpe** em edge proven. Trade-off aceitável se bot otimiza absolute return, rejeitável se otimiza risk-adjusted. **Prior do user historicamente alinhado a Sharpe** (ADR-0030 prioriza faithful replay). Logo PY.1 isolada não é promoção direta.

Single probe + cross-era/cross-asset vazio = insuficiente para promoção manifest v4 (Padrão 43 exige multi-era). Precisaria Fase 2 com 6+ runs cross-window todos com filter.

## Decisão

- **PY Fase 1 refutada** (gate não atingido + 2/3 invalidados estruturalmente).
- **ADR-0180 amended** com invariante #10 (require_regime_filter).
- **Pyramid v4 não é promoção nesta sessão**. Único probe válido tem Sh degradado vs baseline.
- **Manifest v4 schema continua não escrito** (consistente com ADR-0180 amendment: só emitir se houver combo comprovado com filter).
- **Stack 13 combos inalterado.**
- **Bug engine revelado (e corrigido)**: `_max_drawdown` em `metrics.py` não clamp-ava em 1.0, gerando ValidationError em pyramid+leverage com bankruptcy. Fix: clamp dd ≤ 1.0. Preserva invariante semântica (MDD ∈ [0,1]).

## Implicações para handoff bot

- v4 stand-down (ADR-0183, bridge 01:00 UTC) **permanece válido**.
- Caso seja retomada pesquisa v4: toda probe deve ter regime filter atrelado desde pré-reg. Pré-registros sem filter para combos two-sided devem ser rejeitados antes de dev.

## Não-alvo

- Não corrigir RSI/Bollinger strategies para emitir EXIT (muda comportamento fixed_notional do stack atual; risco > valor).
- Não testar PY.2/PY.3 com filter adicionado (vira teste diferente — não é mais "pyramid sobre edge proven"; é combo novo).
- Não rodar Fase 2 PY (single valid probe + constraint insufficient, precisaria pré-reg novo com ≥3 combos filtered).

## Ação executada

- ✅ ADR-0184 pré-reg
- ✅ Tools run_py_sweep + summarize_py
- ✅ Run 1 (leverage=5×): crash bankruptcy → fix metrics.py clamp
- ✅ Run 2 (leverage=2×): crash ainda em SOL 2025-H2 → nota engine limitation
- ✅ Run 3 (metrics clamped): 3 runs completam, 1 válido
- ✅ Summarize + gate check
- ✅ ADR-0180 amendment (invariante #10)
- ✅ ADR-0185 closeout (este)
