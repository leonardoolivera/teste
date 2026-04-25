# VALIDATION.md — {{NOME DA ESTRATÉGIA}}

> **Template.** Copie para `agentic/active/<slug>/VALIDATION.md` e preencha. Remova este bloco de nota ao finalizar.
> Produzido pelo `backtest-validator` após `IMPLEMENTATION.md` completo.

---

## Testes executados

### Suíte completa

- **Comando:** `python -m pytest -q`
- **Resultado:** `{{N}} passed, {{M}} skipped` em `{{tempo}}s`.

### Novos testes desta entrega

| Arquivo | Tipo | Descrição | Verde/Vermelho |
|---|---|---|---|
| `tests/unit/test_{{familia}}.py` | unit | {{classes}} | {{N/N verde}} |
| `tests/property/test_{{familia}}_causal.py` | property | {{descrição}} | {{N/N verde}} |
| `tests/integration/test_{{...}}` | integration | {{descrição}} | {{N/N verde}} |

### Property-based de causalidade (ADR-0002)

- Cobre OHLCV completo? {{sim/não}}.
- Número de exemplos: {{hypothesis max_examples}}.
- Shrink cases: {{N/A ou lista}}.

### Property-based de monotonicidade de custo (ADR-0010 + ADR-0019)

- Fee monotonicity: {{verde/vermelho}}.
- Slippage monotonicity: {{verde/vermelho}}.
- Spread monotonicity: {{verde/vermelho}}.

## Conformidade ao SPEC

| SPEC §seção | Evidência de teste | Status |
|---|---|---|
| Hipótese | {{backtest em dataset real}} | {{characterização}} |
| Mercado | {{dataset_id usado}} | OK |
| Timeframe | {{grão do dataset}} | OK |
| Entradas | {{TestEntrada...}} | {{OK/GAP}} |
| Saídas | {{TestSaida...}} | {{OK/GAP}} |
| Stops | {{teste | N/A}} | {{OK/GAP}} |
| Sizing | via `fixed_fractional_position_sizing` | OK |
| Fees | `CostModel.taker_fee_bps` testado | OK |
| Slippage | monotonicidade em ADR-0010 | OK |
| Spread | monotonicidade em ADR-0019 | OK |
| Funding | {{N/A | deferred}} | {{nota}} |
| Condições inválidas | {{teste warm-up}} | OK |
| Limitações conhecidas | {{registradas}} | OK |

## Falhas conhecidas

{{Lista testes que passaram mas são fracos, testes pendentes, gaps do SPEC. Cada um com razão.}}

- {{falha 1}} — razão: {{...}}

## Comando de reprodução

```bash
python -m pytest -q tests/unit/test_{{familia}}.py tests/property/test_{{familia}}_causal.py
alpha-forge validate --run-id {{slug}} --dataset-id {{dataset}} --strategy {{familia}} --n-folds 5 --mc-resamples 500 --mc-seed 42 --stress fee+10:10:0:0 --stress slip+5:0:5:0 --stress spread+10:0:0:10
```

- Comando **sem** argumentos opcionais → reprodutibilidade ADR-0017 (via `run.json`).
- `--mc-seed 42` é arbitrário mas fixo para esta corrida.
