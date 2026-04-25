# 0093 — Série CX pré-registro: Donchian breakout short cross-period (nova engine family)

**Status:** Accepted — pré-registro
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0092 (v7 ativado), ADR-0030 (runtime-faithful), Padrão 20 (short-only naked em crypto major 1h)

## Hipótese

Stack atual usa só Bollinger + RSI (mean-reversion families). **Donchian breakout** é filosoficamente oposto (momentum/trend-following). Diversifica family ao nível estrutural, não só parâmetro.

Donchian short dispara quando low[t-1] < min(lows[t-exit_window-1:t-1]) → captura **quebras de suporte**. Engine curto-biased por design. Deve funcionar melhor em janelas bearish/chop (2024-H2 teve flushes, 2025-H1 chop com breakdowns, 2025-H2 misto).

Padrão 20 prevê short-only = edge. Confirmação esperada; refutação seria surprise (breakout short em crypto tende a funcionar em flushes).

## Design

**Parâmetros canônicos:** Donchian(entry=20, exit=10) — clássico Turtle Traders.
Modo: long_only=false (reverse-on-signal ADR-0013 ativo) — mas como buscamos short-side naked, vou restringir via filter ou forçar só um lado.

**Decisão de parametrização:** rodar Donchian(20,10) com `long_only=false`. Engine dispara long (bullish) e short (bearish) alternadamente via reverse. Pós-analisar separando pernas long vs short se preciso. Alternativa mais simples: filtro que mate long (trend_htf short_only). Vamos com long_only=false naked primeiro — se Sh global passar, assume simetria. Se FAIL, investigar só perna short.

**Pilotos (9 runs cross-period cross-asset):**

| Tag | Symbol | Window |
|---|---|---|
| CX.1 | BTCUSDT | 2024-H2 |
| CX.2 | ETHUSDT | 2024-H2 |
| CX.3 | SOLUSDT | 2024-H2 |
| CX.4 | BTCUSDT | 2025-H1 |
| CX.5 | ETHUSDT | 2025-H1 |
| CX.6 | SOLUSDT | 2025-H1 |
| CX.7 | BTCUSDT | 2025-H2 |
| CX.8 | ETHUSDT | 2025-H2 |
| CX.9 | SOLUSDT | 2025-H2 |

Runtime invariants ADR-0030 (faithful, fixed_notional=2000). Naked (sem filter).

Total: 9 runs (~22min).

## Gates pré-registrados

### Gate 1 — Passes isolados
Sh≥1.0, trades≥30, MDD≤20%, MC p5>9500, cost_r≥0.95, PnL>3%.

### Gate 2 — Comparação com RSI naked short em mesma janela/ativo
RSI naked short resultados disponíveis (audit-v4-b):
- BTC 2025-H2: Sh=2.63 PASS
- SOL 2025-H2: Sh=2.30 PASS
- (outras janelas não auditadas naked)

Gate informacional: Donchian PASS + similar ou superior a RSI = engine diversificadora válida. Donchian PASS mas Sh << RSI = redundante (RSI domina).

### Gate 3 — Promoção v8 candidato
≥1 PASS → emite `donchian_breakout_<combo>.json`. Se 2-3+ PASS, manifest multi-combo robusto.

### Gate 4 — Correlação vs stack existente
Se PASS, calcular correlação Pearson retornos bar-a-bar vs combos existentes na mesma janela. Se r<0.5 em todos, diversificação real. Se r>0.7 vs RSI/Bollinger do mesmo ativo, redundância — decidir se promove.

## Riscos antecipados

1. **Donchian em chop puro tende FAIL** — breakouts em lateral viram whipsaws. 2025-H1 chop pode destruir Sh.
2. **Trade count baixo** — Donchian(20) dispara menos que RSI. Gate ≥30 pode ser apertado em 6 meses.
3. **Reverse-on-signal + double cost (ADR-0012)** — Donchian reverte em cada breakout oposto. Custo de turnover pode matar edge líquido.
4. **Breakout é trend-following; 2024-H2 foi bull (ruim para short-perna), 2025-H2 misto (ambíguo)** — só 2025-H1 é teoricamente favorável.

## Interpretação dos resultados possíveis

| Cenário | Verdict | Ação |
|---|---|---|
| ≥3 PASS cross-period | Donchian generaliza, engine diversificadora | promove v8 multi-combo |
| 1-2 PASS + baixa correlação vs RSI | diversificadora parcial | promove v8 marginal, monitora |
| 1-2 PASS + correlação alta | redundante | não promove, documenta |
| 0 PASS | engine não funciona naked em crypto major 1h | testa com filter depois (CY) ou abandona |

## Critério de sucesso desta ADR

1. Sweep CX executado
2. ADR-0094 closeout documenta verdict
3. Se promoção: v8 manifest emitido
4. Se refutação naked: decidir abrir CY filter-rescued ou encerrar Donchian
5. STATE.md atualizado
