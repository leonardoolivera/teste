# 0014 — Stress de custos sistematizado

**Status:** Accepted
**Date:** 2026-04-17
**Deciders:** Usuário (owner do projeto, em modo autônomo sequencial) + agente.

## Context

ADR-0003 abriu `validation/` no menor tamanho honesto — walk-forward causal + Monte Carlo sobre trades. Stress de custos ficou explicitamente **deferred** naquela ADR (§"Não entra neste núcleo mínimo"; §"Alternatives considered"). Três entregas da Frente E depois (E.1/E.2/E.3), a matriz 4× de monotonicidade de custo está completa: para cada família × cada modo (`MA × {long_only, simétrico}`, `Donchian × {long_only, simétrico}`) existe um property-based que prova que custo maior nunca melhora `final_equity` em cenário fixo (ADR-0010 generalizada).

A propriedade **"custo maior ≤ custo menor"** cobre uma direção (corretude estrutural). O que falta é a **grade perpendicular**: dado um cenário fixo (uma estratégia, um dataset, um budget), **quanta dependência** de custo a estratégia tem? Uma estratégia que só é lucrativa com taker_fee_bps = 0 e slippage_bps = 0 é frágil no sentido clássico de edge-case — passa no ADR-0010 mas não sobrevive a custo realista. Hoje o laboratório responde à primeira pergunta (monotonicidade), não à segunda (quão rápido deteriora).

Vision §"Definition of success" inclui "perturbação de custos" como um dos quatro filtros anti-overfitting. O módulo que cumpre esse papel não existe. Esta ADR abre esse módulo no **menor tamanho honesto** — o suficiente para gerar uma tabela de cenários perturbados sobre uma estratégia real, com contrato explícito, e deixar extensões (ranking, flags de fragilidade, agregação cross-estratégia) para ADRs próprias.

## Decision

Abrir `validation/cost_stress.py` dentro do módulo `validation/` já existente (ADR-0003). **Não** criar `stress/` como módulo raiz: stress de custos é avaliação sobre um backtest paramétrico, mesmo contrato que walk-forward + Monte Carlo — é natural ficar lado a lado. Se, no futuro, stress de preço, stress de dataset, ou stress de hiperparâmetros entrarem, a questão de "promover `stress/` para raiz" volta como ADR; abrir top-level agora é decidir isso sem evidência.

Escopo mínimo desta ADR:

1. **Contrato funcional.**
   - `validation/cost_stress.py::cost_stress(*, prices, strategy, budget, baseline_cost, perturbations, dataset_id) -> CostStressReport`.
   - `prices`, `strategy`, `budget`, `dataset_id` são os mesmos passados para `run_backtest` — mesma semântica, mesma herança de causalidade.
   - `baseline_cost: CostModel` — cenário de referência. **Roda primeiro**, e é a linha `scenario_index=0` da tabela.
   - `perturbations: list[CostPerturbation]` — lista ordenada de deltas **absolutos aditivos** em bps sobre o `baseline_cost`. Cada perturbação vira uma linha da tabela (`scenario_index ≥ 1`, na ordem da lista). Deltas não-negativos (`fee_delta_bps ≥ 0`, `slip_delta_bps ≥ 0`) — stress **aumenta** custo contra o trader; "reduzir custo" não é stress, é análise de sensibilidade paralela que, se precisar, vira ADR.
   - Pelo menos **uma** perturbação estritamente positiva na lista (pelo menos um `fee_delta_bps > 0` ou `slip_delta_bps > 0`); caso contrário, o report inteiro vira cópia do baseline e a chamada não está stressando nada — `ValidationError`.
   - `len(perturbations) ≥ 1` (pelo menos um cenário perturbado além do baseline) — uma linha só em tabela de stress é um backtest, não é stress.
   - **Função pura**; sem I/O; sem persistência. Consistente com `walk_forward` e `monte_carlo_trades`.

