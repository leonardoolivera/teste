# 0029 — Expansão de deploy: ETH 2025-H1 entra em aprovados (manifest v2)

**Status:** Accepted
**Date:** 2026-04-18
**Deciders:** Usuário (owner do projeto) + agente.

## Context

ADR-0028 aprovou 3 combos (ETH 2024-H1, BTC 2024-H2, SOL 2024-H2) em `exports/approved/bollinger_width_regime_20260418.json`. Séries BA–BJ subsequentes varreram perturbações (timeframe 4h, variação `num_std ∈ {1.25, 1.75}`, variação `min_width_bps ∈ {200, 300}`, cross-período 2023-H2, 2025-H1, 2025-H2, composição AND com ATR, família alternativa RSI, e trend-following Donchian como contraprova). Nenhuma variação produziu deploy grade em 2025-H2; ETH/BTC/SOL 2025-H2 com Sharpe OOS 0.19-1.05 confirmam que o regime daquele semestre é genuinamente hostil a mean-reversion (refutado também por BI: Donchian 2025-H2 Sharpe −3.12 a −4.71).

A Série BJ fechou a matriz 3 ativos × 5 semestres com a config aprovada. **ETH 2025-H1** passa todos os 4 gates formais do AGENTS.md §8 Export Contract:

| Gate | Valor | Status |
|---|---|---|
| Trades OOS ≥ 30 | 36 | ✅ |
| Sharpe OOS ≥ 1.0 | 1.21 | ✅ |
| MDD OOS ≤ 20% | 4.37% | ✅ |
| PnL OOS > 0 | +3.71% | ✅ |
| Lookahead guard | assert_causal | ✅ |

