# SPEC.md — MA Crossover 20/50 BTCUSDT 1h 180d (baseline)

> Gate ativo: **pesquisa**. Piloto H.2b — terceiro piloto agentic; exercita family diferente (MA crossover, ADR-0008 + ADR-0012) no mesmo mercado/período de H.1 (BTC 1h 180d) — permite comparação head-to-head via `alpha-forge compare` (ADR-0018). Primeiro uso real do subcomando `compare` pelo protocolo agentic.

## Hipótese (§1)

A estratégia **MA crossover long-only** com janelas `short_window=20` / `long_window=50`, operando sobre **BTCUSDT 1h 180d** com custos realistas (fee 5bps taker + slippage 2bps/unit_notional + spread 0bps), captura edge de trend-following suficiente para preservar capital em um regime de 2025-07-05 a 2025-12-31 (BTC em máximas históricas e consolidando).

Refrasando afirmativamente: "em 180 dias de BTC 1h, um trader que compra quando SMA(20) cruza SMA(50) para cima e vende quando cruza para baixo, com fracao 10% leverage 2x, termina com equity maior que 0.95 × capital inicial e hit_rate ≥ 45%".

**Relação com H.1 (Donchian BTC):** mesmo mercado, mesmo período, mesmo sizing, mesmos custos. Único eixo de diferença = family/parâmetros. Permite comparação head-to-head via `alpha-forge compare` (ADR-0018). Hipótese testável: "MA crossover tem edge onde Donchian puro não tem" (ou o oposto, ou nenhum). Resultado refuta ou confirma se o gap central é a family ou é estrutural (filtro de regime).

## Mercado (§2)

- **Ativo:** BTCUSDT (spot, venue = Binance Vision dumps — público, sem API de ordem).
- **Regime do período (observado):** BTC em consolidação de alta; janela de análise abrange fim do bull run de 2025 e começo de lateral/baixa. Mesmo período de H.1 por design.

## 3. Timeframe

- **Grão:** 1 hora (1h OHLCV).
- **Período total:** 2025-07-05 00:00 UTC a 2025-12-31 23:00 UTC (~180 dias, 4320 barras).

## Entradas (§4)

`ENTER_LONG` emitido quando SMA(20)(t-1) cruza para cima SMA(50)(t-1) — i.e., `short_prev ≤ long_prev` E `short_now > long_now`, ambos computados sobre fechamentos até `t-1` (causal por construção, ADR-0002).

## Saídas (§5)

`EXIT` (→ `FLAT`) emitido quando SMA(20)(t-1) cruza para baixo SMA(50)(t-1) — i.e., `short_prev ≥ long_prev` E `short_now < long_now`. Saída só por cross-down (sem stop fixo).

## 6. Stops

Sem stops explícitos (fora do escopo do núcleo mínimo — ADR-0008). Saída só acontece por cross-down.

## 7. Sizing

`fixed_fractional_position_sizing` (ADR-0004) com `fracao=0.1` (10% do capital por trade) e `alavancagem=2.0` → notional por trade = 0.1 × 10000 × 2 = **2000 USDT**. Idêntico a H.1/H.2a por design (único eixo de variação é a family).

## 8. Fees

`taker_fee_bps = 5.0` (0.05%). Idêntico a H.1/H.2a.

## 9. Slippage

`slippage_bps_per_unit_notional = 2.0` (ADR-0006). Slip efetivo ≈ **0.4 bps** por fill (notional/capital = 0.2). Idêntico a H.1/H.2a.

## 10. Spread (ADR-0019)

`spread_bps = 0.0` no baseline. Sensibilidade a spread testada via `cost_stress` com cenário `spread+10:0:0:10`.

## 11. Funding

N/A — spot.

## 12. Condições inválidas

- Warm-up: primeiras `long_window + 1 = 51` barras produzem `HOLD` até ter janela completa.
- `close[t-1]` com valor `NaN` ou barra ausente: dataset declara `declared_gaps: []`.
- Short side: `long_only=True` (ADR-0008 default). ADR-0012 short side não ativado.

## 13. Limitações conhecidas

- Dataset único (BTCUSDT) — robustez cross-asset depende de comparar com H.2e (se aberto) em ETH/SOL.
- Janela 180d é curta para trend-following.
- Parâmetros 20/50 são defaults da CLI (não tuned). ADR-0003 proíbe tuning dentro do walk-forward.
- Sem filtros de regime.

## Critério de refutação (explícito e auditável)

Boolean, idêntico em forma ao de H.1/H.2a (simetria intencional para comparação transversal via `compare`):

1. `hit_rate` do baseline cost_stress (4320 barras) **< 45%**.
2. `max_drawdown` do baseline **> 35%**.
3. `final_equity` do cenário `spread+10:0:0:10` **< 95% do baseline** (delta vs baseline < -5%).

**Relação esperada com H.1/H.2a:** propriedade estrutural `fee+Δbps ≡ spread+Δbps` (ADR-0019) deve replicar pela terceira vez (agora cross-family). `hit_rate` pode ser maior ou menor que 45% — MA crossover pega rompimentos diferentes de Donchian; é pergunta aberta.
