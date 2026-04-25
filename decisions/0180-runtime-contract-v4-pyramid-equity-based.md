# 0180 — runtime_contract v4 `pyramid_equity_based` (derroga ADR-0030 invariante #3)

**Status:** Proposed
**Date:** 2026-04-20
**Deciders:** Usuário (direção) + agente
**Relates to:** ADR-0030 (runtime-faithful), ADR-0022 (regime filter), ADR-0031 (manifest v3), ADR-0063 (SizingMode)
**Supersedes:** nenhuma ADR substituída; coexiste com `runtime_contract: "faithful"` como segunda opção v4+.

## Contexto

ADR-0030 fixou 5 invariantes runtime para handoff AF↔BotBinance (entry/exit market @ open next bar, sizing fixed_notional_literal, stop_loss disabled, exit_wins_on_tie). Essa rigidez foi resposta direta ao handoff 2026-04-18 onde 4 reinterpretações inflaram Sharpe +6/+8.

Pesquisa 2026-04-20 tarde (Série TF + BB+width) refutou 4 frentes cheap consecutivas em regimes de alta volatilidade (Padrão 47, autopilot pausa, ADR-0179). Usuário pediu nova direção: **estratégias de consolidação / mercado fraco / baixa vol**, com sizing de **20% do equity por entrada, até 5 entradas (pyramid), rearm de 1h após exit, alavancagem até 5x**.

Essa configuração viola ADR-0030 invariante #3 (sizing fixed_notional_literal) e a semântica implícita de 1 posição aberta por vez. Aceitar o pedido exige **novo runtime_contract** que o manifest v4 declara explicitamente, e que BotBinance precisa implementar separadamente antes do handoff.

Alternativas descartadas:
- (A) research-only sem handoff → não atende o objetivo "estratégia para o bot".
- (C) consolidação com `fixed_notional` 1 posição → preserva ADR-0030 mas sacrifica tese específica (5 tranches é central à hipótese de mean reversion escalar dentro do range).

## Decisão

Abrir `runtime_contract: "pyramid_equity_based"` como segundo valor aceito em manifest **v4** (manifest v3 permanece restrito a `"faithful"`).

### Nove invariantes do runtime v4 pyramid_equity_based

Qualquer runtime (AF engine ou BotBinance) consumindo manifest com esse contrato deve honrar todos:

| # | Invariante | Valor literal |
|---|---|---|
| 1 | `entry_fill` | `market_at_open_next_bar` |
| 2 | `exit_fill` | `market_at_open_next_bar` |
| 3 | `sizing` | `pyramid_equity_fraction` |
| 4 | `stop_loss` | `disabled` |
| 5 | `signal_arbitration` | `exit_wins_on_tie` |
| 6 | `tranche_rule` | `add_on_signal_same_side_while_filter_active` |
| 7 | `exit_rule` | `regime_flip_closes_all_tranches` |
| 8 | `rearm_policy` | `cooldown_bars_after_full_exit` |
| 9 | `max_tranches_per_position` | integer ∈ [1, 10] |
| 10 | `requires_regime_filter` | `true` (adicionado 2026-04-21 via ADR-0185 amendment) |

**Interpretação (literal, sem reinterpretação):**

- **#3 pyramid_equity_fraction:** cada tranche *k* abre com `notional = tranche_equity_frac × equity_at_entry_k × alavancagem`. `equity_at_entry_k` = capital_inicial + realized_pnl_até_agora + unrealized_pnl_das_tranches_abertas. Literal: não use kelly, não use %-risk, não use volatilidade.
- **#6 tranche_rule:** enquanto `regime_filter.is_active() = True` e `|stack| < max_tranches`, cada novo sinal `ENTER_*` da strategy (mesma direção da posição existente) **abre uma tranche adicional**. Sinal em direção oposta com posição aberta → rejeitado (no-op) — reverse-on-signal do ADR-0012 **não se aplica em pyramid mode**.
- **#7 exit_rule:** filtro virar inativo (`is_active() = False`) força `EXIT` que **fecha todas as tranches simultaneamente** ao open[t+1]. Um fill de exit agregado por tranche. N trades registrados (um por tranche, não um por posição).
- **#8 rearm_policy:** após exit total (stack vazio), engine bloqueia novos `ENTER` por `rearm_cooldown_bars` barras LTF. Sinais nesse intervalo são coercivos a HOLD. Zero cooldown = rearm imediato.
- **#9 max_tranches_per_position:** hard cap; default 5 para esta pesquisa, mas manifest carrega o literal — runtime consome, não assume.
- **#10 requires_regime_filter** (amendment 2026-04-21 via ADR-0185): v4 pyramid só é viável com regime filter explícito anexado. Motivo: engines two-sided de mean-reversion (RSI/Bollinger long_only=false) **não emitem `Signal.EXIT`** — em fixed_notional contam com reverse-on-opposite-signal (ADR-0012) para exit, mas pyramid invariante #6 bloqueia reverse. Sem filter + sem EXIT emitter = stack abre tranches até max e nunca fecha. Schema manifest_v4 deve rejeitar `regime_filter == null` para combos com `runtime_contract=pyramid_equity_based`.

