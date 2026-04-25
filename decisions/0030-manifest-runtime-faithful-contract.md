# 0030 — Contrato runtime-faithful do manifest: 4 invariantes obrigatórios

**Status:** Accepted
**Date:** 2026-04-18
**Deciders:** Usuário (owner do projeto) + agente.

## Context

Primeiro handoff formal via bridge `agents_bridge/` (2026-04-18) expôs que a re-validação do bollinger v2 no BotBinance reportava Sharpe +6 a +8 e PnL +990% (SOL) — números fisicamente improváveis. Investigação em 5 turnos revelou **quatro desvios estruturais** entre o backtest do Alpha Forge (que gerou o manifest) e o BacktestRunner genérico do bot:

1. **Double-strip causal:** bot aplicava `candles[:-1]` em window que já excluía a barra atual (`candles[i-w:i]`), usando closes até `i-2` em vez de `i-1` (lookahead-inverso de 1 barra).
2. **Fill model:** bot usava limit agressivo at `close[t-1]`; AF usa market at `open[t+1]`. Limit introduz **survivor bias** (ordem só fila se `high[t+1] ≥ trigger`, filtrando implicitamente as piores entradas em mean-reversion).
3. **Sizing não-conforme:** bot usava `risk_per_trade=2%` (variável por stop distance) que resultava em notional ~4.4× o `fixed_notional=$2000` especificado no manifest; MDD inflado 10×+.
4. **Stop loss ativo:** bot tinha stop ~2.3% do preço; manifest não declara stop. Em mean-reversion, stop corta a recuperação antes do preço voltar à média — catastrófico (explica PnL flip +3.71% → -70.32% em ETH 2025-H1).

Após fixes (1)(2)(3)(4) no bot, os 4 combos bateram o manifest dentro de envelope esperado (trade count ±20%, PnL ±30%, MDD ±1.5pp). Gap residual de Sharpe explicado por fórmula diferente (bot: per-trade com `sqrt(n_trades)`; AF: bar-a-bar com `sqrt(24*365)` sobre equity_curve OOS concatenada — reconstituída e verificada bit-identica ao manifest).

O episódio mostrou que o manifest v2, apesar de tecnicamente completo no schema de `execution_hints`, **não era o suficiente** para evitar quatro reinterpretações plausíveis mas erradas por um runtime genérico. As 4 propriedades precisam ser invariantes nomeados, não texto em prosa no campo notes.

## Decision

Formalizar o **contrato runtime-faithful** que todo manifest `exports/approved/*.json` assume e todo runtime executor deve respeitar. Quatro invariantes obrigatórios:

1. **Entry fill:** `market @ open[t+1]` após signal ENTER em `t` (nunca limit no trigger, nunca delay extra).
2. **Exit fill:** `market @ open[t+1]` após signal EXIT em `t` (nunca stop, nunca take-profit, nunca limit).
3. **Sizing:** valor literal de `execution_hints.notional_per_trade_quote_ccy` como notional fixo por trade. Qualquer override (risk%, kelly, volatility-based) **invalida** a aprovação.
4. **Stop loss:** `disabled`. Exits são 100% governados pelo `exit_rule` do engine. Stops adicionais alteram a estratégia.

O manifest v2 já enforce o ponto (3) via `disallow_sizing_modes: [snowball, kelly_like, martingale]`. ADR-0030 estende: **todo manifest v3+ deve declarar explicitamente `runtime_contract: "faithful"`** no topo e listar os 4 invariantes como `runtime_invariants: [...]`. Runtime que não suportar os 4 deve se recusar a ativar.

### Texto padrão do campo `runtime_invariants` (v3+)

```json
"runtime_contract": "faithful",
"runtime_invariants": {
  "entry_fill": "market_at_open_next_bar",
  "exit_fill": "market_at_open_next_bar",
  "sizing": "fixed_notional_literal",
  "stop_loss": "disabled",
  "signal_arbitration": "exit_wins_on_tie"
}
```

