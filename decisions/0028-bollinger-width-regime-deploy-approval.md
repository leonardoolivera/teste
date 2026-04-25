# 0028 — Aprovação de deploy: Bollinger 30/1.5 long-only + BollingerWidthFilter(250) (Série AZ)

**Status:** Accepted
**Date:** 2026-04-18
**Deciders:** Usuário (owner do projeto) + agente.

## Context

A Série AK (N=105, ADR-0026 + ADR-0022) fechou com a família `BollingerWidthFilter` validada como terceira família ortogonal de filtro de regime (complementar a ATR e SMA slope). A Série AZ, subsequente, varreu o espaço `strategy_window × filter_threshold × asset × janela` com `bollinger long-only + bw:250` e identificou que **janela 30 (em vez da janela canônica 20) Pareto-domina o baseline cross-year** em ETH/BTC e recupera parcialmente SOL 2024 (MDD 15.69% → 9.35%).

Dos 14 pilotos w=30+bw:250 rodados, **todos 14 passam ADR-0025 formal** (hit≥45%, mdd≤35%, ratio≥0.95) e **4 passam a régua estrita** (p5 MC ≥ 10000, ratio_min ≥ 0.95, mdd p95 ≤ 10%, fee≡spread):

- AZ.1 — `bollinger-30-15-eth-1h-2024h1-regime-bw-250`
- AZ.2 — `bollinger-30-15-btc-1h-2024h2-regime-bw-250`
- AZ.3 — `bollinger-30-15-btc-1h-2025h1-regime-bw-250`
- AZ.4 — `bollinger-30-15-sol-1h-2024h2-regime-bw-250`

O usuário pediu avaliação contra os 5 gates do `AGENTS.md` §8 (Export contract). Conferência dos gates produziu:

| Gate | AZ.1 | AZ.2 | AZ.3 | AZ.4 |
|---|---|---|---|---|
| Trades OOS ≥ 30 | 38 ✅ | 30 ✅ | **23** ❌ | 69 ✅ |
| Sharpe OOS ≥ 1.0 (anualizado, barra-a-barra) | 1.83 ✅ | 1.56 ✅ | 1.89 ✅ | 2.40 ✅ |
| MDD OOS ≤ 20% | 1.82% ✅ | 1.90% ✅ | 1.38% ✅ | 3.37% ✅ |
| PnL OOS > 0 | +4.68% ✅ | +2.24% ✅ | +3.29% ✅ | +8.01% ✅ |
| Lookahead guard | ✅ | ✅ | ✅ | ✅ |
| Custo baseline ≥ 0.20% round-trip | ⚠️ | ⚠️ | ⚠️ | ⚠️ |

O custo baseline do cost model atual é `taker_fee_bps=5.0, slippage_bps_per_unit_notional=2.0, spread_bps=0.0` → **0.14% round-trip**, abaixo do mínimo formal de 0.20%. O cenário de stress `fee+10` (taker_fee_bps=15.0) atinge **0.34% round-trip**, e os 4 pilotos mantêm `ratio_min ≥ 0.95` sob esse stress (fee≡spread via ADR-0019). Decisão de aprovação leva isso em conta explicitamente.

## Decision

Aprovar os **3 pilotos** AZ.1, AZ.2, AZ.4 para export em `exports/approved/` e handoff ao BotBinance. **AZ.3 fica excluído** da aprovação por violar o gate de trades mínimos (23 < 30). Os 3 aprovados compartilham a mesma configuração de engine:

- **Strategy:** `bollinger` com `window=30, num_std=1.5, long_only=True`
- **Regime filter:** `bollinger_width:window=30,num_std=1.5,min_width_bps=250`
- **Timeframe:** 1h

**Aceitação consciente do gate #3 (custo):** aprovação é feita mesmo com custo baseline em 0.14% (abaixo de 0.20%). Racional: os 3 pilotos passam o cenário de stress `fee+10` (0.34% round-trip) com `ratio_min ≥ 0.95`, demonstrando que a estratégia sobrevive a custos 2.4× acima do gate formal. O baseline do cost model está abaixo do mínimo do AGENTS.md, mas o stress validado excede com folga. Registrado aqui como divergência deliberada do AGENTS.md §8 gate #3, não como esquecimento.

### Manifest a ser emitido

`exports/approved/bollinger_width_regime_20260418.json` conforme schema do AGENTS.md §8. Um único manifest contendo os 3 `approved_combos`:

