# AUDIT.md — H.3 Donchian+regime SMA slope

> Gate ativo: **auditoria**. 4 JSONs persistidos em `results/validation/donchian-20-10-btc-180d-regime-sma/`; `compare` contra H.1 rodado; conformidade SPEC verificada item-por-item.

## Release decision

```
release_decision: fail
```

**Dupla violação:**

1. **Critério de refutação 1** — `hit_rate = 29.82% < 45%` (gap de 15.18 pp).
2. **Critério de corroboração** — `trade_count = 114 > 110` (H.1 baseline). Filtro deveria ter **reduzido** sinais; redistribuiu sem reduzir.

Critérios 2 (mdd) e 3 (spread+10) passam, mas critério 3 passa por folga de 0.06 pp — não há margem de segurança.

## Saída `compare` H.1 baseline ↔ H.3 regime-sma

```
run_a : donchian-20-10-btc-180d-baseline
run_b : donchian-20-10-btc-180d-regime-sma

--- run_metadata ---
  command             : a=validate  b=validate  (igual)
  run_id              : divergente
  flags diff (2 chave(s); 23 iguais):
    regime_filter     : a=<ausente>  b=sma_slope:min_slope_bps=10:window=50
    run_id            : a=donchian-20-10-btc-180d-baseline
                        b=donchian-20-10-btc-180d-regime-sma

--- walk_forward ---
  n_folds          : 4 (igual)
  total_trades     : a=85  b=80  (delta=-5)
  total_test_bars  : 3456 (igual)
  sum_final_equity : a=39279.18  b=39397.54  (delta=+118.36)

--- monte_carlo ---
  n_resamples      : 500 (igual)  seed : 42 (igual)
  p5  : +165.35    p25 : +192.97
  p50 : +162.12    p75 : +147.94    p95 : +134.71

--- cost_stress ---
  baseline_final   : +105.80
  fee+10           : +89.61
  slip+5           : +104.17
  spread+10        : +89.61
```

**Experimento controlado validado:** exatamente 2 flags divergem (`regime_filter`, `run_id`); 23 flags idênticas. Qualquer diferença métrica é atribuível ao filtro de regime, não a drift de configuração. SPEC §"Experimento controlado" OK.

## Blockers

1. **Critério 1 (hit_rate ≥ 45%) viola por 15.18 pp** — fold 2 isolado atinge 45.83%, mas 3 dos 4 folds ficam entre 22-32%.
2. **Critério corroboração (trade_count < 110) viola por 4 trades** — filtro não reduziu contagem, apenas redistribuiu entradas entre regimes.
3. **Critério 3 (spread+10) passa por 0.06 pp** — sem folga defensável; qualquer variação de calibração de custos potencialmente vira violação.
4. **p95 MC = 9850.98 < 10000** — nem no topo da distribuição (500 resamples) o backtest cruza breakeven; filtro desloca distribuição, mas não atravessa zero.

## Conformidade SPEC

| Item | Status |
|---|---|
| §1 Hipótese | **GAP** — 2 condições simultâneas falham. |
| §2-§13 (mercado, TF, entrada, saída, stops, sizing, fees, slip, spread, funding, regime filter, long_only, limitações) | 9/9 OK. |
| §Critério refutação 1 | **VIOLA** (29.82%). |
| §Critério refutação 2 | OK (9.60%). |
| §Critério refutação 3 | OK com margem mínima (−4.94%). |
| §Critério corroboração | **VIOLA** (114 > 110). |
| §Experimento controlado | OK (2 flags diff, 23 iguais). |

## Propriedades estruturais reafirmadas

- **ADR-0019 `fee+Δ ≡ spread+Δ` (5ª confirmação; 1ª com filtro ativo):** `fee+10` e `spread+10` produzem `final_equity = 8741.66` bit-a-bit. Filtro de regime não quebra a propriedade estrutural — esperado por design (filtro afeta `trade_count`, mas a equivalência depende de `notional/capital_inicial`, constante entre cenários).
- **ADR-0010 monotonicidade:** sem `ValidationError` em cost_stress; cada cenário de custo maior produz equity menor ou igual ao baseline.
- **ADR-0022 canonicalização:** `run.json.flags.regime_filter == "sma_slope:min_slope_bps=10:window=50"` (ordem alfabética); `compare` detecta divergência esperada vs H.1 (chave ausente lá).

