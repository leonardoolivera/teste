# SPEC.md — Donchian 20/10 ETHUSDT 1h 180d (baseline)

> Gate ativo: **pesquisa**. Piloto H.2a — segundo piloto agentic exercitando robustez cross-asset do protocolo reusando Donchian 20/10 long-only (ADR-0011) sobre ETH no mesmo período de H.1. Hipótese é simétrica à de H.1 por design (único eixo de diferença = ativo), para permitir comparação transversal direta.

## Hipótese (§1)

A estratégia **Donchian breakout long-only** com janelas `entry_window=20` / `exit_window=10`, operando sobre **ETHUSDT 1h 180d** com custos realistas (fee 5bps taker + slippage 2bps/unit_notional + spread 0bps), captura edge de trend-following suficiente para preservar capital em um regime de 2025-07-05 a 2025-12-31.

Refrasando afirmativamente: "em 180 dias de ETH 1h, um trader que compra em rompimento de 20-barras e vende em rompimento-baixo de 10-barras, com fracao 10% leverage 2x, termina com equity maior que 0.95 × capital inicial e hit_rate ≥ 45%".

**Relação com H.1:** hipótese idêntica em estrutura (mesma estratégia, mesmo período, mesmas janelas, mesmos custos, mesmo critério de refutação) — único eixo de diferença é o ativo (ETH vs BTC). Resultado simétrico reforça a lição de H.1 (gap = regime, não ativo); resultado dissonante indica que a conclusão de H.1 é ativo-dependente e abre piloto H.2d (SOL).

## Mercado (§2)

- **Ativo:** ETHUSDT (spot, venue = Binance Vision dumps — público, sem API de ordem).
- **Regime do período (observado):** ETH em consolidação pós-all-time-high; janela de análise abrange fim do bull run de 2025 e começo de lateral/baixa. Correlação estrutural alta com BTC (mesma window), mas drawdowns tipicamente maiores por ser mid-cap vs BTC.

## 3. Timeframe

- **Grão:** 1 hora (1h OHLCV).
- **Período total:** 2025-07-05 00:00 UTC a 2025-12-31 23:00 UTC (~180 dias, 4320 barras).

## Entradas (§4)

`ENTER_LONG` emitido quando `close[t-1]` rompe `max(high[t-20..t-1])` (exclusivo — rompimento estrito; ADR-0011 §Entradas).

## Saídas (§5)

`EXIT` (→ `FLAT`) emitido quando `close[t-1]` rompe `min(low[t-10..t-1])` para baixo. `exit_window < entry_window` é a assimetria-chave da Donchian (sair mais cedo que entrar).

## 6. Stops

Sem stops explícitos (fora do escopo do núcleo mínimo — ADR-0011 §"Fica explicitamente fora"). Saída só acontece por rompimento-baixo de 10-barras.

## 7. Sizing

`fixed_fractional_position_sizing` (ADR-0004) com `fracao=0.1` (10% do capital por trade) e `alavancagem=2.0` → notional por trade = 0.1 × 10000 × 2 = **2000 USDT**.

## 8. Fees

`taker_fee_bps = 5.0` (0.05%) — alinhado com tier taker default da Binance spot em 2025.

## 9. Slippage

`slippage_bps_per_unit_notional = 2.0` (ADR-0006). Fórmula: `slip_bps = 2 × (notional / capital_inicial)` — como fracao×alavancagem=0.2, slip efetivo ≈ **0.4 bps** por fill.

## 10. Spread (ADR-0019)

`spread_bps = 0.0` no baseline — hipótese de venue com spread insignificante. Sensibilidade a spread é testada explicitamente via `cost_stress` com cenário `spread+10:0:0:10` (spread de 10bps).

## 11. Funding

N/A — estratégia opera em **spot** (Binance Vision spot dumps). Funding rates são perpetual-only; fora de escopo.

## 12. Condições inválidas

- Warm-up: primeiras `entry_window = 20` barras produzem `HOLD` até ter janela completa de 20 highs passados disponíveis.
- `close[t-1]` com valor `NaN` ou barra ausente: dataset `ethusdt_1h_20250705_20251231_binance_spot` declara `declared_gaps: []` — sem gaps; condição não se manifesta neste recorte.
- Short side: `long_only=True` (ADR-0011 default, confirmado — ADR-0013 short side NÃO ativado neste piloto).

## 13. Limitações conhecidas

- Dataset único (ETHUSDT) — robustez cross-asset depende de comparar com H.1 (BTC); SOL fica para H.2d se necessário.
- Janela 180d é curta para trend-following — regimes de bull sustentado são sub-representados.
- Sem tuning de hiperparâmetros — janelas 20/10 são os defaults da ADR-0011 (mesmo valor usado em H.1 por simetria).
- Sem filtros de regime — todos os rompimentos são tratados uniformemente; lição pendente de H.1.

## Critério de refutação (explícito e auditável)

Boolean, idêntico em forma ao de H.1 (intencional — simetria permite comparação transversal). O piloto é **refutado** (release_decision = `fail`) se qualquer uma das três condições for observada na validação:

1. `hit_rate` do baseline cost_stress (4320 barras) **< 45%**.
2. `max_drawdown` do baseline **> 35%**.
3. `final_equity` do cenário `spread+10:0:0:10` **< 95% do baseline** (i.e., delta vs baseline < -5% em bps de equity).

**Relação esperada com H.1:** propriedade estrutural `fee+Δbps ≡ spread+Δbps` em impacto de equity (ADR-0019) deve se manter — se H.2a mostrar divergência, é bug de execução ou mudança silenciosa de CostModel. A `hit_rate`/`final_equity` podem divergir em magnitude mas não em sinal (ambos resultados abaixo dos thresholds ou ambos acima).
