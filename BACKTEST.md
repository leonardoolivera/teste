# BACKTEST.md — Donchian breakout

> Produzido pelo `backtest-validator` após [VALIDATION.md](./VALIDATION.md) verde.
> Reprodutibilidade: comando exato + dataset_id + sha256 documentados abaixo.

---

## Dataset

| Campo | Valor |
|---|---|
| `dataset_id` | `btcusdt_1h_20250705_20251231_binance_spot` |
| Símbolo | BTCUSDT |
| Timeframe | 1h |
| Período | 2025-07-05 → 2025-12-31 |
| Barras | 4320 |
| Fonte | Binance Vision (spot klines mensais) |
| Timezone | UTC |
| `sha256` | `228249e2ceb7239e5ecb31aa1093614fe5fd9d72a8c5cec2c0f90ebaec7a973f` |
| Gaps declarados | 0 |
| Close range | 82.207 → 126.011 USD (janela bull prolongada; top ~126k) |

Origem em `data/datasets.yaml`. Ingestão via `scripts/ingest_binance_vision.py` (ADR-0009). Dataset não entra no git; só o manifesto.

**Dataset secundário (sanidade):** `synthetic_btcusdt_1h_seed42` — 720 barras determinísticas (seed=42); drift baixo + ruído Gaussiano. Regime anti-breakout por construção; útil como contrapeso.

## Fees / Slippage / Funding

- **Taker fee base (piloto):** `5.0 bps`.
- **Slippage base (piloto):** `2.0 bps / unit notional`.
- **Funding:** `N/A` — spot.
- **Aplicação:** contra o trader, em preço de execução (ADR-0006).

## Métricas — piloto com defaults

**Comando:**
```
python -c "from alpha_forge.cli.app import run; raise SystemExit(run(['run-demo', '--strategy', 'donchian', '--dataset-id', 'btcusdt_1h_20250705_20251231_binance_spot', '--entry-window', '20', '--exit-window', '10']))"
```

| Métrica | Valor |
|---|---|
| `barras` | 4320 |
| `fills` | 220 |
| `rejections` | 0 |
| `trade_count` | 110 |
| `total_pnl` | −910.21 (−9.10%) |
| `hit_rate` | 25.45% |
| `max_drawdown` | 10.49% |
| `final_equity` | 9089.79 |
| `max_equity` | 10154.82 |
| `min_equity` | 9089.73 |

## Sensibilidade — fees × slippage (grid 4×4)

Executado via `python scripts/validate_pilot.py --strategy donchian --dataset-id btcusdt_1h_20250705_20251231_binance_spot --entry-window 20 --exit-window 10`.

| fee(bps) | slip(bps) | trades | hit_rate | max_dd | final_equity | total_pnl |
|---:|---:|---:|---:|---:|---:|---:|
| 0.00 | 0.00 | 110 | 27.27% | 8.28% | 9326.50 | −673.50 |
| 0.00 | 2.00 | 110 | 27.27% | 8.44% | 9308.98 | −691.02 |
| 0.00 | 5.00 | 110 | 27.27% | 8.69% | 9282.71 | −717.29 |
| 0.00 | 10.00 | 110 | 27.27% | 9.09% | 9238.93 | −761.07 |
| 5.00 | 0.00 | 110 | 25.45% | 10.32% | 9107.29 | −892.71 |
| 5.00 | 2.00 | 110 | 25.45% | 10.49% | 9089.79 | −910.21 |
| 5.00 | 5.00 | 110 | 24.55% | 10.73% | 9063.55 | −936.45 |
| 5.00 | 10.00 | 110 | 24.55% | 11.15% | 9019.82 | −980.18 |
| 10.00 | 0.00 | 110 | 22.73% | 12.38% | 8888.29 | −1111.71 |
| 10.00 | 2.00 | 110 | 22.73% | 12.55% | 8870.81 | −1129.19 |
| 10.00 | 5.00 | 110 | 20.91% | 12.80% | 8844.60 | −1155.40 |
| 10.00 | 10.00 | 110 | 20.00% | 13.21% | 8800.93 | −1199.07 |
| 20.00 | 0.00 | 110 | 17.27% | 16.51% | 8450.95 | −1549.05 |
| 20.00 | 2.00 | 110 | 17.27% | 16.68% | 8433.52 | −1566.48 |
| 20.00 | 5.00 | 110 | 17.27% | 16.92% | 8407.37 | −1592.63 |
| 20.00 | 10.00 | 110 | 17.27% | 17.34% | 8363.81 | −1636.19 |

**Leitura:**

- `trade_count = 110` em todas as células: os **sinais** são independentes de custo (confirmando que a estratégia é puramente baseada em OHLC).
- `final_equity` é **monotônico-decrescente** em ambos os eixos (custo maior ⇒ final_equity menor ou igual). Monotonicidade verificada pelo próprio script (`[monotonicidade] OK`).
- Custo **não salva** a estratégia: mesmo em `fee=0, slip=0`, `total_pnl = −673.50`. Não é um caso de "strategy mata por fee"; é um caso de hipótese que não teve edge **neste recorte**, e custos só agravam.
- `hit_rate` cai com custos porque trades marginalmente positivos viram negativos após atrito; isso é **esperado** e confirma que o cost model é efetivo.

