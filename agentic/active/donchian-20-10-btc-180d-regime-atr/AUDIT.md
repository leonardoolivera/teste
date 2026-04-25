# AUDIT.md — H.4 Donchian+regime ATR

> Gate ativo: **auditoria**. 4 JSONs persistidos; `compare` duplo rodado (vs H.1 e vs H.3); conformidade SPEC 9/9 OK + critério 1 viola.

## Release decision

```
release_decision: fail
```

**Violação única (diferente de H.3 que tinha dupla):** critério de refutação 1 `hit_rate = 26.39% < 45%` (gap de 18.61 pp — **pior** que H.3's 29.82%, mesmo com filtro mais restritivo).

**Critério de corroboração passa pela primeira vez no protocolo** (`trade_count = 72 < 110`). ATR filter **reduz trades como esperado**, mas reduz indiscriminadamente — bons e ruins — resultando em hit_rate pior.

Critérios 2 (mdd) e 3 (spread+10) passam com folga — especialmente critério 3: Δ = −3.12% vs H.3 −4.94% e H.1 −4.82%. **Maior folga em 5 pilotos**, atribuível à redução de trade_count.

## Saída `compare` H.1 baseline ↔ H.4 ATR

```
flags diff (2 chave(s); 23 iguais):
  regime_filter : a=<ausente>  b=atr_regime:min_atr_bps=50:window=14
  run_id        : divergente
walk_forward   : total_trades a=85 b=60 (delta=-25)
monte_carlo    : p5=+195.60, p25=+161.90, p50=+124.67, p75=+92.83, p95=+87.90
cost_stress    : baseline_final=+90.66, fee+10=+242.32, slip+5=+105.83, spread+10=+242.32
```

**Padrão:** H.4 vence H.1 em todos os percentis MC e em todos os cenários cost_stress. Experimento controlado validado (2 flags diff).

## Saída `compare` H.3 SMA ↔ H.4 ATR — primeiro uso inter-filtro

```
flags diff (2 chave(s); 23 iguais):
  regime_filter : a=sma_slope:min_slope_bps=10:window=50  b=atr_regime:min_atr_bps=50:window=14
  run_id        : divergente
walk_forward   : total_trades a=80 b=60 (delta=-20)
monte_carlo    : p5=+30.26, p25=-31.07, p50=-37.46, p75=-55.11, p95=-46.81
cost_stress    : baseline=-15.14, fee+10=+152.72, slip+5=+1.66, spread+10=+152.72
```

**Padrão:** ATR vence SMA apenas em p5 e em cost_stress cenários agressivos (menos trades → menos exposição a spread/fee). SMA vence ATR em p25–p95 e em baseline. **Trade-off identificado** — primeiro no protocolo.

**Experimento inter-filtro válido:** 2 flags diff (só `regime_filter` com valores diferentes + `run_id`). Diferenças métricas são puramente atribuíveis à família de filtro.

## Blockers

1. **Critério 1 viola por 18.61 pp** — mais distante de 45% que H.3 (−15.18 pp). ATR filter não recupera hit_rate, piora em 3.43 pp vs H.3.
2. **Nenhum fold cruza 45%** (vs H.3 fold 2 = 45.83%). Homogeneização entre folds, mas todos 23-36%.
3. **p95 MC = 9804.17 < 10000** — ATR nem no topo cruza breakeven.
4. **Trade-off explícito vs H.3:** ATR ganha em robustez a custos (−3.12% spread+10) mas perde em centro de distribuição (p50 −37, p95 −46). Sem dominância estrita.

## Conformidade SPEC

| Item | Status |
|---|---|
| §1 Hipótese | **GAP** — hit_rate e final_equity falham. |
| §2–§13 | 12/12 OK. |
| §Critério refutação 1 | **VIOLA** (26.39%). |
| §Critério refutação 2 | OK (8.80%). |
| §Critério refutação 3 | OK com maior folga do protocolo (−3.12%). |
| §Critério corroboração | **OK** — 72 < 114 < H.3. **Primeira vez no protocolo.** |
| §Experimento controlado (vs H.1) | OK (2 flags diff). |
| §Experimento controlado (vs H.3) | OK (2 flags diff — primeiro inter-filtro). |

## Propriedades estruturais reafirmadas

- **ADR-0019 `fee+Δ ≡ spread+Δ` (6ª confirmação):** fee+10 = spread+10 = 8894.38 bit-a-bit em H.4. Nova família de filtro (ATR) não afeta a propriedade.
- **ADR-0010 monotonicidade:** sem `ValidationError`.
- **ADR-0022 contrato genérico validado:** 2 consumidores reais (`sma_slope`, `atr_regime`) compartilham 100% da integração engine/validation/CLI. Nenhum bypass, nenhum special-case. Confirma que a interface minimal do ADR-0022 é suficiente para acomodar famílias diversas (slope de MA vs ATR normalizado são matemática muito distinta; contrato abstrai).
- **Monotonicity property-based (novo ATR):** aumentar `min_atr_bps` nunca aumenta `trade_count` (property validada em 8 amostras hypothesis sobre MA 20/50 BTC 180d). Confirma que ATR filter é "verdadeiramente restritivo" — matematicamente impossível criar sinais.

## 5 lições transversais

1. **Família de filtro importa qualitativamente, não só quantitativamente.** SMA e ATR produzem distribuições metricamente diferentes — SMA concentra valor no centro (p50 alto), ATR na cauda (p5 alto) + robustez de custos. Pesquisa futura de regime filter é multi-dimensional: qual família, qual parâmetro, qual métrica otimizar.
2. **ATR filter é o primeiro filtro que passa critério de corroboração do protocolo.** Reduz trade_count de 110→72 (−35%), confirmando que "filtro suprime sinais" vale empiricamente quando o threshold está alinhado com o dataset. SMA com `min_slope_bps=10` tinha threshold baixo demais (redistribuía sem cortar).
3. **Trade-off hit_rate × trade_count pode ser intrínseco.** ATR corta 42 trades vs H.3 e hit_rate cai 3.43 pp. Se ATR cortou sinais bons junto com ruins, "adicionar filtro" não é dominante — depende de quais trades foram cortados. Isso implica que **tuning multi-objetivo é necessário** (quadro natural para futuro `ranking/` multi-objective conforme ADR planejada).
4. **Robustez a custos é eixo informativo separado do hit_rate.** H.4 tem pior hit_rate mas melhor cost_stress Δ. Pilotos futuros devem reportar ambos como eixos independentes, não como substitutos.
5. **Arquitetura ADR-0022 provou-se genérica.** Pre-autorização de novos filtros sem nova ADR reduziu gap de código para ~55 linhas + 2 property tests. Próximos filtros (RSI, ADX, HMM) podem ser adicionados na mesma frente — protocolo "filter research" está estabelecido.

## Recomendações para próximos pilotos

**Ranqueados:**

- **H.5 — combinar filtros (AND).** `sma_slope AND atr_regime` — só abrir quando *ambos* ativos. Testa hipótese "regime exige direção + volatilidade". Exige **extensão ADR-0022 (ADR-0023?)**: adicionar `CompositeFilter(filters: list[RegimeFilter], mode: Literal["and", "or"])`. Interface minimal. **Maior ROI** — se passar critério 1, resolve; se refutar, questiona família inteira de filtros heurísticos causais (abre caminho para HMM/ML).
- **H.4b — tuning de `ATRRegimeFilter`** variando `min_atr_bps ∈ {20, 100, 200}`. Pilotos independentes (ADR-0003 permite entre corridas). ROI moderado: pode encontrar threshold que passa hit_rate, mas provavelmente apenas desloca trade-off identificado.
- **H.6 — HMM 2-state regime** (trend vs mean-revert). ADR-0022 tem extensão natural para classificadores stateful (Protocol não impede estado interno; só `is_active` ser pura de window). ROI alto mas custo alto (dependency `hmmlearn`, hiperparâmetros, reprodutibilidade).

**Descartado:** H.3b tuning de SMA — lição de H.3 já indica que família SMA não resolve isoladamente.

**Recomendação principal:** **H.5 CompositeFilter AND**. Testa diretamente a hipótese "regime é multi-dimensional" com gap de código pequeno e sem dependency externa.

---

## Re-auditoria 2026-04-18 (ADR-0025)

release_decision: fail

**Critério vigente:** híbrido (ADR-0025) — `canary_only` exige `hit_rate ≥ 45%` absoluto; `paper_only` exige top-3 por `composite_score` (ADR-0024) com N ≥ 9.

**Snapshot de ranking (2026-04-18, DEFAULT_WEIGHTS de ADR-0024):**

- Rank: **4/12**
- `composite_score`: **5.31**
- `hit_baseline`: **26.39%** (< piso de 45%)
- `fe_baseline`: **9180.45**
- `flags_digest`: `b5ac258e191f0642`

**Justificativa:** rank 4/12 por `composite_score`; fora do top-3 → permanece `fail` sob ADR-0025. `hit_rate`=26.39% < 45% também impede `canary_only`.

**Decisão original preservada acima.** Esta seção é append imutável; revogações futuras devem ser **nova seção**, nunca edit.
