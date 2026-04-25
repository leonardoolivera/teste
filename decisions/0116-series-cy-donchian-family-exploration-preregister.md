# 0116 — Série CY pré-registro: Donchian breakout family exploration (nova engine)

**Status:** Pre-registered
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** backlog item 3 (nova family engine)

## Motivação

Stack atual 100% concentrado em RSI + Bollinger (mean-reversion). Falta de diversificação por engine: risco cross-combo corr alto em periodos de stress (regime-shifts hostis a mean-reversion). Donchian breakout é **momentum** puro (direção oposta ao stack atual), candidato natural a 3ª family.

## Escopo

6 runs, DonchianBreakoutStrategy(20, 10) long_only=true, 3 ativos × 2 janelas:

| Tag | Asset | Window | Regime | Hypothesis |
|---|---|---|---|---|
| CY.1 | BTC | 2024-H2 | bull | Momentum em bull → forte candidato |
| CY.2 | ETH | 2024-H2 | bull | idem |
| CY.3 | SOL | 2024-H2 | bull | idem |
| CY.4 | BTC | 2025-H2 | misto | Probe: Donchian em misto |
| CY.5 | ETH | 2025-H2 | misto | idem |
| CY.6 | SOL | 2025-H2 | misto | idem |

Params 20/10 são breakout canonical Turtle Trading. Hipótese: bull regime (2024-H2) favorável; misto (2025-H2) é desafio.

## Gates pré-registrados (probe, relaxados)

Por combo:
- **Hit forte**: Sh ≥ 1.0 + trades ≥ 30 + PnL > 3% + MC p5 > 9500 (gate full stack)
- **Hit probe**: Sh ≥ 0.5 + trades ≥ 15 + PnL > 0 (sinaliza potencial)
- **Miss**: Sh < 0.5 ou trades < 15 ou PnL ≤ 0

Agregado:
- ≥2/6 hit forte em ≥1 ativo distinto → **abrir série CV** validação dedicada + possível manifest v9 Donchian
- 3/6 hit probe → **inconclusive**: Donchian tem potencial mas não replica robustly
- ≤1 probe total → **refutação preliminar**: Donchian 20/10 não é candidato; tentar outros params (40/20) em próxima probe

## Cross-engine correlação (hipotético, a medir se PASS)

Se CY produzir combo Donchian PASS no mesmo ativo/janela de combo RSI/Bollinger existente, medir correlação bar-a-bar. Expectativa: < 0.3 (diferentes signal-driving mechanics). Se < 0.3 → valor diversificador alto; se > 0.5 → engines correlacionados apesar de diferentes.

## Não-alvo

- Não otimizar params (20/10 só)
- Não testar short side (long_only=true)
- Não testar 1 ano completo (só 6m windows)
- Não promover nada sem CV follow-up

Timebox: 6 runs ~10-15min wall. ADR-0117 closeout.