2. **Schemas (pydantic `frozen`, `extra="forbid"`).**
   - `CostPerturbation`: `fee_delta_bps: float ≥ 0`, `slip_delta_bps: float ≥ 0`, `label: str` (`min_length=1`, identificação humana do cenário).
   - `CostStressCell`: uma linha do relatório — `scenario_index: int ≥ 0`, `label: str`, `cost: CostModel` (o custo efetivo aplicado no run, `baseline + delta`), `result: BacktestResult` (inclui `metrics` via ADR-0007), `final_equity: float`, `final_equity_delta_vs_baseline: float` (sempre `≤ 0` para `scenario_index ≥ 1` pela ADR-0010 — propriedade verificada, não só esperada).
   - `CostStressReport`: `baseline: CostStressCell`, `scenarios: list[CostStressCell]` (não-vazia, na ordem de `perturbations`), `dataset_id: str`.

3. **Semântica de perturbação: absoluta aditiva, em bps.**
   - `CostModel` já expõe os componentes em bps (ADR-0006). Perturbar em bps absoluto mantém a unidade do contrato. Multiplicativa (`fee_bps *= 1.5`) quebra no cenário `baseline_cost = 0` (0 vezes qualquer coisa segue 0 — o cenário "dobrar o custo" deixa de existir). Aditivo em bps é robusto a baseline zero e fácil de ler em relatório.
   - `effective_fee_bps = baseline.taker_fee_bps + perturbation.fee_delta_bps`.
   - `effective_slip_bps = baseline.slippage_bps_per_unit_notional + perturbation.slip_delta_bps`.
   - Sem teto superior no contrato — quem define "cenário irrealista" é quem monta a lista. `run_backtest` não falha com custo alto; apenas rejeita trades (sizing inviável) com fills vazios. Se todos os trades forem rejeitados no cenário, `final_equity == capital_inicial` e o relatório mostra isso honestamente.

4. **Validações eager (antes de qualquer backtest).**
   - `baseline_cost is None` → `ValidationError`.
   - `perturbations` vazio → `ValidationError` (stress sem cenário é backtest único).
   - `perturbations` todo zero (nenhuma `fee_delta_bps > 0 OR slip_delta_bps > 0`) → `ValidationError` (o report seria degenerado).
   - `label` duplicado dentro da lista → `ValidationError` (relatório ambíguo é pior que erro).
   - Motivo de falhar cedo: evitar rodar N backtests antes de descobrir contrato violado.

5. **Integração com o engine — zero mudança de contrato.**
   - `run_backtest` **não** muda. `cost_stress` chama `run_backtest` uma vez por cenário (baseline + N perturbações = N+1 backtests). Todos com o mesmo `dataset_id` (o baseline não recebe sufixo — é o próprio dataset, exatamente como foi chamado; cenários perturbados recebem `f"{dataset_id}#stress{k}"` análogo ao sufixo `#fold{k}` da ADR-0003, por auditabilidade).
   - Causalidade: herdada por composição. Cada cenário é um `run_backtest` completo; `assert_causal` roda como sempre (ADR-0002).
   - Monotonicidade: `cost_stress` **assert-a** `final_equity_delta_vs_baseline ≤ FINAL_EQUITY_TOLERANCE` para cada `scenario_index ≥ 1`, com `FINAL_EQUITY_TOLERANCE = 1e-6 * budget.capital_inicial`. Violação não é flakiness — é bug no engine ou em `apply_cost`, e deve falhar alto. Se algum dia violar, inspecionar (não relaxar tolerância cegamente); mesma regra da ADR-0010.

6. **Relatório mínimo, não-interpretativo.**
   - `CostStressReport` é **dados brutos** + o `delta_vs_baseline` calculado. **Nenhuma flag** tipo `FRÁGIL`, `CURVE FIT PROVÁVEL`, `NÃO SUPORTA CUSTO`. Thresholds exigem calibração empírica que só faz sentido com catálogo de estratégias — `ranking/` + ADR futura (mesma regra da ADR-0003).
   - Persistência (arquivo em `results/validation/` ou similar) fica para ADR futura quando `ranking/` precisar consumir. Hoje é objeto em memória.

