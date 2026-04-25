# ADR-0065 — Promoção manifest v4: RSI short + regime filter width 300

- **Data:** 2026-04-19
- **Status:** Aceita — pendente audit (ADR-0066) + closeout (ADR-0067) antes de ativar
- **Relacionadas:** ADR-0027 (RSI estratégia), ADR-0030 (runtime-faithful), ADR-0031 (schema v3), ADR-0058 (manifest v3 CG — espelho desta), ADR-0062 (CH closeout — origem dos 4 combos), ADR-0064 (snowball closeout — confirma fixed_notional)

## Contexto

Série CH (RSI(14/30/70) short + regime filter bollinger_width(30,1.5,300), 9 pilotos, ADR-0061/0062) resultou em **PASS 4/4 gates** e **4/9 combos** aprovados: CH.4, CH.6, CH.7, CH.9. Isso generaliza o padrão 10 (ADR-0057) de Bollinger para RSI — duas famílias mean-reversion diferentes validam o mesmo filtro composicional regime-aware. Padrão 11 (ADR-0062): famílias diferentes geram combos complementares, não redundantes.

ADR-0064 confirma: sizing snowball não agrega valor material aqui (delta +$1.36 em 4 combos CH), então manifest v4 segue **fixed_notional_literal** ADR-0030.

ADR-0062 havia proposto como ADRs 0063/0064/0065 (pré-register + audit + closeout). ADR-0063/0064 foram consumidos pelo track snowball; ADR-0066 pelo schema adenda. Renumeração final: **0065 (promoção) + 0067 (audit pré-register) + 0068 (audit closeout/activate)**.

## Decisão

Emitir manifest v4 `exports/approved/rsi_short_width_20260419.json` em schema v3 (ADR-0031), separado e complementar aos manifests v1 (bollinger long), v2 (bollinger long width 250) e v3 (bollinger short width 300). Ativação condicional ao audit PASS.

### Parâmetros do engine

```json
{
  "family": "rsi",
  "params": {
    "period": 14,
    "oversold": 30,
    "overbought": 70,
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

### Combos aprovados (4)

| Tag | Asset | Window | Sharpe | MDD% | Trades | cost_r | MC p5 |
|---|---|---|---:|---:|---:|---:|---:|
| CH.4 | BTC | 2025-H1 | 1.69 | 1.67 | 37 | 0.9781 | 9913 |
| CH.6 | SOL | 2025-H1 | 1.32 | 5.74 | 94 | 0.9555 | 9558 |
| CH.7 | BTC | 2025-H2 | 2.63 | 1.39 | 49 | 0.9791 | 10030 |
| CH.9 | SOL | 2025-H2 | 1.92 | 4.57 | 80 | 0.9620 | 9777 |

### Pontos de destaque

- **CH.7 é a joia:** BTC 2025-H2 Sh=2.63 é o maior Sharpe BTC short de todo o projeto. CG.7 (Bollinger) falhou neste piloto (Sh=0.77). Complementaridade empírica confirmada (Padrão 11).
- **MC p5:** CH.7 é o único combo de CH com MC p5 > 10000 (10030). CH.4/6/9 têm MC p5 ∈ [9558, 9913] — folgados acima de 9500 gate.
- **cost_r folgado:** min 0.9555 em CH.6 (gate é 0.95). CH.4 e CH.7 ambos > 0.978.
- **Zero overlap com v3 Bollinger:** combos CG v3 estão em (SOL 2024-H2, BTC/ETH/SOL 2025-H1); CH v4 está em (BTC/SOL 2025-H1, BTC/SOL 2025-H2). Overlap só em 2025-H1 mas ativos diferentes (CG tem ETH, CH tem BTC em 2025-H1).

### Combos excluídos (5)

Todos com razões quantitativas documentadas no manifest `expansion_policy.excluded_combos`:
- CH.1 BTC 2024-H2 (Sh=−0.76, bull hostil)
- CH.2 ETH 2024-H2 (Sh=−1.52, dupla falha)
- CH.3 SOL 2024-H2 (Sh=−0.39 + cost_r degradado vs CE)
- CH.5 ETH 2025-H1 (Sh=0.50, borderline baixo)
- CH.8 ETH 2025-H2 (Sh=0.81 + MC p5 9376 < 9500)

### Sizing

`execution_hints.position_sizing = "fixed_notional_per_trade"`, `notional_per_trade_quote_ccy = 2000`. Alavancagem 2× embutida no notional. `disallow_sizing_modes: ["snowball", "kelly_like", "martingale"]` com razão herdada de ADR-0028/0029 + reforçada empiricamente por ADR-0064.

### Runtime invariants (ADR-0030)

Cinco literais obrigatórios: `entry_fill: market_at_open_next_bar`, `exit_fill: market_at_open_next_bar`, `sizing: fixed_notional_literal`, `stop_loss: disabled`, `signal_arbitration: exit_wins_on_tie`.

## Audit pré-registrado (ADR-0067)

Espelho de ADR-0059 (audit v3 CG). Três gates pré-registrados:

- **Gate A — Seed stability:** re-rodar CH.4, CH.6, CH.7, CH.9 com seeds {42, 1337, 2024} em MC. Critério PASS: manifest gate continua PASS nos 3 seeds × 4 combos = 12/12 runs.
- **Gate B — Filter load-bearing:** re-rodar CH.4, CH.6, CH.7, CH.9 sem `--regime-filter` (RSI puro sem width 300). Critério PASS: ≥3/4 combos mostrando manifest gate FAIL sem filter (confirma que filter é load-bearing, não cosmético). Se 4/4 ainda passarem, o manifest é refutado (filter não é necessário — scope creep).
- **Gate C — Exclusion confirmation:** re-rodar os 2 piores combos excluídos (CH.1 BTC 2024-H2 e CH.5 ETH 2025-H1) para confirmar que continuam FAIL no engine atual. Se algum virar PASS, a exclusão vira incorreta e escopo do manifest precisa expandir.

Audit total: 4×2 + 4 + 2 = 14 runs (seed 42 já arquivado; reusa). ≈25 min.

## Consequências

### Imediatas
- Manifest emitido em `exports/approved/rsi_short_width_20260419.json` com `live_status: "pending_audit"`.
- ADR-0067 abre audit pré-registrado (14 runs).
- Script `tools/run_manifest_v4_audit.py` + `summarize_manifest_v4_audit.py` espelhos dos scripts v3.
- Bot BotBinance **não notificado** até audit PASS (espelho 0059/0060).

### Bot (após ADR-0067 activate)
- Bridge: postar notificação "manifest v4 RSI short ativo, paralelo a v1/v2/v3" com link pro JSON.
- Bot re-valida localmente com seu runtime-faithful adapter (já implementado após ADR-0030 local do bot, 2026-04-18).

### Regras
- Manifests v3 (Bollinger) + v4 (RSI) são **complementares, não substitutos**. Nenhum supersede o outro.
- ADR-0030 + ADR-0031 aplicam integralmente.
- Proibição snowball (ADR-0028/0029) mantida neste manifest com razão dupla: herança + evidência empírica ADR-0064.

## Critério de sucesso desta ADR

1. Manifest JSON valida contra `exports/approved/manifest.schema.json` ✓
2. `alpha_forge_commit` corresponde ao HEAD atual ✓
3. 4 combos referenciam runs arquivados em `results/validation/ch-rsi-14-30-70-*/` ✓
4. ADR-0067 audit pré-registrado em seguida ✓
5. ADR-0068 closeout + bridge após audit PASS
