# 0010 — Property-based test: cost monotonicity

**Status:** Accepted
**Date:** 2026-04-16
**Deciders:** Usuário (owner do projeto) + agente.

## Context

ADR-0006 declara que `CostModel` aplica atrito **contra o trader** no preço de execução. Hoje temos testes unitários que provam isso em 4 direções (entrada/saída × long/short) e em casos analíticos (`notional == capital`, zero-cost, etc.) — mas **não** temos uma garantia property-based de que a relação é *monotônica* em qualquer cenário plausível.

Essa garantia importa. Se alguma refatoração futura introduzir um caminho onde custo maior acaba beneficiando o trader (bug sutil de sinal invertido em algum ramo), os testes atuais podem não pegar. Property-based com `hypothesis` é a ferramenta natural para isso: gera centenas de cenários sintéticos e falha no primeiro que violar a invariante.

O usuário aprovou abrir essa propriedade como **frente curta e separada**, não como follow-up de ADR-0009. ADR própria, decisão pequena, teste reaproveitável.

## Decision

Adicionar `tests/property/test_cost_monotonicity.py`, que fixa **uma** invariante central:

> **Em um mesmo cenário determinístico** (mesmo dataset, mesma estratégia, mesmo `RiskBudget`, mesmo `dataset_id`), se o `CostModel` cresce monotonamente em qualquer dos seus dois componentes e `trade_count > 0` no cenário de referência, então `final_equity` **não aumenta**.

Formalmente: dado
- `result_low = run_backtest(cost_model=cost_low, ...)`
- `result_high = run_backtest(cost_model=cost_high, ...)`

com
- `cost_high.taker_fee_bps ≥ cost_low.taker_fee_bps`
- `cost_high.slippage_bps_per_unit_notional ≥ cost_low.slippage_bps_per_unit_notional`
- pelo menos **uma** das duas desigualdades estrita

a asserção é:

```
result_high.final_equity ≤ result_low.final_equity + tolerance
```

com `tolerance` numérica (ex.: `1e-6 * capital_inicial`) para absorver ruído de ponto flutuante.

### Ressalvas explícitas (parte da decisão)

1. **Zero trades no cenário `low`:** se `result_low.metrics.trade_count == 0`, a estratégia nunca entrou em posição e custo é irrelevante. `hypothesis` pula o exemplo via `assume(...)` — não é falha do teste, é cenário fora do domínio da invariante. Idem se `result_high.trade_count == 0`.
2. **Fills diferentes entre os dois runs:** custo mais alto encarece entradas, o que pode fazer `fixed_fractional_position_sizing` devolver um tamanho que cruza a fronteira de rejeição (`ABOVE_LEVERAGE_CAP`). Resultado: `result_high` pode ter **menos** fills que `result_low`. Isso é comportamento esperado e **não** viola a invariante — `final_equity` continua sendo uma função monotônica não-crescente em custo, porque "não entrou" é sempre melhor que "entrou e perdeu com custo alto". O teste não exige `len(fills_high) == len(fills_low)`.
3. **Determinismo do cenário:** dataset, estratégia, budget e `dataset_id` são **idênticos** nos dois runs. A única variável é `cost_model`. Qualquer outra divergência é bug do teste.
4. **Comparação estritamente em `final_equity`:** não em `total_pnl`, não em `hit_rate`, não em `max_drawdown`. Essas podem se comportar de forma não-monotônica por conta de efeitos de ordem (um trade a menos muda contagem e janela de drawdown). `final_equity` é a única métrica onde a invariante é matematicamente limpa.
5. **Escopo: apenas a estratégia ativa hoje.** A propriedade é testada com `MovingAverageCrossoverStrategy(20, 50)` (estratégia real, ADR-0008) sobre o dataset sintético seminal (`synthetic_btcusdt_1h_seed42`). Adicionar outras estratégias é mecânico e fica para follow-up natural quando cada nova estratégia entrar.
6. **Sobre a `DummyAlternatingStrategy`:** em princípio a invariante vale para qualquer estratégia causal. Mas a dummy negocia 239 vezes e seu PnL é quase nulo — ela é mais sensível a ruído numérico acumulado. Testá-la aqui seria exercício de tolerância, não de corretude. Fica de fora; reintroduzir só se virar útil.

### Shape do teste

Com `hypothesis`:

- Gera dois `CostModel` e impõe ordem via `assume(cost_high >= cost_low)` (componente a componente).
- `assume` pelo menos uma desigualdade estrita.
- Roda os dois backtests.
- `assume(result_low.metrics.trade_count > 0)` (descarta cenários triviais).
- `assert result_high.final_equity <= result_low.final_equity + tolerance`.
- `@settings(max_examples=30, deadline=None)` — 30 exemplos é suficiente para pegar bugs sistemáticos sem explodir tempo de CI; `deadline=None` porque cada exemplo roda dois backtests completos.

