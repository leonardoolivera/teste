# 0003 — Validação mínima: walk-forward causal + Monte Carlo sobre trades

**Status:** Accepted
**Date:** 2026-04-17
**Deciders:** Usuário (owner do projeto) + agente.

## Context

`vision/01-product.md` coloca "validação anti-overfitting embutida" como **Definition of success** — nenhuma estratégia entra no ranking sem passar por walk-forward, out-of-sample, Monte Carlo e perturbação de custos. Até aqui, o módulo `src/alpha_forge/validation/` ficou segurado por AGENTS.md §4 (núcleo mínimo primeiro). `ranking/`, `regimes/`, stress de custos, parameter stability e robustness score continuam deliberadamente segurados.

ADR-0002 proíbe lookahead por infraestrutura. Um validador que fizesse leak de informação do teste para o treino (ou que passasse parâmetros futuros para um fold passado) violaria isso de forma sutil — exatamente o tipo de erro que o projeto existe para evitar. O desenho do `validation/` precisa herdar o mesmo contrato do `backtest/`: causalidade como propriedade verificável, não como promessa.

Esta ADR abre o módulo `validation/` no **menor tamanho honesto** — o suficiente para rodar o pipeline end-to-end uma vez sobre uma estratégia real, e para que as extensões futuras (stress, ranking, regimes) entrem por ADRs próprias em cima de um contrato já existente.

## Decision

Escopo mínimo do módulo `validation/` nesta ADR:

1. **Walk-forward causal com folds disjuntos.**
   - Divide o dataset em **N** janelas de teste contíguas, disjuntas e de tamanho aproximadamente uniforme (último absorve o resto quando `len(prices)` não divide exatamente). `N = n_folds ≥ 2`.
   - Para cada fold `k ≥ 1`, `test_window[k]` é o bloco `[k * test_size, (k+1) * test_size)`; `train_window[k]` é o passado anterior. **Fold 0 é sempre pulado** porque walk-forward exige sempre `train` antes de `test`. Se todos os folds caírem nesse caso, `ValidationError`.
   - Dois esquemas para o `train_window`:
     - `scheme="rolling"` (default): janela fixa de tamanho `int(train_fraction * test_size)` imediatamente antes do teste.
     - `scheme="expanding"`: toda a história do início do dataset até o início do teste.
   - `train_start == 0` (expanding) ou `train_start = test_start - train_size` (rolling); `train_end == test_start` (exclusive); `test_start == train_end + 1 bar`. **Sem overlap, sem gap, sem shuffle.**
   - **Hoje o training não ajusta parâmetros** — a estratégia é fixa (entra com hiperparâmetros já escolhidos). O `train_window` existe **estruturalmente** no schema (`WalkForwardFold.train_window`) mas nenhum backtest é rodado no train nesta ADR. Otimização por fold vira ADR futura (parameter stability); abrir os dois ao mesmo tempo convida overfitting metodológico.
   - Cada fold roda `run_backtest` sobre o `test_slice` com `dataset_id = f"{dataset_id}#fold{k}"` — mantém auditabilidade no `BacktestResult.dataset_id` e impede colisão de runs na eventual persistência futura.
   - Causalidade: herdada por construção. Cada `test_slice` é um `DataFrame` recortado e `run_backtest` aplica `assert_causal` internamente (ADR-0002).
   - **Sem embargo entre train e test** nesta versão. Justificativa: estratégia não é retreinada, então não há leak via parâmetros. Se ADR futura abrir otimização por fold, abrir embargo junto.
   - Validações na entrada da função (eager, antes de qualquer backtest): `n_folds >= 2`; `train_fraction ∈ (0, 1)`; `min_test_bars >= 1`; `scheme ∈ {"rolling", "expanding"}`; `test_size = len(prices) // n_folds >= min_test_bars`. Falha → `ValidationError` com mensagem específica.

