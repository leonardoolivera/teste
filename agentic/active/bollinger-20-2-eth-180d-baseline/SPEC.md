# SPEC.md — Bollinger 20/2 ETHUSDT 1h 180d (I.3)

> Gate: **pesquisa**. Terceiro piloto Série I — triangulação cross-asset do edge
> mean-reversion. Conclui o trio SOL + BTC + ETH sobre a mesma janela 180d 1h.

## Hipótese (§1)

**Triangulação do edge mean-reversion.** I.1 (SOL) e I.2 (BTC) cruzaram 45% com mesma
configuração. I.3 ETH fecha o trio: se também cruzar, família valida em 3 assets
independentes; se refutar, ETH tem idiossincrasia que os outros dois não têm.

## Mercado (§2)

ETHUSDT spot, Binance Vision. Mesma janela 2025-07-05 → 2025-12-31, 4320 barras 1h.

## Entradas (§4)

Idêntico a I.1 e I.2 — ADR-0026, edge-triggered duplo em banda inferior, `window=20, num_std=2.0, long_only=True`.

## Saídas (§5)

Edge-triggered duplo em cruzamento de média (ADR-0026). Custos H.1 (5/2/0 bps).

## Critério de refutação

ADR-0025 híbrido idêntico a I.1/I.2.
