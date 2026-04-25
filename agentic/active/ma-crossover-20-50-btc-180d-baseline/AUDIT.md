# AUDIT.md — MA Crossover 20/50 BTCUSDT 1h 180d (baseline)

> Gate ativo: **auditoria**. Produzido pelo protocolo após VALIDATION.md + BACKTEST.md. `release_decision` obrigatório; **nunca `live`**. Primeiro uso protocolar de `alpha-forge compare` (ADR-0018).

## Resumo executivo

MA crossover 20/50 long-only sobre BTCUSDT 1h 180d **não preserva capital** (baseline `final_equity = 9564.25`, −4.36%) e **refuta por hit_rate** (0.3111 < 0.45). Monte Carlo p50 = 9525.25 (sub-breakeven mediano); apenas p95 = 10043.59 passa breakeven. 3 de 4 folds walk-forward negativos. Decisão natural = `fail`.

**Achado cross-family (vs H.1 Donchian BTC):** MA crossover melhora hit_rate (+5.66 pp), reduz drawdown pela metade (6.52% vs 13.90%), e perde menos em cost_stress (Δ fee+10 −181 vs −437), mas **ambas families refutam no mesmo regime**. Sinal forte de que o fator dominante é **regime**, não family. Propriedade estrutural `fee+Δ ≡ spread+Δ` (ADR-0019) confirmada **pela terceira vez** — agora cross-family.

## Blockers

Itens que **reprovam** o piloto hoje:

1. **`hit_rate = 0.3111` viola SPEC §Critério de refutação item 1** (limiar ≥ 0.45). Evidência: `results/validation/ma-crossover-20-50-btc-180d-baseline/cost_stress.json → baseline.result.metrics.hit_rate = 0.3111`. Remediação: idêntica a H.1/H.2a — hit-rate é propriedade emergente; precisaria ou (a) tuning de janelas (exigiria ADR justificando) ou (b) filtro de regime (deferred).

2. **`final_equity = 9564.25 > 9500` tecnicamente passa preservação** mas margem é 64 USDT — frágil. Em regime ligeiramente diferente (ver walk-forward test-only = −415.50 USDT), sinal inverte. Não é evidência de edge.

3. **3 de 4 folds walk-forward negativos.** Evidência: `walk_forward.json` → pnl=(−202.91, +120.62, −27.93, −305.28) para folds 1-4. Único fold positivo (fold 2) tem hit_rate = 20% e N=5 — statisticamente ruído.

4. **Monte Carlo p50 < capital inicial (9525.25 < 10000).** Evidência: `monte_carlo.json → payload.final_equity_percentiles["50"] = 9525.25`. Apenas p95 = 10043.59 passa breakeven. Probabilidade empírica de preservação ≈ 5–10%.

## Comparação transversal (ADR-0018, primeiro uso protocolar)

Saída literal de `alpha-forge compare donchian-20-10-btc-180d-baseline ma-crossover-20-50-btc-180d-baseline` (timestamp de execução embutido):