7. **Sem CLI exposta ainda.**
   - Mesma regra da ADR-0003: CLI de `validation/` fica para follow-up de `ranking/`. A função é chamável via Python (`from alpha_forge.validation import cost_stress`) e testável; CLI não é parte desta ADR.

8. **Testes obrigatórios como critério de "entregue".**
   - Unit: `tests/unit/test_cost_stress_schemas.py` — construtores rejeitam `fee_delta_bps < 0`, `slip_delta_bps < 0`, `label` vazio; `CostStressReport.scenarios` não-vazia; `frozen`; `extra="forbid"`.
   - Unit: `tests/unit/test_cost_stress.py` — (a) `perturbations` vazio → `ValidationError`; (b) `perturbations` todo zero → `ValidationError`; (c) `label` duplicado → `ValidationError`; (d) chamada feliz (MA 20/50 sobre sintético seminal com baseline zero + duas perturbações) devolve `CostStressReport` com `scenarios[0].cost.taker_fee_bps == baseline + fee_delta_bps` (aritmética do aditivo confere bit-a-bit); (e) `scenario_index` crescente a partir de 0; (f) `baseline.scenario_index == 0`; (g) `dataset_id` propagado com sufixo `#stress{k}` em cada cenário perturbado; (h) monotonicidade assertada em todos os cenários perturbados (reforça ADR-0010 por caminho diferente).
   - Integration: `tests/integration/test_cost_stress_pipeline.py` — pipeline end-to-end: `cost_stress` sobre MA 20/50 em dataset sintético seminal com 4 perturbações (fee+5, slip+5, fee+10&slip+10, fee+50&slip+100). Verifica: 5 linhas na tabela (baseline + 4), `final_equity` não-crescente ao longo dos 4 perturbados quando ordenados por custo total crescente (propriedade esperada por construção, não garantida em qualquer ordenação — a lista respeita a ordenação porque foi montada nessa ordem), `max_drawdown` bem definido em `[0, 1]` em todos.

9. **Relação com ADR-0010.**
   - ADR-0010 prova a invariante no campo property-based sobre pares `(cost_low, cost_high)` dominantes. `cost_stress` **aplica** a invariante a cenários enumerados por um consumidor. Os dois são complementares: property-based cobre arbitrário, cost_stress cobre a grade explícita que um analista quer reportar. O assert de monotonicidade dentro de `cost_stress` é defesa em profundidade, não redundância — se o engine regredir, os dois caminhos acusam.

## Consequences

- **Positive:** o laboratório ganha o terceiro dos quatro filtros anti-overfitting listados em `vision/01-product.md` (os outros três já são walk-forward, Monte Carlo, property-based de monotonicidade). Qualquer estratégia real pode ser caracterizada por uma tabela `baseline + perturbações` com contrato explícito. Monotonicidade passa a ser assertada também em runs não-propertybased — defesa em profundidade. Superfície do contrato cresce em 3 classes pydantic + 1 função, todos dentro de `validation/` — zero churn arquitetural.
- **Negative:** cada chamada roda N+1 backtests — custo linear no número de cenários. Para MA 20/50 sobre 720 barras sintéticas (~0.15 s/run), 5 cenários = ~0.75 s; para 4320 barras reais (~0.9 s/run), 5 cenários = ~4.5 s; dentro da folga da meta de 10 min do pipeline end-to-end (vision §Performance). O `CostStressReport` guarda `BacktestResult` completo por cenário — memória cresce linearmente; se virar problema, ADR futura pode introduzir modo "summary-only". Hoje não é problema: N é pequeno por design (nada no contrato empurra para 1000 cenários).
- **Neutral:** `validation/cost_stress.py` é o **segundo** módulo dentro de `validation/` (primeiro foi walk-forward, outro foi monte_carlo). O namespace `validation/` começa a virar um hub; quando o terceiro irmão entrar, pode valer promover subpastas — decisão para ADR futura, não agora. A escolha "aditivo em bps" é um contrato — se um dia precisar multiplicativo (ex: estudo de sensibilidade log-escala), a opção vira ADR nova com `CostPerturbation` estendida ou segunda função `cost_stress_multiplicative`; hoje é ruído.

