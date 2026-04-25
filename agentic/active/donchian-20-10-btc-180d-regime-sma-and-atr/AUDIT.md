# AUDIT.md — Donchian 20/10 + Composite(sma AND atr) (H.5)

release_decision: fail

## release_decision

**`fail`**.

## Blockers

Nenhum blocker operacional — pipeline executou 100% limpo. O `fail` é por **mérito de hipótese** (hit_rate 29.73% < 45%) e não por falha operacional ou de infra. Dívida técnica aberta (não bloqueante para fechar H.5):

- ADR-0023 property 1 precisa de reformulação a nível de signal-emission (ver §Finding transversal chave).

Dois critérios violados:

1. **Critério de refutação 1:** `hit_rate` baseline = **29.73% < 45%**.
2. **Critério de corroboração auxiliar:** `trade_count` baseline = **74 > 72** (H.4). AND deveria ser **estritamente** mais restritivo que o filtro individual mais restritivo; não foi.

Critérios 2 e 3 (mdd e spread stress) passaram — mas isso é insuficiente dado o não cruzamento do limiar primário de `hit_rate` E a falha da property assumida de AND-restritividade em trade_count.

## Refutação da hipótese SPEC §1

Hipótese: "regime é multi-dimensional (direção AND volatilidade)" — se ambas as condições precisam ser verdadeiras, AND composto deve atingir `hit_rate ≥ 45%`. **Observado: 29.73%, insignificantemente diferente de H.3 (29.82%)**. Adicionar a dimensão volatilidade ao filtro direcional produziu variação de hit_rate de −0.09 p.p. (ruído). A multiplicação de filtros causais heurísticos **não recupera edge**; o espaço de recortes `(slope ≥ 10) AND (ATR ≥ 50)` está desalinhado, ou (mais provável dado o acumulado de 4 pilotos) a família inteira de filtros causais heurísticos é insuficiente.

## Finding transversal chave: AND NÃO é estritamente trade-count-restrictive

ADR-0023 property 1 foi escrita como "AND-restrictive: `len(trades(and(f1,f2))) <= min(len(trades(f1)), len(trades(f2)))`". **Empiricamente, H.5 produz 74 trades e H.4 (ATR alone) produz 72. Violação de 2 trades.**

A property-based test `test_composite_filter_restrictive.py` continua passando sobre `synthetic_btcusdt_1h_seed42` com MA-crossover — não é bug no teste, é insuficiência da hipótese testada. Raiz mecânica da divergência:

- `CompositeFilter(mode="and")` força **EXIT mid-trade** quando qualquer filtro interno retorna `False`.
- Um trade ATR-alone longo que atravessa um período curto de `sma_slope = False` é **quebrado em dois trades menores** pelo composto, com re-entrada quando ambos voltam a `True`.
- Portanto, a invariante correta é a nível de **signal-emission bit-a-bit**: `sum(is_active_bars(and)) ≤ min(sum(is_active_bars(f1)), sum(is_active_bars(f2)))`. O trade_count observado é mediado pela engine de execução (entry/exit windows), que pode gerar mais transações sob o mesmo conjunto de barras ativas quando a ativação é mais fragmentada.

**Ação corretiva** (não executada neste piloto — registrada como dívida):

- Reescrever ADR-0023 property 1 para ser precisa a nível de signal-emission, e adicionar uma nota explícita de que trade_count pode ser violado por fragmentação.
- Opcional: adicionar test property comparando contagem de barras ativas (não trades).

## Lições transversais

1. **Heurística causal atinge plateau em ~30% hit.** Quatro pilotos (H.1 25.45%, H.3 29.82%, H.4 26.39%, H.5 29.73%) convergem para uma faixa 25-30% sem cruzar 45%. A assinatura é consistente com a hipótese de que o dataset 180d BTC 1h simplesmente não tem edge residual após o processo gerador incluir tendência + volatilidade observáveis. **Caminho natural**: saltar para regimes latentes (HMM, ADR futuro) ou encerrar a linha Donchian/MA e buscar alpha fora desta família.
2. **Trade_count como proxy de restritividade é enganoso.** Fold-agregado comporta-se como esperado (H.4 WF=60, H.5 WF=55, −5); cost_stress global tem a direção oposta (+2). O aritmético sobre contagens precisa de cuidado — a engine de execução é um multiplicador não-monotônico sobre janelas ativas fragmentadas.
3. **Monte Carlo p5 melhorou monotonicamente** com cada filtro adicionado (H.1 < H.3 < H.4 < H.5). Filtros **reduzem cauda inferior** mesmo quando não movem a média de forma decisiva. Se alguma estratégia futura precisar apenas de **garantia de preservação de capital** (não de edge positivo), composite-AND é a escolha — isso é, porém, fora do propósito desta série.
4. **Segundo fold a cruzar 45%**: H.3 fold 2 (~47%) e H.5 fold 1 (46.67%). Vale checar se são sub-períodos sobrepostos — se sim, há um window temporal específico onde o regime heurístico funciona, e o resto do dataset é ruído.
5. **ADR-0019 sétima confirmação**: `fee+Δ == spread+Δ` continua inquebrável sobre 7 execuções independentes. Invariante estrutural robusto.