Faixas das flutuações para os componentes:

- `taker_fee_bps` ∈ `[0.0, 50.0]` (0 a 50 bps — cobre faixa realista de taker em cripto).
- `slippage_bps_per_unit_notional` ∈ `[0.0, 100.0]` (0 a 100 bps/notional — cobre até leverage alto com slippage agressivo).

### Onde vive

`tests/property/test_cost_monotonicity.py`. Mesma pasta do `test_lookahead_guard.py` e `test_ma_crossover_causal.py` — já é a camada de testes property-based.

## Consequences

- **Positive:** fecha o flanco de "custo maior nunca pode ajudar"; pega regressão sutil se alguém trocar sinal em `apply_cost` ou inverter o ramo `is_entry` por engano; exercita `run_backtest` end-to-end duas vezes com cenários adversariais gerados, o que por tabela exercita também o loop causal; primeira propriedade que vincula diretamente o contrato de `CostModel` ao `BacktestResult`.
- **Negative:** cada exemplo roda dois backtests completos de 720 barras → ~60 backtests por execução do teste; latência da suíte sobe (aceitável, ainda ordem de segundos); tolerância numérica precisa ser escolhida com cuidado — muito apertada causa flakiness, muito larga mascara bug (escolha inicial `1e-6 * capital_inicial` é defensável e fácil de revisar).
- **Neutral:** não substitui os testes unitários de `test_cost_model.py` (que isolam `apply_cost` sem o engine); é camada adicional, não substituta; aplicar a mesma propriedade à `DummyAlternatingStrategy` é trivial quando/se precisar.

## Alternatives considered

- **Testar monotonicidade em `total_pnl` em vez de `final_equity`** — rejeitado: `final_equity = capital_inicial + total_pnl`, portanto aritmeticamente equivalente; mas mantê-lo em `final_equity` deixa a relação com a curva de equity visível e dispensa aritmética auxiliar no teste.
- **Generar séries OHLCV aleatórias com `hypothesis` e rodar backtest sobre elas** — rejeitado nesta ADR: explode complexidade (precisa garantir invariantes de `OHLCVBar` no gerador, tratar warm-up, etc.); o dataset sintético seminal já é determinístico e suficiente para a propriedade; geração de série sintética para testes fica para quando tivermos mais de uma estratégia a comparar.
- **Cobrir também monotonicidade em `max_drawdown` ("custo maior nunca diminui drawdown")** — rejeitado: intuitivamente razoável, mas **falsa em geral**. Custo maior pode fazer a estratégia não entrar em um trade ruim; sem o trade, o drawdown acontece com menos equity em risco, e a curva pode de fato melhorar localmente. Monotonicidade só vale para `final_equity`.
- **Property em `apply_cost` puro, sem rodar o engine** — aceitável, mas já coberto pelos testes unitários analíticos em `test_cost_model.py`. O valor de rodar via `run_backtest` é cobrir interação entre custo, sizing e rejeição.
- **ADR-0010 como follow-up de ADR-0009** — rejeitado pelo usuário explicitamente: "O teste de custo merece ficar como decisão pequena, explícita e reaproveitável, sem ficar pendurado como detalhe de follow-up da ADR de dataset". ADR separada respeita essa direção.
- **Testar múltiplas estratégias no mesmo arquivo** — aceitável no futuro; por ora, uma estratégia (MA crossover) é suficiente para estabelecer a propriedade e o padrão de escrita. Outras estratégias adicionam testes análogos em momentos específicos.

## Follow-ups

- Implementar `tests/property/test_cost_monotonicity.py` conforme §"Shape do teste". Rodar `pytest -q` e verificar que passa com 30 exemplos sem flakiness.
- Se algum exemplo falhar durante implementação: **não** relaxar a tolerância cegamente. Primeiro inspecionar o caso gerado por `hypothesis` (ele reporta o shrink mínimo); se for ruído legítimo de ponto flutuante, ajustar tolerância documentando no comentário do teste; se for bug real, corrigir `apply_cost` ou o loop do engine e só então commitar.
- Quando ADR-0011 (Donchian breakout) entrar, replicar o teste com a nova estratégia em caso análogo (teste paralelo, não parametrização — cada estratégia é explícita).
- Quando primeiro dataset real (ADR-0009) entrar, **não** mover a propriedade para ele — dataset real é ortogonal. Teste continua sobre sintético seminal, que é determinístico e offline.
- Atualizar `system/flows.md` com entrada curta: "Flow: monotonicidade de custo (property-based)", análoga às entradas de `assert_causal` e `ma_crossover_causal`.
- **Não** tocar em `src/`. ADR-0010 é estritamente camada de testes.