### Manifest v4 schema (aditivo sobre v3)

- `manifest_version` aceita `"v4"` (além de `"v3"` legacy).
- `runtime_contract` aceita `"faithful"` (v3 default) OU `"pyramid_equity_based"` (v4+).
- `runtime_invariants` em v4-pyramid é **objeto com 9 chaves literais** (tabela acima).
- `execution_hints` em v4-pyramid substitui `notional_per_trade_quote_ccy` por:
  - `tranche_equity_fraction: float ∈ (0, 1]`
  - `max_tranches: int ∈ [1, 10]`
  - `rearm_cooldown_bars: int ≥ 0`
  - `leverage: float ∈ [1, 10]`
- `disallow_sizing_modes`: manter enum `["kelly_like", "martingale"]`. **Remover `"snowball"` da blacklist** para v4-pyramid (pyramid é snowball-like por construção).

Schema canônico: novo arquivo `exports/approved/manifest_v4.schema.json`. Validator `alpha_forge.exports.validate_manifest` roteia por `manifest_version`.

### Approval gate em v4-pyramid

Mantém Padrão 41 (Sh≥1.5 + trades≥30 cross-era ≥2/3) **mas reinterpreta "trades"**: em pyramid cada tranche gera um trade, então 30 trades pode corresponder a apenas 6 sequências de 5 tranches. **Novo gate específico:** ≥15 sequências de entrada distintas cross-window (não só ≥30 trades). Evita aprovar estratégia que só rodou 3 vezes mas cada vez gerou 10 tranches.

## Handoff a BotBinance

BotBinance deve implementar runtime v4 pyramid **antes** de aceitar manifest com `runtime_contract: "pyramid_equity_based"`. Até lá:
- Manifests v4-pyramid ficam em `exports/approved/` mas com `pending_runtime_impl: true` (campo opt-in).
- AF pode iterar pesquisa offline sem bloqueio.
- Bridge post separado notifica bot do novo contrato para priorizar dev.

## Consequências

### Positivas
- Abre espaço de pesquisa em consolidação/baixa vol, ortogonal às 4 frentes cheap refutadas hoje.
- Permite testar hipótese "scale-in durante range, exit no breakout" que é padrão conhecido em mean reversion.
- Preserva ADR-0030 faithful como contrato válido em paralelo — manifests v3 existentes (13 combos) não são afetados.

### Negativas
- Aumenta superfície de reinterpretação runtime (9 invariantes em vez de 5). Cada uma é um novo vetor de divergência AF↔bot.
- Backtests pyramid **não são comparáveis** com backtests v3 do mesmo engine — PnL/Sharpe de manifests v4-pyramid precisam ser lidos contra o próprio contrato.
- Bot binance ganha dívida de dev antes de qualquer handoff nessa frente.

### Riscos de reinterpretação (antecipar agora)
- **Equity base do cálculo da tranche:** é mark-to-market no momento ou realized-only? Fixo aqui em **realized + unrealized mark-to-market** (ver #3). Runtime que usar realized-only produz sizing diferente.
- **Ordem das tranches no exit:** fechar FIFO ou LIFO importa pra taxes/reporting mas não pra PnL (todas fecham no mesmo open[t+1]). Fixar **FIFO** para reporting consistente.
- **Cooldown mid-stack:** rearm_cooldown só conta após **exit total**, não entre tranches. Tranche 1→2→3 sem cooldown, exit→cooldown→nova tranche 1.

## Próximos passos

1. Implementar engine pyramid mode no AF (ADR-0181 pré-reg cobre Fase 1 probe).
2. Criar `manifest_v4.schema.json` + ajustar `validate_manifest`.
3. Bridge post para bot com este ADR + schema preview.
4. AF roda probe consolidação (ADR-0181). Se edge confirmado cross-era, promove a combo v4.
5. Bot implementa runtime v4. Handoff segue após ambos lados prontos.

## Não-alvo

- Não quebrar ADR-0030 faithful. Ele continua válido e é o default para todo manifest v3.
- Não permitir pyramid em engines onde não faz sentido (mean reversion paired com regime filter é o único caso previsto). Strategies sem `max_*_bps` filter **não devem** usar v4-pyramid — validator pode avisar.
- Não exportar manifests v4-pyramid até bot implementar runtime (flag `pending_runtime_impl: true` bloqueia activation).