O quinto item (`exit_wins_on_tie`) já era ADR-0011; entra no contrato explícito pra simetria.

### Aplicação retroativa ao manifest v2

Manifest v2 (`bollinger_width_regime_20260418_v2.json`) fica **imutável** (ADR-0029). A conformidade do v2 com ADR-0030 é implícita por leitura dos `execution_hints` existentes; não se re-emite v3 só pra adicionar os campos novos. V3+ futuros passam a incluí-los explicitamente.

## Consequences

- **Positive:** runtime executors ganham contrato não-ambíguo. Quem lê um manifest v3+ sabe exatamente as 4 propriedades que não pode reinterpretar. Falhas como as descobertas em 2026-04-18 ficam impossíveis sem violação explícita do schema. Pilotos futuros do Alpha Forge permanecem tendo **um** caminho de execução canônico — o do backtest engine do AF. Isso reduz a superfície de divergência sem forçar o runtime a implementar o engine do AF: basta implementar um adapter conforme.
- **Negative:** runtimes genéricos (como o BacktestRunner atual do bot) precisam de um adapter dedicado por strategy family, ou um modo `manifest_faithful` que bypass features nativas (stops, limits, sizing dinâmico). Engines do bot que dependem dessas features não conseguem rodar manifests AF direto.
- **Neutral:** o AF não ganha novas capacidades; apenas codifica o que já fazia. Schema dos manifests v1 e v2 não muda. O campo `runtime_contract` é aditivo pra v3+ e opcional em leitores antigos (missing key = assume faithful).

### Fica explicitamente fora desta ADR

1. **Contrato para stops e take-profits em estratégias que os requerem** (ex: trend-following com trailing stop). Essas vão requerer outro contrato nomeado (ex: `runtime_contract: "trailing_stop"`). ADR-0030 só define o `faithful` porque é o único usado hoje.
2. **JSON-schema formal dos manifests** — ADR-0031.
3. **Validação automática no AF de que manifests emitidos cumprem o contrato** — follow-up; hoje o export é manual.
4. **Adapter do lado do bot** — responsabilidade do BotBinance (ADR-0030 local deles).
5. **Runtime-faithful para outras engines em auditoria** — depende de cada engine suportar os 4 invariantes ou não; decisão por engine, não global.

## Alternatives considered

- **Deixar como prosa em `execution_hints.notes`** — rejeitado: foi isso que já havia no v2 e não evitou 4 reinterpretações erradas. Invariantes nomeados em schema são mais defensáveis.
- **Embutir o engine do AF no bot como lib** — rejeitado: acoplamento forte, bloqueia bot de evoluir independente. Contrato + adapter é o trade-off certo.
- **Manifest declara o caminho de código exato (hashes de arquivos)** — rejeitado: frágil, prende bot à versão do AF em build-time.
- **Deixar "faithful" como default implícito, sem campo novo** — rejeitado: o v3+ é a oportunidade de tornar explícito. Evita outro handoff no futuro com as mesmas dúvidas.
- **Adicionar os 4 invariantes via patch ao v2 (re-emit)** — rejeitado: viola imutabilidade declarada em ADR-0029.

## Follow-ups

Concrete actions this decision creates. Each one belongs in `STATE.md` as pending work.

- Atualizar `AGENTS.md §8` (Export contract) pra documentar `runtime_contract` e `runtime_invariants` como campos obrigatórios em manifests v3+.
- Próximo manifest que emitirmos (v3 de qualquer strategy) será o primeiro a conter os campos novos — serve de referência.
- Usar a oportunidade de adicionar property-based teste: "manifest v3+ deve conter `runtime_contract: faithful` ou rejeitar export".
- Registrar na bridge (`conversa.md`) que ADR-0030 foi aceita; inbox bot já espera isso.
- **Explicitamente fora:** re-emissão do v2, novos contratos além de `faithful`, mudança no engine do AF.
