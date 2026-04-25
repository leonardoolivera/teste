# 0203 — Roadmap 1000 estratégias

**Status:** Accepted — backlog pronto para execução serial
**Date:** 2026-04-21
**Deciders:** Usuário ("roadmap 1000 estrategias depois 1 por 1") + agente
**Relates to:** ADR-0202 (TF10m exauridamente refutado), ADR-0183 (frentes residuais), Padrões 46/48/50

## Contexto

Após cobertura exaustiva TF10m (4 Fases, 93 probes, 8 engines, stack inalterado), user pediu roadmap de **1000 estratégias** para executar 1-a-1. Necessidade: uma agenda de pesquisa de longo prazo cobrindo direções pouco exploradas, validação cross-era dos achados marginais (Padrão 50 bear-avoidance, Padrão 48 SOL regime), grids de parâmetro sistemáticos, e frentes residuais (portfolio, stress adversarial, exotic signals).

## Estrutura do roadmap

Arquivo gerado: [`decisions/roadmap_1000.md`](roadmap_1000.md) + [`exports/diag/roadmap_1000.json`](../exports/diag/roadmap_1000.json) (machine-readable).

Gerador: [`tools/gen_roadmap_1000.py`](../tools/gen_roadmap_1000.py) — reprodutível/editável.

**Distribuição por tier** (prior descendente):

| Tier | Count | Prior típico | Conteúdo |
|---|---:|---:|---|
| T1 | 217 | 15-30% | High-EV: Padrão 50 cross-era, Padrão 48 SOL regime, portfolio stack13, regime detection meta, param sensitivity stack |
| T2 | 300 | 10-12% | Param grid BB/RSI/composite em 1h canonical + filter combinations |
| T3 | 268 | 5-15% | Coverage gaps: TFs × non-MR, short variants, Keltner/zscore reabertura restritiva, asset expansion LINK/DOT/AVAX |
| T4 | 215 | 5-40% | Long tail: stress adversarial, ablation, exotic signals (código novo), ML experiments (código novo) |

**Total: 1000.**

## Orçamento de compute

- ~10 min/probe médio (walk-forward 5 folds + MC 1000 + stress 2 cenários)
- Serial: 1000 × 10min = **167h** (~7 dias 24/7) de compute wall-clock
- Prático: distribuir em **Fases de 20-30 probes** (cada Fase: 3-5h de compute)
- **~40 Fases total** para esgotar roadmap

Aviso: Tier 4 exotic/ML (~140 entries) **requer código novo** (features orderbook, funding, CVD, ML models) — não é execução pura de CLI existente. Estimativa de dev adicional: ~20-40h por feature exotic. Deixar tier 4 para final.

## Ordem de execução sugerida

1. **Tier 1 primeiro** (217 probes, ~36h compute)
   - 1.a. Padrão 50 cross-era MA+ST (60 probes, ~10h): direct test do único achado positivo 10m.
   - 1.b. Padrão 48 SOL regime replication (60 probes, ~10h): validar se é windowregime ou engine-generalizable.
   - 1.c. Portfolio stack13 (50 probes, ~8h): segunda maior prioridade (combinar winners).
   - 1.d. Regime detection meta (50 probes, ~8h): gated strategy alocação dinâmica.
   - 1.e. Stack param sensitivity (~30 probes): robustez das já validadas.

2. **Tier 2** (300 probes, ~50h): grid systematic se Tier 1 não resolver.

3. **Tier 3** (268 probes, ~45h): gaps coverage; asset expansion requer ingest LINK/DOT/AVAX dados.

4. **Tier 4** (215 probes, ~35h + dev time): last resort + exotic/ML com código novo.

## Gates e encerramento por Fase

Cada Fase (bloco de probes de uma subcategoria) segue padrão ADR pré-reg:

- **Gate padrão**: `annual_sharpe ≥ 1.5 AND trades ≥ 30` por probe.
- **Gate alfa** (novo, aprendido em Fase 4): `pnl_pct_probe > pnl_pct_bh / alavancagem` — superar B&H ajustado pela alavancagem para contar como edge real.
- **Gate agregado por Fase**: ≥2/N probes passam gate Sh **E** gate alfa.
- Refutação: ADR de closeout com análise de patterns + update STATE.

## Stop conditions

Roadmap **não é obrigatório**. Parar antecipado se:
- 2 Fases consecutivas em Tier 1 passam gate → promover + consolidar stack v4.
- 5 Fases consecutivas em Tier 1 refutam → reevaluar validade da direção e possivelmente pular tiers.
- User direct redirect → obedecer escopo novo.

## Não-alvo

- Não executar todas 1000 probes sem check-in intermediário (desgasto cognitivo + context risk).
- Não promover single-probe pass sem cross-era validation (lição dos Padrões 45/48/50).
- Não skip pré-reg ADR por Fase (integridade metodológica).