2. **Monte Carlo sobre a sequência de PnLs de trades (bootstrap com reposição).**
   - Input: `BacktestResult` inteiro. O Monte Carlo opera sobre `result.trades` — a lista de trades fechados, já com `pnl` pós-custo computado pelo engine (ADR-0006/0007).
   - Resampling: **bootstrap com reposição**, tamanho do resample = número original de trades. Aleatoriedade determinística: `seed` é **obrigatório** na assinatura de `monte_carlo_trades`; run sem seed persistido não entra em relatório de ranking (ADR-0002 §reprodutibilidade).
   - `n_resamples` mínimo 100 (validado em função); default sensato é 1000 (do chamador). Máximo não é limitado pelo contrato — é limitado pelo tempo.
   - Em cada simulação: PnLs reamostrados somam-se cumulativamente à partir de `capital_inicial`; reconstrói curva de equity e calcula `max_drawdown` por simulação.
   - Estatísticas sumárias: percentis **5, 25, 50, 75, 95** de `final_equity` e de `max_drawdown`. Conjunto fixo (não configurável) — cauda + quartis + mediana sem explodir superfície. Acrescentar percentis exige ADR.
   - `result.trades` vazio → `ValidationError`. Monte Carlo sobre zero trades é simular zeros; o chamador precisa saber que o backtest não entrou em posição nenhuma vez.
   - **Limitação declarada no código**: assume PnL de trade i.i.d., o que é falso em regimes com autocorrelação serial. Bootstrap em blocos / circular block bootstrap são deferred para ADR futura.
   - **Não** aleatoriza timestamps nem preços — só a sequência de trades. Monte Carlo sobre preços sintéticos (GBM, bootstrap de retornos) é ADR separada; sobre trades responde "o quanto o resultado dependeu da ordem de chegada dos trades vencedores/perdedores?", que é a primeira pergunta útil num laboratório.

3. **Relatório mínimo.**
   - `WalkForwardFold`: `fold_index`, `train_window`, `test_window` (`WalkForwardWindow` com `start`, `end`, `bars`), `result: BacktestResult` completo (inclui `BacktestMetrics` via `result.metrics`).
   - `MonteCarloSummary`: `n_resamples`, `seed`, `final_equity_percentiles: dict[int, float]`, `max_drawdown_percentiles: dict[int, float]`, `original_final_equity`, `original_max_drawdown` — chaves dos percentis fixas em `{5, 25, 50, 75, 95}`.
   - **Nenhuma flag de fragilidade aqui.** `CURVE FIT PROVÁVEL`, `FRÁGIL`, `NÃO GENERALIZA` exigem critério explícito contra thresholds, e thresholds dependem de calibração empírica que só faz sentido com catálogo de estratégias + dataset catalog — `ranking/` + ADR futura.

4. **Integração com `backtest/engine.py` — zero mudança de contrato.**
   - `run_backtest` não muda. `validation/` **chama** `run_backtest` internamente uma vez por fold (walk-forward) ou zero vezes (Monte Carlo opera sobre trades de um backtest já rodado, passado como input).
   - `lookahead_guard.assert_causal` roda dentro de cada `run_backtest` como sempre. Nenhum bypass em `validation/`.
   - Invariante ADR-0010 (monotonicidade de custo) continua valendo por fold (o invariante é sobre cenário fixo, e cada fold é cenário fixo isoladamente); não é re-testado aqui.

5. **Contrato funcional.**
   - `validation/walk_forward.py::walk_forward(*, prices, strategy, budget, cost_model, dataset_id, n_folds, scheme="rolling", train_fraction=0.5, min_test_bars=50) -> list[WalkForwardFold]`.
   - `validation/monte_carlo.py::monte_carlo_trades(*, result, capital_inicial, n_resamples, seed) -> MonteCarloSummary`.
   - `validation/schemas.py` — pydantic frozen para `WalkForwardWindow`, `WalkForwardFold`, `MonteCarloSummary`. Validators em todos os campos numéricos.
   - Funções puras; sem I/O; sem persistência. Persistência (`results/validation/`) vira ADR separada quando `ranking/` precisar consumir.
   - `validation/__init__.py` reexporta os nomes públicos; namespace é parte do contrato.

6. **Testes obrigatórios como critério de "entregue".**
   - Unit: `tests/unit/test_validation_schemas.py` — construtores rejeitam `n_resamples < 100`, `seed` ausente/negativo, `bars < 0`.
   - Unit: `tests/unit/test_walk_forward.py` — dataset sintético com número conhecido de barras produz exatamente N−1 folds (fold 0 pulado); folds de teste são disjuntos em tempo; `train.end + 1 bar == test.start`; `scheme="expanding"` sempre começa em `train_start == 0`; `scheme="rolling"` respeita `train_fraction`; `n_folds < 2` e `train_fraction` fora de `(0, 1)` falham com `ValidationError`; dataset curto (`test_size < min_test_bars`) falha; cada fold tem `result.dataset_id == f"{dataset_id}#fold{k}"`.
   - Unit: `tests/unit/test_monte_carlo.py` — `n_resamples < 100` falha; `capital_inicial ≤ 0` falha; `result.trades` vazio falha; com `result.trades` conhecido (ex: dois trades com PnL `[+100, -50]`) e `seed` fixo, percentis retornados estão dentro da faixa plausível (`p05 ≥ capital − 2*|max(|pnl|)|`, `p95 ≤ capital + 2*max(pnl)`); `original_final_equity` e `original_max_drawdown` são copiados do `result`.
   - Property: `tests/property/test_monte_carlo_determinism.py` — mesma terna `(result, n_resamples, seed)` produz `MonteCarloSummary` bit-a-bit idêntico em duas execuções consecutivas. Regressão dura contra "alguém puxou `np.random.random()` sem passar pelo `rng`".