## Alternatives considered

- **Módulo `stress/` no topo (raiz de `src/alpha_forge/`).** — Rejeitado: só existe stress de custos por enquanto; promover a raiz sem segundo irmão é desenhar abstração sem evidência. Se amanhã entrar `stress/price`, `stress/dataset`, `stress/hyperparams`, o refator de subir `cost_stress` de `validation/` para `stress/cost` é mecânico (2 arquivos + imports + `__init__.py`).
- **Perturbações multiplicativas (`cost *= 1.5`).** — Rejeitada como único modo: quebra no baseline zero (`0 * 1.5 = 0`, cenário "dobrar custo" desaparece); dificulta interpretar relatório ("o que é 1.5× de `taker_fee_bps=0`?"). Aditiva em bps é robusta ao zero e fácil de ler. Se precisar multiplicativo no futuro, ADR nova.
- **Grade implícita (passar `[5, 10, 20, 50]` bps, gerar o produto cartesiano automaticamente).** — Rejeitado: esconde o que foi rodado atrás de uma conveniência. Explicitar a lista de cenários torna o relatório auditável (quem leu este ADR sabe exatamente o que rodou). Wrapper que gera a lista pode viver em `scripts/` — não precisa ser contrato.
- **Flags de fragilidade (`FRÁGIL`, `CUSTO-SENSÍVEL`) no report.** — Rejeitado: thresholds sem calibração viram ruído (mesma regra da ADR-0003). Abrir com `ranking/` quando houver base para calibrar.
- **Persistir `CostStressReport` em `results/validation/cost_stress/`.** — Rejeitado nesta ADR: persistência é contrato com `ranking/`, ainda ausente. Hoje é objeto em memória. Quando `ranking/` precisar consumir, ADR futura desenha schema persistente.
- **Redução de custo (`fee_delta_bps < 0`) como parte do contrato.** — Rejeitado: stress é **aumentar** pressão contra o trader; reduzir custo é análise de sensibilidade paralela, útil mas diferente no sentido. Separar conceitualmente; se precisar, ADR nova com sinal explícito.
- **Integrar `cost_stress` dentro de `walk_forward` (rodar walk-forward × stress cartesiano).** — Rejeitado: dobra custo sem evidência de demanda; `walk_forward(..., cost_model=cost_stress(...))` não compõe trivialmente (tipos diferentes). Se o consumidor precisar "walk-forward + stress", monta o loop externamente. Se virar padrão, ADR futura.
- **Expor CLI `alpha-forge stress --scenarios ...`.** — Rejeitado (mesma regra da ADR-0003): CLI para `validation/` vira follow-up de `ranking/`. Função é chamável via Python + testável; isso basta.

## Follow-ups

- Implementar `src/alpha_forge/validation/cost_stress.py` (função + 3 schemas pydantic) no mesmo ciclo desta ADR.
- Atualizar `src/alpha_forge/validation/__init__.py` reexportando `cost_stress`, `CostPerturbation`, `CostStressCell`, `CostStressReport`.
- Escrever `tests/unit/test_cost_stress_schemas.py` e `tests/unit/test_cost_stress.py` + `tests/integration/test_cost_stress_pipeline.py`.
- Atualizar `system/domain.md`, `system/api.md`, `system/flows.md` e `decisions/README.md`.
- Atualizar `STATE.md`.
- **Não abrir**: CLI de stress (vira follow-up de `ranking/`); persistência do relatório (ADR futura); perturbação multiplicativa (ADR futura se tiver caso de uso); flags de fragilidade (ADR + `ranking/`); stress de preço / dataset / hiperparâmetro (ADRs separadas se entrarem); integração com walk-forward (ADR futura se virar padrão); redução de custo (ADR separada).
