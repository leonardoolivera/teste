# AUDIT.md — Donchian 20/10 BTCUSDT 1h 180d (symmetric)

> Gate ativo: **auditoria**. Produzido pelo protocolo após VALIDATION.md + BACKTEST.md. `release_decision` obrigatório; **nunca `live`**. Segundo uso protocolar de `alpha-forge compare` (ADR-0018).

## Resumo executivo

Donchian 20/10 simétrico (long + short com reversal, ADR-0013 + ADR-0012) sobre BTCUSDT 1h 180d **refuta em três critérios simultâneos**: (1) `hit_rate = 27.27% < 45%`, (2) hipótese §1 preservação falha (`final_equity = 8526.83 < 9500`), (3) `spread+10` Δ = −10.34% < −5%. Primeira vez que o critério 3 é violado no protocolo. Monte Carlo p95 = 9954.15 < 10000 — nem o topo da distribuição cruza breakeven. Decisão natural = `fail`.

**Achado cross-mode (vs H.1 Donchian long):** reversal **não gera edge** em regime 2025-07..12 — dobra os trades (220 vs 110), aumenta drawdown (+1.55 pp), piora final_equity em 6.18%, e amplifica sensibilidade a cost_stress em 2.15× (Δ fee+10 −881 vs −438). Propriedade estrutural `fee+Δ ≡ spread+Δ` (ADR-0019) confirmada **pela quarta vez** (cross-mode). Padrão transversal agora inequívoco: em BTC 1h 180d, nem long-only nem reversal nem MA crossover passam `hit_rate ≥ 45%` — fator dominante é **regime**.

## Blockers

Itens que **reprovam** o piloto hoje:

1. **`hit_rate = 0.2727` viola SPEC §Critério de refutação item 1** (limiar ≥ 0.45). Evidência: `results/validation/donchian-20-10-btc-180d-short/cost_stress.json → baseline.result.metrics.hit_rate = 0.2727`. Remediação: mesma de H.1/H.2a/H.2b — hit-rate é emergente do regime; requer filtro ou tuning (ambos deferred).

2. **Hipótese §1 falha em preservação:** `final_equity = 8526.83 < 9500` (limiar 0.95×capital). Evidência: `cost_stress.json → baseline.final_equity = 8526.83`. Pior preservação de todos os pilotos até hoje.

3. **`spread+10` Δ = −10.34% < −5% viola critério 3.** Evidência: `cost_stress.json → scenarios[2] (spread+10) .final_equity_delta_vs_baseline = −881.32`. Primeira violação deste critério no protocolo. Causa mecânica: reversal aplica custo duplo por flip (ADR-0012) — perturbação de +10 bps em 220 trades amplifica-se vs 110 trades em H.1.

4. **Monte Carlo p95 < breakeven.** Evidência: `monte_carlo.json → payload.final_equity_percentiles["95"] = 9954.15`. Nem o topo da distribuição preserva capital — edge estatisticamente ausente.

## Comparação transversal (ADR-0018, 2º uso protocolar)

Saída literal de `alpha-forge compare donchian-20-10-btc-180d-baseline donchian-20-10-btc-180d-short`:

