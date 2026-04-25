# 0094 — Série CX closeout: Donchian breakout naked refutado 0/9 cross-period cross-asset (Padrão 21)

**Status:** Accepted — closeout
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0093 (CX pré-registro), ADR-0030 (runtime-faithful), Padrão 20 (short-only naked = edge em crypto major 1h)

## Resultado

**0/9 PASS.** Refutação completa em todos os 9 pares (asset × window).

| Tag | Asset | Window | Trades | PnL% | MDD% | Sh | MCp5 | costr | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| CX.1 | BTC | 2024-H2 | 159 | -6.47 | 7.28 | -1.667 | 8393 | 0.9105 | FAIL |
| CX.2 | ETH | 2024-H2 | 160 | -6.72 | 9.37 | -1.381 | 8172 | 0.9123 | FAIL |
| CX.3 | SOL | 2024-H2 | 166 | -12.62 | 13.53 | -2.158 | 7201 | 0.9020 | FAIL |
| CX.4 | BTC | 2025-H1 | 152 | -0.51 | 5.35 | -0.096 | 8974 | 0.9156 | FAIL |
| CX.5 | ETH | 2025-H1 | 159 | -3.25 | 7.85 | -0.482 | 7972 | 0.9136 | FAIL |
| CX.6 | SOL | 2025-H1 | 171 | -16.60 | 21.99 | -2.504 | 6152 | 0.9081 | FAIL |
| CX.7 | BTC | 2025-H2 | 167 | -8.33 | 9.70 | -2.729 | 8372 | 0.8966 | FAIL |
| CX.8 | ETH | 2025-H2 | 152 | -6.14 | 11.02 | -1.201 | 8250 | 0.9225 | FAIL |
| CX.9 | SOL | 2025-H2 | 161 | -14.10 | 17.10 | -2.536 | 7192 | 0.9009 | FAIL |

PASS count: **0/9**. Todos Sh<0, todos MC p5<9500, todos cost_r<0.95.

## Análise

### Diagnóstico do colapso
1. **Turnover absurdo**: 152-171 trades em 6 meses = ~1 trade/dia. Whipsaws constantes em qualquer regime. Ponto pior: SOL (asset mais volátil, mais quebras falsas).
2. **Cost_r ~0.90 em todos**: -10% de PnL só por custo de transação no stress +10bps. Ratifica que turnover é o killer estrutural, não apenas regime.
3. **Reverse-on-signal (ADR-0013)**: cada breakout oposto reverte posição = double-cost (ADR-0012). Donchian dispara breakouts contrários frequentes, multiplicando custos.
4. **MC p5 < 9500 em 100%**: bootstrap confirma que retornos são fundamentalmente negativos, não ruído.
5. **PnL pior em ativo mais volátil**: SOL -12 a -16%, ETH -3 a -6%, BTC -0.5 a -8%. Ordem de volatilidade alinha com magnitude de loss.

### Comparação com RSI naked short (Gate 2)
RSI naked (audit-v4-b 2025-H2): BTC Sh=2.63 PASS, SOL Sh=2.30 PASS.
Donchian naked (CX 2025-H2): BTC Sh=-2.73, SOL Sh=-2.54.

**Delta = -5+ Sharpe**. Não é só pior — é catastroficamente oposto. Engine family **trend-following/breakout** é incompatível com crypto major 1h naked, enquanto **mean-reversion** (RSI/Bollinger) funciona naked em short-side.

## Padrão 21 (NOVO) — Breakout naked é refutável em crypto major 1h

**Enunciado:** Engine breakout/trend-following puro (Donchian, momentum cross, etc) **sem filtro de regime** falha sistematicamente em crypto major 1h por turnover excessivo + whipsaw em qualquer regime (bull/bear/chop). Magnitude de loss escala com volatilidade do ativo (SOL > ETH > BTC).

**Implicação:** breakout só pode entrar no stack via filtro de regime que mate setups em chop/contra-tendência (ex: ADX>25, slope HTF aligned, volatilidade expansiva). Não é "filter-rescued opcional" — é **mandatório**.

**Padrão 21 não contradiz Padrão 20.** Padrão 20 diz: "long naked falha, short naked funciona". Padrão 21 refina por engine family: "naked funciona apenas em mean-reversion short-side". Trend-following naked falha em ambas direções.

## Riscos antecipados confirmados

Da ADR-0093:
1. ✅ "Donchian em chop puro tende FAIL" — confirmado em 2025-H1 (chop) com Sh -0.10 a -2.50.
2. ❌ "Trade count baixo" — falsa hipótese; veio o oposto, count altíssimo (152-171).
3. ✅ "Reverse-on-signal + double cost mata edge líquido" — cost_r 0.90 confirma.
4. ✅ "Breakout em 2024-H2 bull (ruim short-perna)" — confirmado: Sh -1.4 a -2.2 em 2024-H2.

## Decisão

### Não promove v8 (zero PASS).
Donchian naked não entra no stack.

### Próximas opções
| Opção | Esforço | Probabilidade |
|---|---|---|
| **A. CY: Donchian + filter (trend_htf, ADX, vol regime)** | 9-18 runs | Médio — filter pode rescue, mas turnover ainda alto |
| **B. Donchian(40,20) ou (55,20) — turnover menor** | 9 runs | Baixo-médio — clássico Turtle 55/20, menos sinais mas direção semelhante |
| **C. Abandonar Donchian, testar outra engine** (MA crossover, MACD se existir) | 3-9 runs | Médio — diversificação family ainda em aberto |
| **D. Pausar engine-new, ir para item 4 (ingest tooling) ou item 1 (consolidação)** | 0 | Default produtivo |

**Recomendação:** **D agora**, com **C/B em backlog**. CY (Donchian+filter) tem custo médio e probabilidade só média — antes de investir nisso, vale ingest tooling (desbloqueia DOT/AVAX/LINK + 4h windows) que multiplica espaço de teste para todas as engines existentes. Depois revisita Donchian com mais janelas.

## Critério de sucesso desta ADR

1. ✅ Sweep CX executado (9 runs)
2. ✅ Closeout documenta verdict 0/9
3. ✅ Padrão 21 formalizado (breakout naked refutável em crypto major 1h)
4. ✅ Não promove v8
5. ⏳ STATE.md atualizado (próximo)
6. ⏳ Bridge: signal-only — sem mudança de stack, **não posta** (silêncio = sem novo manifest)
