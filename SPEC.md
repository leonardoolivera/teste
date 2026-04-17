# SPEC.md — Donchian breakout (long-only)

> **Piloto agentic ativo.** Produzido pelo `strategy-researcher` a partir de [ADR-0011](./decisions/0011-donchian-breakout-strategy.md).
> **Release mode:** `backtest_only`. **Live trading:** desligado por hook + doutrina.

---

## Hipótese

Em mercado cripto de timeframe médio (spot/perp 1h, 4h, 1d), o rompimento da máxima das últimas `N` barras exibe edge estatístico positivo **versus** baseline HOLD passivo, condicional ao mercado estar em regime de tendência ou expansão de volatilidade. A hipótese é **falsificável**: se sobre dataset real BTCUSDT 180d, ETHUSDT 180d e pelo menos um regime de range, a estratégia não supera HOLD em expectancy após fees+slippage em nenhuma configuração razoável de `(entry_window, exit_window)`, a hipótese é refutada nesse recorte.

Esta SPEC **não promete retorno**. A promessa é de hipótese clara, contrato de execução auditável e refutabilidade.

## Mercado

- **Famílias de ativos:** cripto líquida (BTC, ETH, SOL, majors).
- **Tipo:** spot **e** perpétuo linear (mesma regra; funding tratado explicitamente quando perp).
- **Venue para dataset (não para execução):** Binance Vision (klines mensais públicos). Venue de execução é `N/A` — live trading está fora do escopo estrutural deste repositório.

## Timeframe

- **Granularidade:** 1h (piloto inicial). Arquitetura agnóstica a timeframe; 4h e 1d são follow-ups naturais.
- **Janela mínima de histórico:** `max(entry_window, exit_window) + 2` barras para sair do warm-up. Para o default 20/10, são 22 barras — na prática ~1 dia de 1h. Caracterização significativa exige ≥ 60 dias.

## Entradas

Dado `window = prices[:t+1]` e parâmetros `entry_window`, `exit_window`:

- **Condição de entrada long em `t`:** `high[t-1] > max(high[t-entry_window-1 : t-1])`.
- Comparação estritamente `>`. Empate exato **não** é sinal.
- Sem posição → emite `ENTER_LONG`; engine executa em `t+1 open`.
- Com posição long aberta → engine reduz sinal redundante a no-op (comportamento já existente).

## Saídas

### Sinal de saída (parte da estratégia)

- **Condição:** `low[t-1] < min(low[t-exit_window-1 : t-1])`.
- Comparação estritamente `<`. Empate exato **não** é saída.
- Com posição long aberta → `EXIT`; engine fecha em `t+1 open`.
- Sem posição → engine reduz a no-op.

### Ordem de avaliação

Saída antes de entrada. Se `t-1` rompe high_max **e** low_min simultaneamente, a estratégia emite `EXIT`. Justificativa: saída antes é a arbitragem mais conservadora e legível (ADR-0011 §"Separação estratégia × engine").

## Stops / Takes / Trailing

- **Stop-loss:** `N/A`. Única saída é o rompimento da baixa do exit_window. Motivo: stops interagem de forma não-trivial com sizing e cost model; empurrar para ADR dedicada.
- **Take profit:** `N/A`. Mesmo motivo.
- **Trailing:** `N/A`. O próprio Donchian exit já é um tipo de trailing discreto sobre mínimas.

## Sizing

- **Modelo:** fixed fractional (`fixed_fractional_position_sizing`, [risk/sizing.py](./src/alpha_forge/risk/sizing.py)).
- **Fração por trade (default piloto):** `0.1` (10% do capital corrente por trade).
- **Alavancagem máxima (hard cap):** `2.0x` no piloto. Hard cap estrutural do projeto continua `10x` (ADR-0004) — piloto é conservador dentro do cap.
- **Sem martingale. Sem averaging down. Sem grid.** Um trade por vez; tamanho fixo da fração do capital corrente.
- **Rejeição determinística:** sizing inválido (zero/negativo/NaN/inf/acima do cap) nunca vira trade; `Rejection` registrada com motivo categorizado.