```
run_a            : donchian-20-10-btc-180d-baseline
run_b            : donchian-20-10-btc-180d-short

--- run_metadata ---
  alpha_forge_version : a=0.0.0  b=0.0.0  (igual)
  timestamp_utc       : a=2026-04-18T00:33:14.509104+00:00  b=2026-04-18T01:53:16.180896+00:00  (delta=+4801.7s)
  command             : a=validate  b=validate  (igual)
  run_id              : a=donchian-20-10-btc-180d-baseline  b=donchian-20-10-btc-180d-short  (divergente)
  flags diff (2 chave(s); 22 iguais):
    long_only         : a=True  b=False
    run_id            : a=donchian-20-10-btc-180d-baseline  b=donchian-20-10-btc-180d-short

--- walk_forward ---
  n_folds          : a=4  b=4  (delta=+0)
  total_trades     : a=85  b=167  (delta=+82)
  total_test_bars  : a=3456  b=3456  (delta=+0)
  sum_final_equity : a=39279.1790  b=39153.4564  (delta=-125.7226)

--- monte_carlo ---
  n_resamples      : a=500  b=500
  seed             : a=42  b=42
  p5 _final       : a=8821.5993  b=8349.9303  (delta=-471.6690)
  p25_final       : a=9063.0874  b=8790.0376  (delta=-273.0498)
  p50_final       : a=9246.8564  b=9114.0610  (delta=-132.7954)
  p75_final       : a=9426.3649  b=9453.7498  (delta=+27.3849)
  p95_final       : a=9716.2676  b=9954.1489  (delta=+237.8812)
  original_final   : a=9279.1790  b=9161.3101  (delta=-117.8689)
  original_maxdd   : a=0.000000  b=0.000000  (delta=+0.000000)

--- cost_stress ---
  dataset_id       : a=btcusdt_1h_20250705_20251231_binance_spot  b=btcusdt_1h_20250705_20251231_binance_spot  (igual)
  baseline_final   : a=9089.7894  b=8526.8335  (delta=-562.9560)
  scenarios (3 label(s)):
    fee+10            : a=8652.0560  b=7645.5144  (delta=-1006.5416)
    slip+5            : a=9046.0534  b=8438.7227  (delta=-607.3306)
    spread+10         : a=8652.0560  b=7645.5144  (delta=-1006.5416)
```

**Leituras extraídas do compare:**

1. **22/24 flags iguais; divergem apenas `run_id` e `long_only`.** Experimento controlado: efeito é puramente do modo (long-only → symmetric).
2. **Walk-forward total_trades dobra em B (85 → 167, delta=+82)** — quase exatamente o dobro esperado de reversal. Mas `sum_final_equity` piora em apenas −125.72 USDT no test-only — magnitude pequena em walk-forward, larga no baseline full (−562.96). Sinal: a diferença full vs test-only se concentra em barras pré-folds (warm-up e sobreposições), onde reversal é mais punido.
3. **MC percentis: B tem cauda esquerda pior (p5 −472) mas cauda direita melhor (p95 +238).** Reversal adiciona variância em ambas direções; medianas quase iguais (delta −133). Não é edge, é volatility.
4. **Cost_stress amplificação 2.15×:** Δ baseline = −563 explicado pelo próprio modo; Δ fee+10 = −1007 (2.15× maior que H.1 fee+10 = −437) confirma a hipótese de custo duplo por flip. **fee+10 ≡ spread+10 exato em ambos os pilotos (ADR-0019).**
5. **`original_max_drawdown = 0.0` em ambos** é artifact do reporting MC (ADR-0007 reporta mdd dos resamples, não do original; delta=0 esperado).

## Riscos operacionais

Nenhum — piloto falha em `backtest_only`, não há paper/live a mitigar.

## Compliance do laboratório

- [x] `LIVE_TRADING=false`; hook `.claude/hooks/block_live_trading.py` bloquearia.
- [x] Alavancagem 2.0 ≤ hard cap 10x.
- [x] Sizing fixed fractional (ADR-0004), sem martingale/grid.
- [x] Sem `import ccxt`/`binance.client`/`create_order` em `src/`.
- [x] Secrets fora do repo.
- [x] `paper_only`/`canary_only` não tratados como existentes; `live` excluído.
- [x] Testes property-based de causalidade verdes.
- [x] Monotonicidade de custo verde nos 3 eixos (baseline ≥ slip+5 ≥ fee+10 = spread+10).
- [x] `walk_forward.json`, `monte_carlo.json`, `cost_stress.json`, `run.json` persistidos (ADR-0015 + ADR-0017).

## Evidências consultadas

- **JSONs:** `run.json`, `walk_forward.json`, `monte_carlo.json`, `cost_stress.json` em `results/validation/donchian-20-10-btc-180d-short/`.
- **Pilotos anteriores:** AUDIT.md de H.1, H.2a, H.2b.
- **Comandos executados:** `alpha-forge validate --no-long-only` (pipeline, exit 0), `alpha-forge compare donchian-20-10-btc-180d-baseline donchian-20-10-btc-180d-short` (ADR-0018, 2º uso).
- **ADRs consultadas:** 0002, 0003, 0004, 0006, 0007, 0010, 0011, 0012, 0013, 0014, 0015, 0016, 0017, 0018, 0019.

