# 0058 — Manifest v3 promoção: Bollinger short + width_bps=300 (4 combos CG)

**Status:** Accepted — manifest gravado; audit em ADR-0059 antes de marcar ready pro bot
**Date:** 2026-04-19
**Deciders:** Usuário + agente.
**Relates to:** ADR-0026 (Bollinger mean-rev), ADR-0030 (runtime faithful), ADR-0031 (schema v3), ADR-0051 (short side), ADR-0057 (closeout CG PASS).

## Context

ADR-0057 arquivou Série CG com gate PASS em todos os 4 gates pré-registrados. 4/9 combos aprovados: CG.3 (SOL 2024-H2), CG.4 (BTC 2025-H1), CG.5 (ETH 2025-H1), CG.6 (SOL 2025-H1). Primeiro PASS cross-period em 7 séries consecutivas.

Promoção requer ADR própria (ADR-0057 §Consequences imediatas) porque não é reversível casualmente — bot passará a notificar intenção de paper-trade no manifest novo.

## Decisão

Emitir **manifest v3 separado** (não supersede v2) com os 4 combos aprovados e ativar audit antes de notificar bot.

### Schema: separado vs superseding v2

**Escolhido: separado.** Razão: v2 é `long_only=true` (Bollinger long + width 250); v3 é `long_only=false` (Bollinger short + width 300). São produtos direcionais distintos, calibrados pra regimes opostos (bull 2024-H2 long; chop 2025-H1 short). Supersede implicaria substituição, mas v2 continua ativa e válida pro regime long. Manifests são complementares.

**Nomeação:** `bollinger_short_width_20260419.json`, `strategy_name: "bollinger_width_short_regime"` (espelha v2 `bollinger_width_regime` com prefixo direcional).

### Engine params

```json
{
  "family": "bollinger",
  "params": {
    "window": 20,
    "num_std": 1.5,
    "long_only": false,
    "regime_filter": {
      "type": "bollinger_width",
      "window": 30,
      "num_std": 1.5,
      "min_width_bps": 300
    }
  }
}
```

Observações:
- `window=20` (v2 usa 30). Decisão da CE/CF/CG: short mean-rev usa window curta pra capturar reversões mais rápidas. Documentado em ADR-0052 pré-registro.
- `num_std=1.5` igual a v2.
- `long_only=false` habilita short (ADR-0051).
- Filtro igual a v2 exceto `min_width_bps=300` (gate testado em CG, 9/9 lift cost_r vs CF 250).

### Combos aprovados

| Tag | Symbol | Window | OOS trades | OOS Sharpe | OOS MDD% | OOS PnL% | MC p5 | cost_r |
|---|---|---|---:|---:|---:|---:|---:|---:|
| CG.3 | SOLUSDT | 2024-H2 | 102 | 1.38 | 6.33 | 6.64 | 9729 | 0.9505 |
| CG.4 | BTCUSDT | 2025-H1 | 37 | 1.24 | 2.17 | 2.96 | 9953 | 0.9774 |
| CG.5 | ETHUSDT | 2025-H1 | 85 | 2.39 | 8.33 | 12.16 | 9924 | 0.9594 |
| CG.6 | SOLUSDT | 2025-H1 | 109 | 2.71 | 4.92 | 17.47 | 10460 | 0.9512 |

Todos dentro do gate: trades≥30, Sharpe≥1.0, MDD≤20, MC p5>9500, cost_r≥0.95.

### Expansion policy — combos excluídos

Os 5 combos reprovados de CG têm exclusão com razão quantitativa:

- **CG.1** (BTC 2024-H2): Sharpe 0.52 < 1.0 (bull hostil a short puro, coerente com ADR-0049 Padrão 8).
- **CG.2** (ETH 2024-H2): Sharpe −0.23 < 0 + MC p5 9246 < 9500.
- **CG.7** (BTC 2025-H2): Sharpe 0.77 < 1.0 (H2 regime misto).
- **CG.8** (ETH 2025-H2): Sharpe 0.94 < 1.0 + MC p5 9442 < 9500.
- **CG.9** (SOL 2025-H2): Sharpe 0.72 < 1.0 + MC p5 9150 + cost_r 0.9497 (triplo FAIL).