## Consequences

- **Positive:** o pipeline end-to-end descrito em `vision/01` agora tem pelo menos uma versão rodável — o laboratório sai do estado "sem validação implementada" sem abrir simultaneamente ranking, regimes e stress. Qualquer estratégia real pode ser rodada sob walk-forward + Monte Carlo com contratos explícitos. A meta de "pipeline end-to-end < 10 min" deixa de ser só extrapolação: vira número medível a partir desta ADR.
- **Negative:** a versão entregue é deliberadamente conservadora — sem otimização por fold, sem embargo, sem bootstrap por bloco, sem stress de custos, sem flags de fragilidade. Quem consumir o relatório precisa entender isso, e o texto do relatório deve deixar claro. O risco é a tentação de "só acrescentar uma flag" sem abrir ADR — cada extensão tem que passar por ADR.
- **Neutral:** `validation/` ganha forma pública pela primeira vez; qualquer ADR futura que expanda vai referenciar esta. A escolha "bootstrap de trades" (não de retornos nem de preços) é padrão de literatura (Lopez de Prado, *Advances in Financial Machine Learning*, cap. 12) mas não é a única opção — ADR futura pode substituir por resampling mais sofisticado sem quebrar interface.

## Alternatives considered

- **Walk-forward com janela expansiva (train cresce, test rola) como único modo.** — Rejeitado: o código suporta `scheme="expanding"` como opção, mas obrigar expanding desde o começo fecha portas antes da hora (rolling é útil quando o regime do mercado muda e histórico antigo vira ruído).
- **Monte Carlo sobre retornos diários da curva de equity.** — Rejeitado: a curva de equity do backtest é função dos trades na ordem original; reamostrar retornos diários desfaz a estrutura de trade (efeito do `fracao_por_trade` e da alavancagem some). Bootstrap de trades preserva essa estrutura.
- **Monte Carlo sobre preços sintéticos (GBM / bootstrap de retornos do ativo).** — Rejeitado nesta versão: gera controle muito diferente — é "o que aconteceria se o preço tivesse outro caminho", não "o que aconteceria se o viés de seleção dos trades fosse outro". Ambos são úteis; o segundo é mais barato e mais direto para caracterizar sorte-na-sequência. Primeiro vira ADR futura.
- **Percentis configuráveis.** — Rejeitado: superfície configurável sem caso de uso gera ruído. Fixar `{5, 25, 50, 75, 95}` já dá cauda + quartis + mediana; trocar exige ADR e um motivo.
- **Incluir flags `CURVE FIT PROVÁVEL` / `FRÁGIL` / `NÃO GENERALIZA` nesta ADR.** — Rejeitado: thresholds sem calibração empírica viram ruído. Abrir com `ranking/`, quando houver base para calibrar.
- **Abrir também `ranking/` ou `regimes/` junto.** — Rejeitado: AGENTS.md §4 — núcleo mínimo, adicionar depois é barato. Fica tentador pela proximidade conceitual; é tentação.
- **Persistir relatórios em `results/validation/` já nesta ADR.** — Rejeitado: persistência é contrato com `ranking/`, que ainda não existe. Formato do arquivo hoje seria chute; amanhã seria dívida.

## Follow-ups

- `src/alpha_forge/validation/schemas.py`, `walk_forward.py`, `monte_carlo.py` e `__init__.py` — **implementados no mesmo ciclo desta ADR** (código já presente).
- `tests/unit/test_validation_schemas.py` — a escrever (follow-up desta ADR).
- `tests/unit/test_walk_forward.py` — a escrever.
- `tests/unit/test_monte_carlo.py` — a escrever.
- `tests/property/test_monte_carlo_determinism.py` — a escrever.
- Atualizar `system/domain.md`, `system/api.md`, `system/flows.md` com os novos módulos e flows.
- Atualizar `STATE.md`.
- **Não abrir**: CLI exposta para validation (vira follow-up de `ranking/`), stress de custos (ADR futura), parameter stability (ADR futura), bootstrap de retornos (ADR futura), flags de fragilidade (ADR + `ranking/`), otimização/tuning por fold (ADR futura).