```json
{
  "strategy_name": "bollinger_width_regime",
  "approved_at": "2026-04-18T00:00:00Z",
  "engine": {
    "family": "bollinger",
    "params": {
      "window": 30,
      "num_std": 1.5,
      "long_only": true,
      "regime_filter": {
        "type": "bollinger_width",
        "window": 30,
        "num_std": 1.5,
        "min_width_bps": 250
      }
    }
  },
  "approved_combos": [
    {"symbol": "ETHUSDT", "timeframe": "1h", "window": "2024-H1"},
    {"symbol": "BTCUSDT", "timeframe": "1h", "window": "2024-H2"},
    {"symbol": "SOLUSDT", "timeframe": "1h", "window": "2024-H2"}
  ]
}
```

### Escopo explícito da aprovação

Aprovado **apenas** para as janelas históricas listadas em `approved_combos`. Expandir para outras janelas (ex: SOL 2025-H2, que foi excluído pelo MDD de 12.80%) requer nova validação e nova ADR. BotBinance pode executar em paper ou live sobre os 3 combos aprovados; qualquer extensão volta pelo gate de aprovação.

## Consequences

- **Positive:** primeiro handoff formal Alpha Forge → BotBinance; fecha o ciclo completo do protocolo (pesquisa → validação → aprovação → export). Estabelece precedente para as próximas séries (BA+) seguirem o mesmo caminho. Valida empíricamente que `BollingerWidthFilter` (terceira família de filtro) produz candidatos deploy-grade.
- **Negative:** divergência explícita do gate #3 do AGENTS.md (custo baseline). Futuras séries devem rodar com cost model baseline ≥ 0.20% desde o início para evitar este descompasso. Escopo restrito por janela-ano significa que o manifest precisa ser re-emitido quando novas janelas forem validadas.
- **Neutral:** Manifest único cobrindo 3 combos, não 3 manifests separados — consistente com schema do AGENTS.md §8 (`approved_combos` é array). SOL 2025-H2 exclusão documentada em BACKTEST de AZ.4 e aqui.

### Fica explicitamente fora desta ADR

1. **AZ.3** (BTC 2025-H1) — 23 trades < 30. Re-validar com janela maior (ex: 2025-H1+H2 combinados) se quiser incluir.
2. **SOL 2025-H2** — MDD 12.80% na janela, excluído do `approved_combos`.
3. **Ajuste do cost model baseline** para 0.20% round-trip — deixado como follow-up de protocolo, não bloqueia este deploy.
4. **Canary live vs paper** — decisão do BotBinance, não do Alpha Forge. O manifest é o contrato; BotBinance decide execução.
5. **Promoção de outros pilotos w=30+bw:250** além dos 3 aprovados — requer nova ADR se desejado.

## Alternatives considered

- **Aprovar os 4 pilotos AZ incluindo AZ.3** — rejeitado: AZ.3 viola gate de trades mínimos do AGENTS.md (23 < 30), gate que existe para reduzir ruído amostral. Aprovar seria abrir exceção em 2 gates (trades + custo), excessivo.
- **Rejeitar aprovação e re-rodar com baseline 0.20%** — rejeitado: usuário optou explicitamente pela rota (A) — aceitar o custo atual com ressalva registrada — ciente de que o stress `fee+10` (0.34%) passa com folga nos 3 aprovados.
- **Emitir 3 manifests separados (um por combo)** — rejeitado: schema do AGENTS.md §8 usa `approved_combos` como array; manifest único é a leitura canônica do schema.
- **Aprovar a família inteira (todos 14 pilotos w=30+bw:250 que passam ADR-0025)** — rejeitado: aprovação deve refletir o que passou a régua estrita, não apenas o mínimo formal. 10 dos 14 ficam fora por não atingirem p5 ≥ 10000 ou mdd p95 ≤ 10%.
- **Incluir AZ.3 como "pendente de mais dados"** — rejeitado: manifest é binário (aprovado ou não). Meio-termos vivem em STATE.md, não em `exports/approved/`.

## Follow-ups

Concrete actions this decision creates. Each one belongs in `STATE.md` as pending work.

- Criar diretório `exports/approved/` (não existe ainda).
- Emitir `exports/approved/bollinger_width_regime_20260418.json` conforme schema do AGENTS.md §8.
- Atualizar `STATE.md` marcando AZ.1/AZ.2/AZ.4 como aprovados para handoff e AZ.3 como excluído.
- Notificar usuário de que o manifest está pronto (passo explícito do AGENTS.md §8 "After exporting").
- Aguardar resposta do BotBinance (re-validação local). Se falhar, investigar divergência de cost/risk — **não** relaxar critérios aqui para forçar aprovação.
- **Follow-up de protocolo (não bloqueia este deploy):** ajustar cost model baseline para ≥ 0.20% round-trip nas próximas séries (BA+) para alinhar com AGENTS.md §8 gate #3 sem exceção.
- **Explicitamente fora:** re-validação de AZ.3 com janela expandida; re-aprovação de SOL 2025-H2; aprovação de outros w=30+bw:250 fora dos 3 combos.
