# 0019 — Synthetic spread as third cost component

**Status:** Accepted
**Date:** 2026-04-17
**Deciders:** Usuário (owner do projeto) + agente.

## Context

O `CostModel` mínimo da ADR-0006 cobre dois componentes: `taker_fee_bps` (fee base aplicado em cada fill) e `slippage_bps_per_unit_notional` (slippage linear por notional/capital). `vision/02-scope.md` §"backtest" declara **spread sintético** como capability esperada do módulo, separado de maker/taker e funding. A ADR-0006 §"Explicitamente fora do escopo" também o listou como ADR futura.

Hoje, `apply_cost` trata slippage como proxy informal de tudo que não é fee — mas um trader que abra e feche posições pequenas (notional → 0) paga fee quase zero e slippage quase zero, ignorando que todo mercado tem bid-ask estrutural. Isso enviesa estratégias de alta frequência em notionals pequenos. Antes de abrir `ranking/` (próximo grande consumidor), queremos que o `CostModel` cubra o atrito estrutural de spread independente de tamanho — separando claramente "fee de corretora" (`taker_fee_bps`), "impacto proporcional ao tamanho" (`slippage_bps_per_unit_notional`) e "spread estrutural do mercado" (`spread_bps`).

Maker vs taker e funding ficam explicitamente fora desta ADR — exigem decisões maiores (anotar `Signal` para marcar maker intent, série adicional no manifesto para funding rate por barra). Spread é o componente mais simples dos três listados em ADR-0006 §"Fora do escopo": aditivo em bps, independente de notional/direção, compatível com a forma `total_bps` existente de `apply_cost`.

## Decision

Adicionar **um terceiro componente não-negativo ao `CostModel`**: `spread_bps: float = Field(ge=0.0, default=0.0)` — representa half-spread efetivo em basis points aplicado **contra o trader** em cada fill, somado diretamente ao `total_bps` calculado por `apply_cost`.

**Regra exata:**

```
total_bps = taker_fee_bps
          + slippage_bps_per_unit_notional * (notional / capital_inicial)
          + spread_bps
```

Resto de `apply_cost` inalterado. Direção do ajuste continua sendo "contra o trader" (compra paga mais, venda recebe menos).

**Default `0.0` preserva comportamento bit-a-bit da ADR-0006.** Chamadores antigos de `CostModel(taker_fee_bps=..., slippage_bps_per_unit_notional=...)` continuam funcionando sem mudar; `zero_cost()` também. Isso é crítico — `validation/cost_stress.py`, `validation/walk_forward.py`, `validation/persistence.py`, `cli/app.py`, testes property-based, todos constroem `CostModel` ou consomem seu dump. O default zero mantém todos bit-a-bit.

**Exposição via CLI:** nova flag compartilhada `--spread-bps` (default `0.0`) em `run-demo` e `validate`, passada para o construtor de `CostModel`. Mesmo padrão das flags `--taker-fee-bps` e `--slippage-bps-per-notional`.

**Exposição via `validation/cost_stress.py`:** `CostPerturbation` ganha campo opcional `spread_delta_bps: float = Field(ge=0.0, default=0.0)`, com mesma semântica aditiva não-negativa dos deltas existentes. CLI `--stress label:fee:slip` passa a aceitar opcionalmente uma **quarta parte** `label:fee:slip:spread`; formato de 3 partes permanece válido (`spread_delta_bps=0.0` implícito) para preservar corridas antigas. Parser rejeita 5+ partes.

**Persistência (ADR-0015+ADR-0017):** `schema_version` do envelope **não** muda. Pydantic aceita o novo campo com default em payloads antigos (JSONs gravados antes desta ADR carregam com `spread_bps=0.0` automaticamente). Testado explicitamente — round-trip bit-a-bit de artefato antigo é preservado.

**Monotonicidade ADR-0010 estendida:** se `spread_bps_high ≥ spread_bps_low` (mantendo os outros dois componentes iguais), então `final_equity_high ≤ final_equity_low + tolerance`. Pelo menos um novo property-based test cobre a direção spread isolada; os testes existentes (MA/Donchian × long/short) ganham cobertura implícita via composição de deltas no `@st.composite dominated_cost_pair`.

## Consequences

- **Positive:** `CostModel` passa a modelar explicitamente o atrito estrutural que não depende de tamanho — corrige o viés de estratégias "abusando" de notional pequeno. Realismo do backtest cresce sem abrir módulo novo nem tocar engine. Retrocompatibilidade bit-a-bit: todo JSON persistido pré-E.9 carrega sem migração, todo código que constrói `CostModel` com 2 args continua funcionando. Preparação direta para `ranking/` (próximo consumidor sabe que o `CostModel` já reflete os três componentes de atrito listados em `vision/`).
- **Negative:** a CLI `--stress` passa a aceitar 3 **ou** 4 partes, que é marginalmente mais complexo para documentar. `@st.composite dominated_cost_pair` e sua duplicata em 3 arquivos paralelos (MA/Donchian × long/short) precisam passar a sortear o terceiro componente — trabalho mecânico mas toca 4 arquivos property-based. `CostPerturbation` ganha um campo opcional; consumidores que iterassem sobre seus campos por `model_fields` (nenhum em `src/` hoje) veriam o novo campo.
- **Neutral:** `spread_bps` é aditivo em bps como os outros — não existe "cenário spread zero igual a slippage zero"; continuam sendo dois eixos diferentes do atrito. Quem quer isolar comportamento velho passa `spread_bps=0.0` explicitamente; quem não passa nada também fica em zero.

