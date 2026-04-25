# SPEC.md — Donchian 20/10 BTCUSDT 1h 180d (symmetric long+short)

> Gate ativo: **pesquisa**. Piloto H.2c — quarto piloto agentic; primeiro uso protocolar do modo `--no-long-only` (ADR-0013). ADR-0013 ativa **reversal simétrico** (long E short, com reversão no breakout oposto, custo duplo via ADR-0012), não short-only. Fecha a matriz family×modo exercitada pelo protocolo: Donchian long-only ✓ (H.1/H.2a), MA crossover long-only ✓ (H.2b), Donchian simétrico ✗ → ✓ com este piloto. MA crossover simétrico fica como H.2+ futura.

## Hipótese (§1)

A estratégia **Donchian breakout simétrica** (`long_only=False`, ADR-0013 — reversal no breakout oposto, sem EXIT explícito; ADR-0012 aplica custo de reversão) com `entry_window=20` / `exit_window=10`, operando sobre **BTCUSDT 1h 180d** com custos realistas (fee 5bps taker + slippage 2bps/unit_notional + spread 0bps), captura edge em regimes heterogêneos (bullish + pullback) suficiente para preservar capital em um período de 2025-07-05 a 2025-12-31.

Refrasando afirmativamente: "em 180 dias de BTC 1h, um trader sempre posicionado (long no breakout de máxima, short no breakout de mínima, revertendo em cada sinal oposto), com fracao 10% leverage 2x, termina com equity maior que 0.95 × capital inicial e hit_rate ≥ 45%".

**Relação com H.1:** mesmo mercado, mesmo período, mesmos parâmetros (20/10), mesmo sizing, mesmos custos. Único eixo de diferença = modo (simétrico em vez de long-only). Permite comparação head-to-head via `alpha-forge compare` (ADR-0018) isolando o efeito do modo. Hipótese testável: "reversal duplica o número de trades (custo duplo ADR-0012) — o ganho do short em pullbacks compensa o custo extra?" Resultado orienta doutrina (reversal vs long-only).

## Mercado (§2)

- **Ativo:** BTCUSDT (spot, venue = Binance Vision dumps — público, sem API de ordem).
- **Regime do período (observado):** BTC em consolidação de alta; janela de análise abrange fim do bull run de 2025 e começo de lateral/baixa. Mesmo período de H.1 por design.

## 3. Timeframe

- **Grão:** 1 hora (1h OHLCV).
- **Período total:** 2025-07-05 00:00 UTC a 2025-12-31 23:00 UTC (~180 dias, 4320 barras).

## Entradas (§4)

Dois sinais de entrada (ADR-0013 §mapeamento simétrico):

- `ENTER_LONG` quando `high[t-1] > max(high[t-entry_window-1 : t-1])` (breakout bullish).
- `ENTER_SHORT` quando `low[t-1] < min(low[t-exit_window-1 : t-1])` (breakout bearish).

Ambos causais por construção (ADR-0002). Empates simultâneos resolvem-se para `ENTER_SHORT` (ADR-0013 §arbitragem conservadora — informação cronologicamente posterior).

## Saídas (§5)

**Sem `EXIT` explícito.** Fechamento ocorre por reversão: posição long vira short no próximo breakout bearish, e vice-versa. Engine aplica custo duplo (fee + slippage sobre close + open) via ADR-0012 reverse-on-signal. Posição `FLAT` só antes do primeiro sinal (warm-up).

## 6. Stops

Sem stops explícitos (ADR-0013 preserva ausência de stops da ADR-0011). Saída só por reversão do sinal oposto. Drawdown durante reversões é risco conhecido — cada reversão custa 2× fee + 2× slippage.

## 7. Sizing

`fixed_fractional_position_sizing` (ADR-0004) com `fracao=0.1` (10% do capital por trade) e `alavancagem=2.0` → notional por trade = 0.1 × 10000 × 2 = **2000 USDT**. Idêntico a H.1/H.2a/H.2b por design.

## 8. Fees

`taker_fee_bps = 5.0` (0.05%). Idêntico a H.1/H.2a/H.2b.

## 9. Slippage

`slippage_bps_per_unit_notional = 2.0` (ADR-0006). Slip efetivo ≈ **0.4 bps** por fill (notional/capital = 0.2). Idêntico a H.1/H.2a/H.2b.

## 10. Spread (ADR-0019)

`spread_bps = 0.0` no baseline. Sensibilidade a spread testada via `cost_stress` com cenário `spread+10:0:0:10`.

## 11. Funding

N/A — spot. Short em spot é simulação (não há funding de short perpétuo porque não há perpétuo); reflete custo de venda a descoberto zero, o que é **otimista** em prod real. Limitação declarada em §13.

## 12. Condições inválidas

- Warm-up: primeiras `max(entry_window, exit_window) + 2 = 22` barras produzem `HOLD` até ter janela completa.
- `close[t-1]` com valor `NaN` ou barra ausente: dataset declara `declared_gaps: []`.
- Mode: `long_only=False` (ADR-0013). Sem `EXIT`; reversal long↔short coordenado pela engine (ADR-0012).

## 13. Limitações conhecidas

- **Short em spot é aproximação otimista.** Não modela custo de borrow, funding de perpétuo, ou indisponibilidade de liquidez short. Resultado é upper-bound; prod real seria pior.
- **Reversal duplica o custo efetivo por evento de flip.** ADR-0012 aplica fee+slippage em ambos (close anterior + open novo) — ADR-0019 property continua válida mas com notional/capital efetivamente 2x no evento de reversão.
- Dataset único (BTCUSDT) — cross-asset mode simétrico não exercitado neste piloto.
- Janela 180d é curta para trend-following.
- Parâmetros 20/10 são defaults da CLI (não tuned). ADR-0003 proíbe tuning dentro do walk-forward.
- Sem filtros de regime.

## Critério de refutação (explícito e auditável)

Boolean, idêntico em forma ao de H.1/H.2a/H.2b (simetria intencional para comparação transversal via `compare`):

1. `hit_rate` do baseline cost_stress (4320 barras) **< 45%**.
2. `max_drawdown` do baseline **> 35%**.
3. `final_equity` do cenário `spread+10:0:0:10` **< 95% do baseline** (delta vs baseline < -5%).

**Relação esperada com H.1/H.2a/H.2b:** propriedade estrutural `fee+Δbps ≡ spread+Δbps` (ADR-0019) deve replicar **pela quarta vez** (agora cross-mode). Reversal aproximadamente dobra o número de trades (167 observados vs 110 em H.1) — custo duplo por flip amplifica sensibilidade a cenário fee+10 e spread+10 (esperado Δ% maior que H.1 em módulo). Pergunta aberta: reversal captura lado short o suficiente para compensar o custo duplo, ou sangra em whipsaws típicos de consolidação?