## Robustez

**Sintético (contrapeso):**
```
trade_count = 14     total_pnl = -372.50 (-3.73%)    hit_rate = 42.86%
```

Sintético é drift-baixo + ruído Gaussiano — regime anti-breakout **por construção**. Donchian perde menos aqui (em % de capital) não por edge, mas por número baixo de sinais disparando (14 trades vs 110).

**Multi-janela / multi-asset:** `N/A` nesta entrega. Follow-up explícito.

## Lookahead bias

- Property-based `test_donchian_causal` passa em 80 exemplos com mutação de OHLC completo.
- Engine chama `assert_causal` obrigatoriamente — ADR-0002.
- Estratégia usa slice `iloc[-N-2 : -2]`, nunca `iloc[-1]`.

**Lookahead: ausente.**

## Notas (achados factuais, sem juízo promocional)

1. **Donchian 20/10 long-only não teve edge no recorte BTCUSDT 1h 180d.** Isto é **um achado**, não uma sentença sobre a família Donchian. Recorte ≠ edge estrutural.
2. **Sensibilidade a custos é linear e esperada** — ADR-0010 (monotonicidade) continua segurando experimentalmente.
3. **Baixo hit rate (25%)** com sinais simétricos sugere que o mercado nesta janela ficou mais ruidoso do que "rompimentos persistentes"; tendências curtas sendo desfeitas antes do exit_window disparar.
4. **Max drawdown de 10.49%** com 110 trades e sizing fixo de 10% não dispara alarmes de ruína, mas consome uma boa parte do capital — qualquer decisão de promoção precisa levar isso em conta.

---

## Caracterização observacional paramétrica — 90d (NÃO é validação)

> **Status epistêmico:** isto é **observação**, não validação. 3 combos escolhidos a priori da literatura (não varridos), um único recorte, um único ativo. Endereça **parcialmente** o blocker #B-3 do AUDIT (sensibilidade de parâmetros) — não fecha.
> Grid search completo, walk-forward, multi-asset e Monte Carlo (blockers #B-3 completo, #B-4, #B-5) continuam pendentes.

### Dataset

| Campo | Valor |
|---|---|
| `dataset_id` | `btcusdt_1h_20251003_20251231_binance_spot` |
| Símbolo | BTCUSDT |
| Timeframe | 1h |
| Período | 2025-10-03 → 2025-12-31 (90d) |
| Barras | 2160 |
| `sha256` | `5db1a51578d430b8badc0097b03fceeb0eebfc077b0fb5fb65d3c309ecb9680d` |
| Gaps declarados | 0 |

### Combos declarados (a priori, não fitados)

| Nome informal | `entry_window` | `exit_window` | Procedência |
|---|---:|---:|---|
| curto | 10 | 5 | metade do default |
| default | 20 | 10 | ADR-0011 + Turtle |
| longo | 40 | 20 | Turtle clássico |

### Resultados (fee=5bps, slip=2bps, capital=10k, fração=10%, alav=2x)

| entry | exit | fills | trades | hit_rate | max_dd | final_equity | total_pnl |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 5 | 192 | 96 | 28.12% | 4.28% | 9598.54 | −401.46 (−4.01%) |
| 20 | 10 | 102 | 51 | 23.53% | 7.12% | 9307.94 | −692.06 (−6.92%) |
| 40 | 20 | 44 | 22 | 22.73% | 4.42% | 9606.71 | −393.29 (−3.93%) |

**Leituras factuais:**

1. **Todos os três combos negativos no recorte 90d.** Consistente com o recorte 180d; sem reversão de sinal.
2. **Trade count escala inversamente com janela** (96 → 51 → 22), como esperado — janelas maiores filtram mais sinais.
3. **Hit rate cai levemente com janela maior** (28% → 23%) — possível sinal de que sinais mais raros aqui não foram mais "limpos".
4. **Combo longo (40/20) tem o melhor PnL absoluto em termos relativos** (−3.93%), mas com menor número de trades (22) — significância estatística baixa; pode ser ruído.
5. **Max drawdown de 20/10 no recorte 90d (7.12%) é menor que no 180d (10.49%)** — janela mais curta, menos acumulação.

**O que isto NÃO mostra:**

- Não mostra que 40/20 é "melhor" que 20/10. 22 trades não permitem discriminar edge de ruído.
- Não mostra generalização. Mesmo ativo; **janela é subconjunto próprio do recorte 180d** (2025-10-03 → 2025-12-31 ⊂ 2025-07-05 → 2025-12-31). "Coerência" entre os dois não é evidência independente — é o mesmo material duas vezes. Qualquer promoção futura exigirá **dataset disjunto temporalmente** (out-of-sample real), não recorte-de-recorte.
- Não mostra robustez temporal. Sem walk-forward.
- Não mostra robustez multi-asset. Só BTCUSDT.

**Conclusão observacional:** no recorte observado, Donchian long-only continua sem evidência de edge para qualquer dos três combos. Resultado coerente com o piloto 180d. Não altera `release_decision = fail`.