## Comparação quadruple (fe / hit / trades / mdd)

| piloto | regime      | fe      | hit    | trades | mdd    |
| ------ | ----------- | ------- | ------ | ------ | ------ |
| H.1    | none        | 9089.79 | 25.45% | 110    | 10.49% |
| H.3    | sma_slope   | 9195.59 | 29.82% | 114    | 9.60%  |
| H.4    | atr_regime  | 9180.45 | 26.39% | **72** | 8.80%  |
| H.5    | and(atr,sma)| **9247.34** | 29.73% | 74 | **8.14%** |

H.5 Pareto-domina H.1 em 3 de 4 métricas (tudo exceto trade_count), mas a dominância não basta se o piso de hit_rate não é cruzado.

## Recomendações

### Curto prazo
- **Não escalar** com variações de thresholds (slope=20, ATR=100, etc.) — ADR-0003 proíbe tuning, e o gradiente horizontal dos 4 pilotos sugere que recortes finos de causal heurístico não vão romper 45%.
- **Atualizar ADR-0023** com finding transversal — property 1 precisa ser enunciada a nível de signal-emission, não trade_count.

### Próxima frente (H.6) — opções
- **H.6-HMM**: regime stateful latente (2 estados Gaussianos sobre returns, prob > 0.7 para `active`). Primeiro filtro não-heurístico; abre caminho para ML.
- **H.6-abandono**: encerrar série Donchian/MA BTC 180d, mover para dataset novo (ETH? período diferente?) ou família de estratégia diferente (mean-reversion, carry).

### Encerramento da série H
SPEC H.5 preview dizia "corroboração encerra a série H em 6 pilotos". Com H.5 refutado, a decisão é:

- Se H.6 também refutado sob a mesma forma (hit_rate ~25-30%), o sinal é claro: **dataset 180d BTC 1h não tem edge residual para esta família de estratégia**. Encerra série H e inicia série I com dataset diferente.
- Se H.6 corroborar, documenta-se que regimes latentes estavam efetivamente ocultos para heurísticas causais — e abre-se a frente ML como continuação natural.

## Integrity cross-checks

- `run.json.flags.regime_filter` = `"and(atr_regime:min_atr_bps=50:window=14,sma_slope:min_slope_bps=10:window=50)"` — ordem lexicográfica (ADR-0023 canonical).
- ADR-0019 (7ª): `fee+10.final_equity == spread+10.final_equity == 8953.15`. ✅
- ADR-0010 monotonicity: `slip+5.fe < baseline.fe` e `spread+10.fe < baseline.fe`. ✅
- Compare H.1↔H.5, H.3↔H.5, H.4↔H.5 todos com exatamente 2 flags diff. ✅

---

## Re-auditoria 2026-04-18 (ADR-0025)

release_decision: fail

**Critério vigente:** híbrido (ADR-0025) — `canary_only` exige `hit_rate ≥ 45%` absoluto; `paper_only` exige top-3 por `composite_score` (ADR-0024) com N ≥ 9.

**Snapshot de ranking (2026-04-18, DEFAULT_WEIGHTS de ADR-0024):**

- Rank: **6/12**
- `composite_score`: **4.99**
- `hit_baseline`: **29.73%** (< piso de 45%)
- `fe_baseline`: **9247.34**
- `flags_digest`: `4d30fedb125bcf80`

**Justificativa:** rank 6/12 por `composite_score`; fora do top-3 → permanece `fail` sob ADR-0025. `hit_rate`=29.73% < 45% também impede `canary_only`.

**Decisão original preservada acima.** Esta seção é append imutável; revogações futuras devem ser **nova seção**, nunca edit.