## Fees

- **Modelo:** taker fee linear por fill, em basis points sobre `notional`.
- **Default piloto:** `taker_fee_bps = 5.0` (0.05%). Caracterização também varre `{0, 5, 10, 20}`.
- **Maker:** `N/A` no piloto. Todas as ordens tratadas como taker (mais conservador).
- **Aplicação:** custo ajusta o **preço de execução** contra o trader (entrada long paga mais caro, saída long recebe mais barato), nunca o PnL diretamente. Implementado em [backtest/cost.py](./src/alpha_forge/backtest/cost.py) — ADR-0006.

## Slippage

- **Modelo:** linear em basis points por unidade de `notional / capital_inicial`. Justificativa: aproximação conservadora do impacto-de-mercado; cresce com o tamanho relativo do trade.
- **Default piloto:** `slippage_bps_per_unit_notional = 2.0`.
- **Grid de sensibilidade:** `{0, 2, 5, 10}` bps.
- **Aplicação:** idem fees — ajusta preço contra o trader.

## Funding

- **Piloto:** `N/A`. Dataset inicial é spot BTCUSDT. Quando perp entrar, funding será adicionado como custo periódico aplicado sobre posição aberta em snapshots de 8h (Binance padrão).
- **Registro:** follow-up explícito — abrir ADR antes de tocar funding no engine.

## Condições inválidas (não executar)

A estratégia emite **`HOLD`** (não executa, não sinaliza) quando:

1. `len(window) < max(entry_window, exit_window) + 2` — **warm-up**.
2. Dataset com gap não declarado → `load_dataset` rejeita antes de chegar à estratégia (ADR-0005).
3. Sizing inválido → engine rejeita e grava `Rejection` (ADR-0004).

Condições que **não** são tratadas nesta fase (ficam explicitamente fora):

- Volatilidade extrema / pânico / euforia → exigiria `regimes/`, fora de escopo.
- Feriados / gaps de liquidez → tratamento operacional, fora de escopo.
- Falha de dados em tempo real → `N/A` no piloto (não há live).

## Limitações conhecidas

1. **Long-only.** Short side fica para ADR dedicada. Implica viés estrutural em regime de baixa prolongada.
2. **Um ativo por invocação.** Multi-asset portfolio-level fica para `ranking/` (deferred).
3. **Sem filtros de regime.** A estratégia entra em qualquer contexto onde a regra dispara; caracterização por regime fica para `regimes/` (deferred).
4. **Parâmetros não otimizados.** Defaults 20/10 vêm da literatura Turtle, **não** foram fitted sobre o dataset BTCUSDT 180d.
5. **Amostra pequena.** BTCUSDT 1h 180d = 4320 barras, ~110 trades no piloto — suficiente para caracterização observacional; **insuficiente** para afirmar edge estatístico com confiança alta.
6. **Sem stops, takes, trailing.** Exposição a drawdown intra-trade é limitada apenas pelo sinal de saída Donchian.
7. **Paper/live inexistentes.** O único estágio executável é `backtest_only`. Promoção para paper exige que o módulo `paper-trade` exista (deferred em `vision/02-scope.md`).

---

## Teste de falsificação mais barato

Rodar `scripts/validate_pilot.py --strategy donchian` sobre BTCUSDT 180d e sintético 720 barras com grid de fees {0,5,10,20} × slippage {0,2,5,10}. Se em **nenhuma** célula do grid o `final_equity` supera o `capital_inicial` em mais de 1% (após custos), a hipótese está refutada neste recorte. Custo do teste: ~30 segundos, nenhuma ordem real, nenhum risco.

## Referências

- ADR-0002 (causalidade) · ADR-0004 (risco) · ADR-0005 (manifesto) · ADR-0006 (custos) · ADR-0007 (métricas) · ADR-0011 (esta família).