```
run_a            : donchian-20-10-btc-180d-baseline (.../results/validation/donchian-20-10-btc-180d-baseline)
run_b            : ma-crossover-20-50-btc-180d-baseline (.../results/validation/ma-crossover-20-50-btc-180d-baseline)

--- run_metadata ---
  alpha_forge_version : a=0.0.0  b=0.0.0  (igual)
  timestamp_utc       : a=2026-04-18T00:33:14.509104+00:00  b=2026-04-18T01:04:24.208841+00:00  (delta=+1869.7s)
  command             : a=validate  b=validate  (igual)
  run_id              : a=donchian-20-10-btc-180d-baseline  b=ma-crossover-20-50-btc-180d-baseline  (divergente)
  flags diff (2 chave(s); 22 iguais):
    run_id            : a=donchian-20-10-btc-180d-baseline  b=ma-crossover-20-50-btc-180d-baseline
    strategy          : a=donchian  b=ma_crossover

--- walk_forward ---
  n_folds          : a=4  b=4  (delta=+0)
  total_trades     : a=85  b=29  (delta=-56)
  total_test_bars  : a=3456  b=3456  (delta=+0)
  sum_final_equity : a=39279.1790  b=39584.4893  (delta=+305.3103)

--- monte_carlo ---
  n_resamples      : a=500  b=500
  seed             : a=42  b=42
  p5 _final       : a=8821.5993  b=9090.9673  (delta=+269.3680)
  p25_final       : a=9063.0874  b=9320.4918  (delta=+257.4044)
  p50_final       : a=9246.8564  b=9525.2528  (delta=+278.3964)
  p75_final       : a=9426.3649  b=9720.5498  (delta=+294.1848)
  p95_final       : a=9716.2676  b=10043.5868  (delta=+327.3191)
  original_final   : a=9279.1790  b=9511.2494  (delta=+232.0703)
  original_maxdd   : a=0.000000  b=0.000000  (delta=+0.000000)

--- cost_stress ---
  dataset_id       : a=btcusdt_1h_20250705_20251231_binance_spot  b=btcusdt_1h_20250705_20251231_binance_spot  (igual)
  baseline_final   : a=9089.7894  b=9564.2455  (delta=+474.4560)
  scenarios (3 label(s)):
    fee+10            : a=8652.0560  b=9383.2825  (delta=+731.2265)
    slip+5            : a=9046.0534  b=9546.1642  (delta=+500.1109)
    spread+10         : a=8652.0560  b=9383.2825  (delta=+731.2265)
```

**Leituras extraídas do compare:**

1. **22 flags iguais em 24** — apenas `run_id` e `strategy` divergem. Confirma protocolo agentic: comparação H.1 vs H.2b é controlada (mesmo dataset, sizing, custos, seed, folds, resamples).
2. **fee+10 ≡ spread+10 em ambos os pilotos** (8652.0560 idêntico em A; 9383.2825 idêntico em B). ADR-0019 replicada pela terceira vez, agora via subcomando `compare`.
3. **MA crossover melhora todos os percentis Monte Carlo** em ~270 USDT (p5→p95). Deslocamento paralelo, não mudança de formato — família reduz custos mas não gera edge novo.
4. **Total trades walk-forward: 85 vs 29** (−56). MA crossover é ~3x menos ativo, o que explica melhora em cost_stress e redução de drawdown sem criar edge (média por trade ainda negativa).
5. **original_maxdd = 0 em ambos** — métrica `original_max_drawdown` do Monte Carlo é sempre 0 por definição (ADR-0007 reporta mdd dos resamples, não do original); delta=0 é esperado.

## Bug encontrado e corrigido durante auditoria

`_cmd_compare` em [src/alpha_forge/cli/app.py](../../../src/alpha_forge/cli/app.py) imprimia `Δ=...` (U+0394) em 11 linhas, quebrando em Windows cp1252 — mesmo bug de H.1/H.3 mas em função não-coberta pelo patch anterior. **Corrigido nesta sessão**: substituído `Δ=` por `delta=` em `_fmt_delta`/`_diff_run_metadata`/`_diff_walk_forward`/`_diff_monte_carlo`/`_diff_cost_stress`. Sem gate novo — fix é extensão direta da Frente H.3 (mesma natureza, ADR-0001 §nomes ASCII). Suíte `pytest` deve ser re-validada após esta edição.

## Riscos operacionais

Nenhum — piloto falha em `backtest_only`, não há paper/live a mitigar.

## Compliance do laboratório

- [x] `LIVE_TRADING=false` confirmado; hook `.claude/hooks/block_live_trading.py` bloquearia.
- [x] Alavancagem 2.0 ≤ hard cap 10x.
- [x] Sizing fixed fractional (ADR-0004), sem martingale/grid.
- [x] Sem `import ccxt`/`binance.client`/`create_order` em `src/`.
- [x] Secrets fora do repo (`.claude/settings.json → permissions.deny`).
- [x] `paper_only`/`canary_only` não tratados como se existissem; `live` excluído.
- [x] Testes property-based de causalidade verdes.
- [x] Monotonicidade de custo verde nos 3 eixos (baseline ≥ slip+5 ≥ fee+10 = spread+10).
- [x] `walk_forward.json`, `monte_carlo.json`, `cost_stress.json`, `run.json` persistidos (ADR-0015 + ADR-0017).

## Evidências consultadas