Regra expansion: "**Combos novos require nova ADR + nova série cross-period; mudar `min_width_bps`, `num_std` ou `window` requer bump de schema (v4) e ADR acompanhando**". Não promover cross-regime sem validação separada.

### Runtime invariants (ADR-0030)

Todos os 5 literais preservados. Short usa mesmo contrato faithful do long — fill em open(t), notional fixo, sem stop, exit vence empate.

```json
{
  "runtime_contract": "faithful",
  "runtime_invariants": {
    "entry_fill": "market_at_open_next_bar",
    "exit_fill": "market_at_open_next_bar",
    "sizing": "fixed_notional_literal",
    "stop_loss": "disabled",
    "signal_arbitration": "exit_wins_on_tie"
  }
}
```

### Execution hints — delta vs v2

- `entry_rule_long`: inalterado ("close[t-1] cruza estritamente abaixo de (ma - num_std*sigma)...")
- `entry_rule_short` (novo): "close[t-1] cruza estritamente acima de (ma + num_std*sigma), vindo de dentro ou da borda"
- `exit_rule`: mesmo conceito (cruza ma vindo do lado oposto), agora aplicável a ambas direções
- `regime_gate`: `bollinger_width_bps >= 300` (vs 250 em v2)

### Audit pré-notificação — ADR-0059 proposto

Antes de marcar manifest como `live_status=ready` e notificar bot:

1. **Seed stability**: re-run CG.3/4/5/6 com `mc_seed` ∈ {42, 43, 44}. Sharpe deve ser idêntico (WF determinístico), MC p5 percentiles podem variar mas gate PASS em todos os 3 seeds.
2. **Filter attribution**: re-run CG.3/4/5/6 sem filtro (`--regime-filter none`). Confirma que removendo filtro quebra gate (cost_r cai abaixo de 0.95). Espelha ADR-0048 Audit B.
3. **Exclusion confirmation**: re-run CG.1 + CG.9 (falhas mais severas) com `mc_seed=43`. Confirma que seed não é fonte de falha.

5 runs total (3 seeds × 4 combos aprovados = 12, mas seed 42 já feito → 8 novos + 4 sem filtro + 2 exclusão = **~14 runs**; timebox ~25min).

Gate audit: todos 3 checks passam → manifest v3 `live_status=active`. Se qualquer check falhar, reverter promoção e arquivar em ADR-0060.

### Notificação BotBinance

Após audit PASS em ADR-0059, postar em `inbox_botbinance.md`:
- Caminho do manifest (`exports/approved/bollinger_short_width_20260419.json`)
- Combos aprovados (4)
- Runtime contract (faithful, mesmo que v2)
- Solicitação: bot paper-trada os 4 combos e reporta divergência de premissa (signal-only rule, ADR-0018).

V2 continua ativa em paralelo. Bot deve rodar v2+v3 simultaneamente (engines separadas por `strategy_name`).

## Consequences

### Imediatas
- Manifest v3 gravado em `exports/approved/bollinger_short_width_20260419.json`.
- **`live_status=pending_audit`** no manifest — bot não ativa ainda.
- ADR-0059 pré-registra audit (escopo + critérios) antes de rodar.
- Bot não notificado até audit PASS.

### Longo prazo
- Se audit FAIL, manifest arquivado sem live. ADR-0060 documenta qual check quebrou.
- Se audit PASS, manifest ativa e bot passa a paper-tradar. Timebox paper 14-21d (ADR-0049 padrão).
- Novos pilotos cross-regime (ex: short em 2024-H2 com num_std=2.0) ficam como trabalho futuro — requerem nova ADR.

### Não muda
- V2 (long + width 250) continua ativa.
- Bot continua paper-tradando v2 independentemente.
- Nenhum canary/live; AGENTS.md política "sem pressa pra deploy" honrada.

## Critério de sucesso

1. Manifest v3 gravado com schema correto ✓
2. ADR-0059 pré-registra audit antes de rodar ✓
3. Bot não notificado até audit ✓
4. Expansion_policy quantitativa documenta todos os 5 excluídos ✓

## Fora do escopo

- Audit em si (ADR-0059 pré-registra e executa).
- Notificação bot (pós-audit).
- Variação `min_width_bps` ou `num_std`. Se audit levantar problema, ADR posterior.
- Short em outras famílias (RSI, Donchian). Width semanticamente vinculado a Bollinger.