## 5 lições transversais

1. **Filtro de regime desloca distribuição inteira para cima (+134 a +193 USDT em todos os 5 percentis MC), mas +160 USDT não é suficiente para cruzar breakeven em 180 dias de BTC 1h.** A magnitude do edge faltante é maior que o ganho marginal do filtro `SMA-50 slope ≥ 10 bps`. H.3 prova que *mais filtro* (desta família) não resolve; precisa-se de *outra família de filtro* ou *mudança estrutural* (stops, outra saída, outro mercado).
2. **Fold 2 atinge 45.83% — primeira vez no protocolo que um fold cruza 45% em qualquer piloto Donchian.** Esse fold captura ~864 barras (36 dias) do período. Investigar qual sub-janela é (provavelmente a alta de 2025-09 a 2025-10) pode informar um filtro de regime mais específico (ex.: filtro de volatilidade + slope combinado, ou HMM de 2 estados).
3. **Filtro não reduz `trade_count` (+4 vs H.1).** Hipótese implícita era "filtro suprime sinais laterais → menos trades". Observado: filtro **redistribui** trades entre regimes sem reduzir contagem total. Implicação: `SMA-50 slope ≥ 10 bps` ativa ~tanto quanto desativa; o recorte pode ser ruído (threshold baixo demais).
4. **`spread+10` Δ = −4.94%, passa por 0.06 pp — mesma fragilidade que H.1 (−4.82%).** Filtro não altera sensibilidade a spread porque a mecânica de custos é a mesma (cada trade paga spread). Para aliviar essa sensibilidade seria preciso **reduzir `trade_count`**, o que este filtro não faz.
5. **Arquitetura ADR-0022 validada como primeiro consumidor real.** Gap de código = zero; integração engine↔filter passa 3 property-based + 3 integration CLI + walk-forward + cost_stress sem regressão. A infraestrutura está pronta para **RSI-range, ATR-regime, HMM-2state, volatility-bucket** — o próximo piloto testará outra família sem custo de re-implementação.

## Recomendações para próximos pilotos

**Descartar** tuning de `SMASlopeFilter(window, min_slope_bps)` dentro deste dataset — ADR-0003 proíbe grid search intra-walk-forward, e a família de filtro parece ortogonal ao edge faltante.

**Candidatos ranqueados:**

- **H.4 — Donchian + ATR-regime filter** (volatilidade; outra família, mesmo gap-zero de código se ADR-0022b for uma extensão; mais informativo sobre "qual tipo de regime importa").
- **H.3b — Donchian + SMA-slope com `min_slope_bps=20` ou `window=100`** (variação dentro da família; barato, mas provavelmente confirma lição #1).
- **H.2d — Donchian baseline SOL** (fecha cross-asset BTC/ETH/SOL sem filtro; barato, exaustivo do ciclo H.2).

Sugestão principal: **H.4 ATR-regime** — testa outra família e amplia ADR-0022 como contrato genérico antes de commitar a uma só dimensão de regime.

---

## Re-auditoria 2026-04-18 (ADR-0025)

release_decision: fail

**Critério vigente:** híbrido (ADR-0025) — `canary_only` exige `hit_rate ≥ 45%` absoluto; `paper_only` exige top-3 por `composite_score` (ADR-0024) com N ≥ 9.

**Snapshot de ranking (2026-04-18, DEFAULT_WEIGHTS de ADR-0024):**

- Rank: **5/12**
- `composite_score`: **5.00**
- `hit_baseline`: **29.82%** (< piso de 45%)
- `fe_baseline`: **9195.59**
- `flags_digest`: `2f4c4affe4f2adfe`

**Justificativa:** rank 5/12 por `composite_score`; fora do top-3 → permanece `fail` sob ADR-0025. `hit_rate`=29.82% < 45% também impede `canary_only`.

**Decisão original preservada acima.** Esta seção é append imutável; revogações futuras devem ser **nova seção**, nunca edit.