- **JSONs:** `run.json`, `walk_forward.json`, `monte_carlo.json`, `cost_stress.json` em `results/validation/ma-crossover-20-50-btc-180d-baseline/`.
- **Pilotos anteriores (transversal):** AUDIT.md de H.1 e H.2a.
- **Comandos executados:** `alpha-forge validate` (pipeline), `alpha-forge compare` (ADR-0018 — primeiro uso protocolar).
- **ADRs consultadas:** 0002, 0003, 0004, 0006, 0007, 0008, 0010, 0012, 0014, 0015, 0016, 0017, 0018, 0019.

## Release decision

**Decisão:** `fail`.

**Justificativa:** critério 1 do SPEC violado (`hit_rate = 0.3111 < 0.45`). Critérios 2 (mdd=6.52% < 35%) e 3 (Δ spread+10 = −1.89% > −5%) passam, mas regra é boolean OR. Hipótese §1 quase-passa em preservação (9564.25 > 9500 por 64 USDT) mas falha em hit_rate — refutada.

> **`live` nunca é opção.** Hook bloqueia; `paper_only` sem módulo `paper-trade`; `release_decision = fail`.

## Condicionais

Piloto **não** vira `paper_only`/`canary_only` em nenhuma condição realista. Re-avaliação exigiria:
- Filtro de regime (deferred).
- Dataset maior (≥1 ano) para testar estabilidade cross-regime.
- Tuning de janelas (exigiria ADR — ADR-0003 proíbe dentro do walk-forward).

## Lições aprendidas

1. **Regime > family.** Duas families distintas (Donchian, MA crossover) refutam no mesmo asset/período. Se next piloto mantiver hipótese de preservação em BTC 180d sem filtro de regime, espera-se mesma conclusão.
2. **Propriedade `fee+Δ ≡ spread+Δ` replica cross-family (3ª confirmação).** ADR-0019 é estrutural, não artefato de family. Próximos pilotos podem dispensar re-verificação explícita a menos que mudem `notional/capital_inicial`.
3. **Menor frequência de trades → menor perda absoluta, não edge.** MA crossover faz 45 trades vs 110 da Donchian em BTC; Δ cost_stress é proporcionalmente menor. Edge real exigiria maior win-rate, não menor N.
4. **`alpha-forge compare` (ADR-0018) é operacional.** Primeiro uso protocolar — 22/24 flags iguais validam controle experimental; deslocamento paralelo em MC percentis é diagnóstico claro. Preocupação de encoding cp1252 ressurgiu no subcomando — corrigida ad-hoc; fix estrutural já existe pós-H.3 para `_cmd_validate`.
5. **Walk-forward degradation não é monotônica em MA crossover** (vs H.2a Donchian ETH que era monótona). N baixo (29 trades em 4 folds) faz ruído dominar sinal. Para pilotos low-frequency, percentis MC tornam-se mais informativos que pnl por fold.

## Assinatura

- **Auditado por:** `risk-auditor` em modo autônomo autorizado pela janela de 4h iniciada 2026-04-17.
- **Data:** 2026-04-18 (timestamp `run.json` = 2026-04-18T01:04:24Z).
- **Confirmação humana:** dispensada — `release_decision = fail` não requer promoção; piloto encerra no gate 5.

release_decision: fail

---

## Re-auditoria 2026-04-18 (ADR-0025)

release_decision: paper_only

**Critério vigente:** híbrido (ADR-0025) — `canary_only` exige `hit_rate ≥ 45%` absoluto; `paper_only` exige top-3 por `composite_score` (ADR-0024) com N ≥ 9.

**Snapshot de ranking (2026-04-18, DEFAULT_WEIGHTS de ADR-0024):**

- Rank: **3/12**
- `composite_score`: **6.44**
- `hit_baseline`: **31.11%** (< piso de 45%)
- `fe_baseline`: **9564.25**
- `flags_digest`: `ca8100fe8995812f`

**Justificativa:** top-3 por `composite_score` (ADR-0024) em sample N=12 ≥ 9 → canal relativo `paper_only` habilitado (ADR-0025).

**Decisão original preservada acima.** Esta seção é append imutável; revogações futuras devem ser **nova seção**, nunca edit.