Custos: baseline `taker_fee_bps=5.0 + slippage_bps=2.0 + spread_bps=0.0` → 0.14% round-trip (mesma divergência do gate #3 registrada em ADR-0028); stress `fee+10` → 0.34% mantém `ratio_min ≥ 0.95` (bit-identico ao stress `spread+10` via ADR-0019).

BTC 2025-H1 fica **próximo** mas falha gate #4 (trades=23 < 30), mesmo com Sharpe 1.89 — confirma padrão BTC de "ativo lento" que dificilmente entrega 30 trades em um semestre mean-reversion. Não aprovado.

## Decision

Expandir `exports/approved/` com **ETH 2025-H1** como quarto combo aprovado. Emitir **manifest v2** (`bollinger_width_regime_20260418_v2.json`) contendo os 4 combos totais; manifest v1 (`bollinger_width_regime_20260418.json`) fica preservado imutável como registro histórico.

Parâmetros do engine **inalterados** em relação a ADR-0028 (`window=30, num_std=1.5, long_only=True, regime_filter=bollinger_width:window=30:num_std=1.5:min_width_bps=250`). A expansão é exclusivamente de `approved_combos`, não de engine.

### approved_combos no manifest v2

```json
[
  {"symbol": "ETHUSDT", "timeframe": "1h", "window_tag": "2024-H1"},
  {"symbol": "ETHUSDT", "timeframe": "1h", "window_tag": "2025-H1"},
  {"symbol": "BTCUSDT", "timeframe": "1h", "window_tag": "2024-H2"},
  {"symbol": "SOLUSDT", "timeframe": "1h", "window_tag": "2024-H2"}
]
```

### Divergência do gate #3 (custo baseline) — re-registrada

Mesma situação de ADR-0028: baseline 0.14% abaixo do mínimo formal 0.20%, stress `fee+10` 0.34% passa com folga. Aceita explicitamente pelo usuário em ambas ADRs. Follow-up de protocolo (ajustar baseline) segue pendente, **não bloqueia** esta expansão.

### Combos que continuam excluídos

| Combo | Motivo | Origem |
|---|---|---|
| BTC 2025-H1 | Trades 23 < 30 | BJ |
| BTC 2025-H2 | Trades 16 < 30 | BE |
| BTC 2024-H1 | Trades 26 < 30 + Sharpe 0.41 | BJ |
| BTC 2023-H2 | Trades 10 < 30 | BD |
| ETH 2024-H2 | Sharpe 0.72 < 1.0 | BC (controle) |
| ETH 2025-H2 | Sharpe 0.42 < 1.0 | BE |
| ETH 2023-H2 | Trades 17 < 30 | BD |
| SOL 2023-H2 | Sharpe 0.46 < 1.0 | BD |
| SOL 2024-H1 | Sharpe 0.30 < 1.0 | BJ |
| SOL 2025-H1 | Sharpe 0.62 < 1.0 | BJ |
| SOL 2025-H2 | Sharpe 0.19 < 1.0 | BE |

11 combos excluídos por gate formal. Qualquer inclusão futura deles requer nova ADR.

## Consequences

- **Positive:** segundo handoff formal, reforça que o protocolo AGENTS.md §8 é iterável (não é "one-shot"). Manifest v2 adiciona cobertura temporal (2025-H1 além de 2024) sem mudar engine — BotBinance pode expandir execução sem alterar código. Valida que séries de sensibilidade (BA-BJ) produzem mais do que refutações: também descobrem combos aprováveis adicionais.
- **Negative:** matriz final revela que a estratégia **é específica de ativo × período**. Dos 15 combos testados (3 ativos × 5 semestres), só 4 passam — taxa de 27%. Edge existe mas não é universal; expansão para "rodar sempre" não é justificada pelos dados. Operacionalmente: BotBinance precisa saber quando re-avaliar cada combo (end-of-window) e re-submeter ao Alpha Forge para re-aprovação.
- **Neutral:** versioning de manifest (v1, v2, ...) vira padrão. Manifests anteriores preservados imutáveis para auditoria. Quando um combo sai (ex: BotBinance reporta degradação live), emite-se vN+1 removendo-o; não se edita manifest anterior.

### Fica explicitamente fora desta ADR

1. **BTC 2025-H1** — falha gate de trades. Re-avaliação só com janela combinada H1+H2 (2025 inteiro) que requer mudança de CLI (atualmente aceita 1 dataset-id por run).
2. **Qualquer combo 2025-H2** — regime hostil confirmado cross-family. Re-avaliação só quando dados de 2026-H1 estiverem disponíveis.
3. **Ajuste do baseline cost model** — follow-up de protocolo herdado de ADR-0028.
4. **Carteira multi-estratégia** (ex: rodar bollinger + RSI em paralelo cobrindo regimes complementares) — observação das séries BG/BH de que RSI e bollinger capturam regimes diferentes sugere valor, mas requer ADR de composição de portfólio (além do escopo do manifest atual, que é single-engine).
5. **Trend-following em 2025-H2** — BI confirmou Donchian Sharpe −3 a −4.7; refutado. Retomar só com nova família (não Donchian 20/10).

## Alternatives considered

- **Aprovar também BTC 2025-H1** (Sharpe 1.89 mas trades=23) — rejeitado: gate #4 é binário (≥30 não negociável no AGENTS.md §8). Abrir exceção por "quase" inflaciona o protocolo.
- **Aprovar SOL 2025-H1** (Sharpe 0.62, 44 trades) — rejeitado: Sharpe < 1.0, gate #1 claro.
- **Re-emitir v1 apagando o arquivo original** (overwrite) — rejeitado: manifests são imutáveis por auditoria. v2 coexiste com v1; BotBinance usa o mais recente.
- **Esperar acumular 2-3 combos novos antes de emitir vN** — rejeitado: cada combo aprovado por gate deve ir para produção rápido, sem batching. O custo do handoff é baixo (1 JSON).
- **Aprovar com snowball explicitamente permitido** — rejeitado: BotBinance re-validação reportou que snowball quebra mean-reversion (ETH PnL +19% → +0.78% com snowball). Manifest v2 segue `fixed_notional_per_trade`, e agora com campo explícito `disallow_sizing_modes` para evitar reintrodução acidental.

## Follow-ups

Concrete actions this decision creates. Each one belongs in `STATE.md` as pending work.

- Emitir `exports/approved/bollinger_width_regime_20260418_v2.json` com 4 combos e campo novo `disallow_sizing_modes: ["snowball", "kelly_like", "martingale"]`.
- Atualizar `STATE.md` refletindo manifest v2 e matriz 15-combos BJ.
- Notificar BotBinance do v2 (usuário faz handoff manual).
- Aguardar re-validação BotBinance nos 4 combos; se ETH 2025-H1 divergir live, investigar gap (mesmo protocolo aplicado a v1 — indexação close[t-1], timezone, inclusivo/estrito).
- **Explicitamente fora:** edição do v1, composição multi-estratégia, expansão para BTC 2025-H1 ou SOL 2025-H1.