## Alternatives considered

- **Multiplicar `spread_bps` por `(notional / capital_inicial)`** — rejeitado: seria indistinguível de `slippage_bps_per_unit_notional`. Spread estrutural é atrito fixo por fill, independente de tamanho; essa é a razão de ele ser um componente separado, não um ajuste de slippage.
- **Modelar spread como bid-ask explícito no preço** — rejeitado: exigiria mudar o schema de dados para incluir `bid`/`ask` por barra (hoje só temos OHLCV). Viola a regra "dois componentes aplicados no preço" da ADR-0006; expande o manifesto ADR-0005 (hoje só sha256 do OHLCV) sem motivo forte. Aditivo em bps preserva a forma declarada da ADR-0006 §"Aplicação determinística".
- **Expor como campo obrigatório sem default** — rejeitado: quebraria todos os consumidores atuais de `CostModel` (CLI, `cost_stress`, property-based, persistence). Default zero é retrocompatível e bit-a-bit.
- **Apertar a semântica "spread" para "half-spread" explicitamente no nome (`half_spread_bps`)** — rejeitado: o valor em bps é intuitivamente "what you lose crossing the book once"; adicionar "half" no nome força o usuário a pensar em termos de full-spread e dividir. Mantemos `spread_bps` como o que é efetivamente pago em cada fill.
- **Adicionar funding junto (`funding_bps_per_hour`)** — rejeitado nesta ADR: funding exige `hours_in_position` por Trade, o que muda o engine (hoje não há rastro de tempo em posição). Vira ADR própria quando houver consumidor real.
- **Adicionar maker/taker junto** — rejeitado nesta ADR: maker exige anotar `Signal` para marcar intent, o que muda o contrato de `StrategyProtocol`. ADR separada com superfície maior.
- **Elevar `spread_bps` só na CLI, sem mexer em `CostPerturbation`** — rejeitado: cost_stress (ADR-0014) é o jeito canônico de sensibilizar custos; deixar o novo componente fora dele tornaria o stress incompleto. O custo de estender `CostPerturbation` é mínimo (campo opcional com default).
- **Aceitar `spread_bps` negativo** (para simular rebate) — rejeitado: viola o princípio "atrito, não prêmio" declarado na ADR-0006 §"Aplicação determinística". Rebate é maker fee, não spread; se entrar, é ADR própria.

## Follow-ups

Concrete actions this decision creates. Each one belongs in `STATE.md` as pending work.

- Estender `src/alpha_forge/backtest/cost.py` com `spread_bps: float = Field(ge=0.0, default=0.0)`; atualizar `apply_cost` somando `cost_model.spread_bps` ao `total_bps`. `zero_cost()` permanece bit-a-bit idêntico (default zero do novo campo).
- Estender `src/alpha_forge/validation/schemas.py::CostPerturbation` com `spread_delta_bps: float = Field(ge=0.0, default=0.0)`. Nenhuma mudança em `CostStressCell`/`CostStressReport`.
- Estender `src/alpha_forge/validation/cost_stress.py` para validar "nem tudo zero" considerando os três deltas e somar `spread_delta_bps` ao `spread_bps` efetivo de cada cenário.
- Estender `src/alpha_forge/cli/app.py`: nova flag compartilhada `--spread-bps` (default `0.0`); `parse_stress_specs` passa a aceitar 3 **ou** 4 partes (`label:fee:slip[:spread]`), rejeitando ≥5 partes e labels/valores inválidos como hoje. Summary de `run-demo` ganha `spread_bps` na linha `cost_model`.
- Estender `tests/unit/test_cost_model.py`: 4 testes novos — `spread_bps` default é 0; aplicado contra o trader nas 4 direções (entrada/saída × long/short); soma linear com os outros dois componentes; `spread_bps` ≥ 0 (pydantic rejeita negativo).
- Estender `tests/unit/test_cost_stress_schemas.py`: spread_delta_bps default, rejeição de negativo, validação "nem tudo zero" considera spread.
- Estender `tests/unit/test_cli_parse_stress.py`: 3 testes novos — formato 4 partes com spread positivo; spread como string "0" aceito; 5+ partes rejeitado; retrocompatibilidade (3 partes → spread_delta_bps=0.0).
- Novo `tests/property/test_cost_monotonicity_spread.py` exercitando isolamento do componente spread: `@st.composite` varia só `spread_bps` (outros componentes fixos), invariante ADR-0010 segue valendo.
- `tests/unit/test_validation_persistence.py`: adicionar 1 teste confirmando que JSON antigo (sem `spread_bps` em `CostModel` dump) carrega via pydantic com default zero — retrocompatibilidade formal.
- Atualizar `system/domain.md` (`CostModel` ganha terceiro campo; `CostPerturbation` ganha quarto delta opcional), `system/api.md` (`CostModel.spread_bps` documentado; CLI `--spread-bps` e formato `label:fee:slip[:spread]`), `system/flows.md` (flow `run-demo` menciona o componente; flow `cost_stress` menciona perturbação opcional), `decisions/README.md` (índice com linha da ADR-0019), `STATE.md` (entrega + Next step pós-E.9).
- Gate anti-hardcode verificado: `rg -n 'BTC|ETH|SOL' src/` = 0.