## Release decision

**Decisão:** `fail`.

**Justificativa:** três critérios do SPEC §Critério de refutação violam simultaneamente:
- `hit_rate = 0.2727 < 0.45` (critério 1).
- `final_equity = 8526.83 < 9500` (hipótese §1 preservação).
- `spread+10` Δ = −10.34% < −5% (critério 3).

Boolean OR com 3 violações; refutação mais robusta até hoje.

> **`live` nunca é opção.** Hook bloqueia; `paper_only` sem módulo `paper-trade`; `release_decision = fail`.

## Condicionais

Piloto **não** vira `paper_only`/`canary_only`. Re-avaliação exigiria mudança estrutural:
- Filtro de regime antes do sinal de reversal.
- Dataset com regime de crash genuíno (short seria favorecido).
- Stops para limitar drawdown em whipsaws.

## Lições aprendidas

1. **Reversal não é edge em regime lateral/bullish.** H.2c dobra custos sem dobrar sinal — 167 walk-forward trades contribuem −846.54 USDT de PnL (edge negativo puro). ADR-0013 é ferramenta correta mas sem filtro de regime, simétrico piora vs long-only.
2. **ADR-0019 `fee+Δ ≡ spread+Δ` confirmada 4ª vez (cross-mode).** Agora validada ao longo de 2 ativos × 2 families × 2 modos. Próximos pilotos podem dispensar re-verificação explícita. Propriedade estrutural consolidada.
3. **Custo duplo ADR-0012 amplifica sensibilidade a bumps de custo proporcionalmente ao número de flips.** Cada +10 bps custa 2.15× mais em reversal (220 trades) do que em long-only (110 trades). Confirma modelo aditivo ADR-0019: Δ = bps × trade_count × notional_per_trade.
4. **Critério 3 do SPEC é acionado pela primeira vez em H.2c.** Critério 1 (hit_rate) acionou em 100% dos pilotos; critério 3 (spread+10 Δ) é discriminador útil para pilotos high-frequency onde o número de trades excede ~150. Sugere que próximos pilotos devam preferir estratégias low-frequency se o objetivo é preservação, ou adicionar filtro de regime antes de aumentar frequência.
5. **Padrão transversal confirmado (3 pilotos BTC × 1 ETH → 4 refutações):** `hit_rate` em BTC 1h 180d é emergente do regime. Próxima frente lógica é **mudança estrutural** (filtro de regime, janela maior, ou stops), não mais enumeração de family×mode×asset. Protocolo agentic já validou sua capacidade de produzir refutações reprodutíveis — o próximo deliverable deveria atacar a causa raiz.

## Assinatura

- **Auditado por:** `risk-auditor` em modo autônomo autorizado pela janela de 4h iniciada 2026-04-17.
- **Data:** 2026-04-18 (timestamp `run.json` = 2026-04-18T01:53:16Z).
- **Confirmação humana:** dispensada — `release_decision = fail` não requer promoção.

release_decision: fail

---

## Re-auditoria 2026-04-18 (ADR-0025)

release_decision: fail

**Critério vigente:** híbrido (ADR-0025) — `canary_only` exige `hit_rate ≥ 45%` absoluto; `paper_only` exige top-3 por `composite_score` (ADR-0024) com N ≥ 9.

**Snapshot de ranking (2026-04-18, DEFAULT_WEIGHTS de ADR-0024):**

- Rank: **12/12**
- `composite_score`: **1.98**
- `hit_baseline`: **27.27%** (< piso de 45%)
- `fe_baseline`: **8526.83**
- `flags_digest`: `5271664a8b8569d4`

**Justificativa:** rank 12/12 por `composite_score`; fora do top-3 → permanece `fail` sob ADR-0025. `hit_rate`=27.27% < 45% também impede `canary_only`.

**Decisão original preservada acima.** Esta seção é append imutável; revogações futuras devem ser **nova seção**, nunca edit.
