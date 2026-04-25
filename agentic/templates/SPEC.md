# SPEC.md — {{NOME DA ESTRATÉGIA}}

> **Template.** Copie para `agentic/active/<slug>/SPEC.md` e preencha. Remova este bloco de nota ao finalizar.
> **Release mode:** `backtest_only`. **Live trading:** desligado por hook + doutrina.

---

## Hipótese

{{Afirmação falsificável sobre o mercado. Não "esta estratégia dá lucro"; sim "em regime X, o sinal Y tem edge estatístico contra baseline Z". Especificar a condição sob a qual a hipótese é refutada.}}

Esta SPEC **não promete retorno**. A promessa é hipótese clara, contrato de execução auditável e refutabilidade.

## Mercado

- **Famílias de ativos:** {{BTC/ETH/SOL/...}}.
- **Tipo:** {{spot | perpétuo linear | futuros}}.
- **Venue para dataset (não para execução):** {{Binance Vision (klines) | outro}}. Venue de execução é `N/A` — live trading está fora do escopo estrutural deste repositório.

## Timeframe

- **Granularidade:** {{1h | 4h | 1d | ...}}.
- **Janela mínima de histórico:** {{barras necessárias pra sair do warm-up}}.
- **Dataset mínimo para caracterização significativa:** {{ex: ≥ 60 dias}}.

## Entradas

Dado `window = prices[:t+1]` e parâmetros `{{param1}}`, `{{param2}}`:

- **Condição de entrada em `t`:** {{expressão causal, exemplo: `high[t-1] > max(high[t-N-1:t-1])`}}.
- {{Regras de tratamento de empate, posição existente, direção long/short.}}
- Engine executa em `t+1 open` (ADR-0002).

## Saídas

### Sinal de saída (parte da estratégia)

- **Condição:** {{expressão causal}}.
- {{Tratamento de empate, posição existente.}}

### Stops

- **Stop-loss:** {{parâmetro + justificativa | `N/A` — razão}}.
- **Take-profit:** {{parâmetro + justificativa | `N/A` — razão}}.
- **Trailing:** {{descrição | `N/A` — razão}}.

## Sizing

- **Fração por trade:** {{fração fixa, ex: 10% do capital via `fixed_fractional_position_sizing` (ADR-0004)}}.
- **Alavancagem máxima:** {{x ≤ 10}}.
- **Regras de agregação multi-asset:** {{descrição | `N/A` — single-asset piloto}}.

## Fees

- **Maker em bps:** {{valor | `N/A` — piloto só considera taker}}.
- **Taker em bps:** {{valor, default ADR-0006 = configurável via `CostModel.taker_fee_bps`}}.

## Slippage

- **Modelo:** linear em notional/capital_inicial (ADR-0006). Parâmetro `slippage_bps_per_unit_notional`.
- **Valor:** {{bps}}. Justificativa: {{por que este valor é conservador/realista}}.

## Spread

- **Modelo:** aditivo em bps (ADR-0019). Parâmetro `CostModel.spread_bps`.
- **Valor:** {{bps | 0.0 se não aplicável}}.

## Funding

- **Se perpétuos:** {{como entra ou `deferred — ADR futura`}}.
- **Se spot:** `N/A`.

## Condições inválidas

Quando a estratégia NÃO deve ser executada:

- {{warm-up, gap declarado, feriado, volatilidade extrema, etc.}}

## Limitações conhecidas

- **Direção:** {{long-only | long+short opt-in}}.
- **Multi-asset:** {{sim/não, e por quê}}.
- **Sample size mínimo:** {{trades}}.
- **Regime-dependency:** {{assumido ou caracterizado}}.
- **{{outras limitações}}**

## Critério de refutação

Falsifica a hipótese se, sobre {{dataset real + janela}}:

- {{ex: expectancy líquida (após fees+slippage+spread) ≤ 0 com fees/slip/spread razoáveis}};
- {{ex: max_drawdown > X em todas as configurações de parâmetros sensatas}};
- {{ex: hit_rate abaixo do esperado via monte_carlo_trades}}.
