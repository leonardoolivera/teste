# SPEC.md — Bollinger 20/2 SOLUSDT 1h 180d (I.1)

> Gate: **pesquisa**. Primeiro piloto da **Série I** (mudança estrutural de família:
> mean-reversion). Primeiro piloto aberto já sob ADR-0025 (critério híbrido).

## Hipótese (§1)

**Em SOL 1h — ativo com volatilidade e dispersão maior que BTC/ETH (confirmado em H.10) —
uma estratégia de mean-reversion (Bollinger Bands, ADR-0026) captura edge onde Donchian
breakout não encontrou.** A intuição é estrutural: mean-reversion extrai alfa da componente
estacionária/oscilatória dos preços; breakout extrai da componente trending. SOL historicamente
alterna regimes; com filtro nenhum, Bollinger 20/2 deveria capturar a porção oscilatória enquanto
Donchian 20/10 captura a trending — dois alfas ortogonais sobre o mesmo tape.

Teste concreto da Série I: se mean-reversion cruza `hit_rate ≥ 45%` onde breakout não cruzou
(H.10: 31.07%), a hipótese "edge não existe nesta família" (Série H) é falsificada para o
universo de famílias causais sem filtro.

## Mercado (§2)

SOLUSDT spot, Binance Vision. Mesmo dataset usado em H.10 para permitir comparação ortogonal
família-a-família no mesmo tape.

## 3. Timeframe

1h OHLCV; 4320 barras; 2025-07-05 a 2025-12-31. Idêntico a H.10 (corte temporal preservado).

## Entradas (§4)

`ENTER_LONG` quando `close[t-1] < mu_now - 2·sigma_now` **E** `close[t-2] >= mu_prev - 2·sigma_prev`
(ADR-0026, cruzamento estrito da banda inferior). Edge-triggered: só dispara quando a barra
`t-1` cruzou *para dentro* da região oversold. `mu` e `sigma` (ddof=0) sobre janela de 20.
Long-only rígido (ADR-0026 §'Fica fora': short side fica para ADR futura).

## Saídas (§5)

`EXIT` quando `close[t-1] >= mu_now` **E** `close[t-2] < mu_prev` (cruzamento estrito da média).
Edge-triggered por simetria com a entrada. Arbitragem ordinal: EXIT antes de ENTER_LONG
(ADR-0026, consistente com ADR-0011). Em inputs reais `mu > mu - k·σ` sempre, então ambos nunca
disparam simultaneamente.

## 6-11-bis

- Sem stops (ADR-0015, convenção da série).
- `fracao=0.1, alav=2.0` (idêntico a H.1–H.10 para cross-family comparable).
- Custos H.1: `taker_fee_bps=5.0, slippage_bps_per_notional=2.0, spread_bps=0.0`.
- **Sem filtro de regime** (`--regime-filter none`) — baseline da família, ortogonal a H.7/H.9.

## 12-13

Warm-up: `len(window) >= window + 3 = 23` barras (ADR-0026). Bollinger precisa de `now_slice`
(20) + `prev_slice` (mais 1 barra antes) + 2 closes passados para edge detection.

Limitação: `num_std=2.0` em `window=20` é mais conservador que `num_std=1.5` usado em testes
unitários (ver comentário matemático em `test_bollinger_mean_reversion.py` — com N=5 e k=2.0 um
único outlier não pode cruzar a banda; com N=20 há margem porque outliers perturbam menos).

## Critério de refutação (sob ADR-0025)

Hard gate absoluto para `canary_only`:
1. `hit_rate baseline ≥ 45%` (critério 1).
2. `max_drawdown baseline ≤ 35%` (critério 2).
3. `spread+10 / baseline ≥ 0.95` (critério 3, monotonicidade bruta de custo).

Gate relativo para `paper_only`: **top-3 em `composite_score` (ADR-0024) com N ≥ 9 pilotos válidos**.

**Se 1 passa:** `canary_only` (primeiro canal na história do protocolo).
**Se 1 não passa E rank ∈ top-3:** `paper_only`.
**Senão:** `fail`.

**Experimento controlado:** `compare` I.1 (Bollinger SOL) ↔ H.10 (Donchian SOL) no mesmo dataset
→ 3 flags diff esperado (`strategy`, `bollinger_window`, `bollinger_num_std` vs `entry_window`,
`exit_window`). Ortogonalidade de família com tape compartilhado.
