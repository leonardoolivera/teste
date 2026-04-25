# 0220 — V2/RAIO Ciclo 6 — BHDrawdownFilter implementado + Padrão 59 (gate vs sample size trade-off)

**Status:** Accepted
**Date:** 2026-04-25
**Deciders:** Agente, autonomamente per RAIO §13
**Relates to:** ADR-0219 (P52 cross-era FAIL Padrão 58), ADR-0022 (regime filter contract), ADR-0023 (CompositeFilter)

## Contexto

ADR-0219 estabeleceu Padrão 58: trend-following long-only crypto é regime-conditional (bull/recovery only); explode em bear absoluto. P52 BTC 18/60 não pode ser exportado standalone. Solução proposta: regime detector que bloqueia execução em bear.

Cycle 6 implementou `BHDrawdownFilter` — primeiro filtro V2 dedicado a regime gating (todos 4 filtros V1 — sma_slope, atr_regime, bollinger_width, trend_htf — eram de natureza diferente).

## Implementation

Arquivo: [`src/alpha_forge/regimes/filter.py`](../src/alpha_forge/regimes/filter.py).

```python
class BHDrawdownFilter:
    name = "bh_drawdown"

    def __init__(self, lookback_bars: int, max_dd_pct: float):
        # validations omitted

    def is_active(self, window: pd.DataFrame) -> bool:
        causal = window.iloc[:-1]
        if len(causal) < self.lookback_bars: return False
        closes = causal["close"].to_numpy()
        recent = closes[-self.lookback_bars:]
        max_recent = recent.max()
        close_now = closes[-1]
        dd_pct = (max_recent - close_now) / max_recent * 100.0
        return dd_pct < self.max_dd_pct
```

CLI spec: `--regime-filter "bh_drawdown:lookback_bars=720:max_dd_pct=25"`. Round-trip serialization implementado. Smoke test passa.

Causal (ADR-0002): usa apenas window.iloc[:-1] para max histórico + close current.

## Resultado test P52 + BHDrawdownFilter cross-era

Tools: [`tools/v2_rb004_p52_with_bh_drawdown_gate.py`](../tools/v2_rb004_p52_with_bh_drawdown_gate.py).

3 thresholds × 3 assets × 5 windows = 45 probes. Wall ~30s.

**Drawdown reduction (Padrão 58 mitigation works):**

| Window | P52 raw MDD | P52+gate(25%) MDD | Reduction |
|---|---:|---:|---:|
| BTC 2022-H1 | 12% | 1.1% | -91% |
| ETH 2022-H1 | 11% | 1.1% | -90% |
| BTC 2022-H2 | 7.6% | 0.9% | -88% |
| SOL 2022-H2 | 12.4% | 0.95% | -92% |

**Drawdowns colapsam ~90% — gate efetivo contra bear extremo.**

**MAS — trade count cai dramaticamente:**

| Threshold | Mediana trades por probe | Probes com tr ≥ 30 |
|---|---:|---:|
| max_dd=15% | 2 | 0/15 |
| max_dd=25% | 2 | 0/15 |
| max_dd=35% | 3 | 0/15 |

**Gate ADR-0030 cross-era: FAIL em todos 3 thresholds.** Não por edge ausente, mas por trade count insuficiente.

Sharpe individual ainda mostra sinal: SOL 2024-H1+gate(35%) Sh=2.45 (1 trade), SOL 2023-H2+gate(35%) Sh=1.99 (3 trades), SOL 2022-H1+gate(35%) Sh=1.18 (4 trades). MAS 1-4 trades não constituem evidência estatística.

## Padrão 59 (novo)

**B&H drawdown gate vs sample size trade-off:**

Regime gate apertado é eficaz contra bear catastrófico (Padrão 58 mitigation), mas reduz trade count drasticamente em windows curtas (6 meses).

Tradeoff:
- Gate apertado → poucos trades, mas todos em bull/recovery (drawdowns minúsculos).
- Gate frouxo → mais trades, mas alguns em bear (drawdowns maiores).
- **Solução**: testar em janela contínua de 12-24 meses para trade count cumulativo ≥ 30.

Implicação V2: **janelas de 6 meses do roadmap V1 são insuficientes para estratégias com regime gate apertado**. Reformular gate ADR-0030 para essas estratégias: usar janela contínua 2024 (12 meses = H1+H2) ao invés de 2 windows separadas.

## Decision

1. **BHDrawdownFilter** implementado e operacional. Round-trip serialization OK.
2. **P52 + bh_drawdown** continua **QUARANTINED** — gate ADR-0030 strict FAIL devido a trade count.
3. **Drawdown protection works** — Padrão 58 mitigation confirmada quantitativamente (-90% MDD).
4. **Padrão 59** registrado: regime gate vs sample size tradeoff.
5. **Próximo passo:** testar P52 + bh_drawdown em janela continua estendida (1.5-2 anos) para acumular trade count. Requer concat de datasets (ingest extra) — adiado para Cycle 7.

## Lessons cross-cycle

- V2/RAIO entregou implementação engine novo em ~30 min wall-clock + ADR + test cross-era. Demonstra que custo dev de filtros novos é gerenciável.
- Tradeoff sample size é estrutural a regime gates — não é falha do filter. Padrão 59 é guidance permanente.

## Consequences

- **Positive:** primeiro filter V2 implementado (BHDrawdownFilter); arquitetura `regimes/filter.py` extensível confirmada; Padrão 58 mitigação validada quantitativamente; roadmap V2 RM034 (B&H DD gate) parcialmente coberto.
- **Negative:** P52 ainda não-exportável após Cycle 6. Necessita janela contínua estendida (Cycle 7+) para validação estatística.
- **Neutral:** filtro disponível para outros candidatos V2 que sofram do Padrão 58 (qualquer trend-long crypto).

## Follow-ups (Cycle 7+ autopilot)

- **Concat datasets** (script novo): merge BTC/ETH/SOL 1h 2023-H2 + 2024-H1 + 2024-H2 + 2025-H1 + 2025-H2 = 30 meses contínuos. Permite trade count ≥ 30 mesmo com gate apertado.
- **Re-test P52 + bh_drawdown(25%) sobre janela 30-meses contínua**: gate ADR-0030 reformulado: Sh ≥ 1.0 ∧ trades ≥ 30 ∧ MDD ≤ 5%.
- **Implementar tests unitários** para BHDrawdownFilter em `tests/test_regime_filter.py`.
- **Outras hipóteses V2 paralelas**: dado custo dev baixo de filter novo, considerar atacar EX001 (time stop curto) — exit_layer engine. Score similar.

## Não-alvo

- Não promover P52 + bh_drawdown sem janela continua estendida + trade count adequado.
- Não reduzir gate trade-count abaixo de 30 (ADR-0030).
- Não tentar outras strategies sem regime gate em bear absoluto — Padrão 58 universal pra trend-long crypto.

## Padrões totais: 59 (Padrão 59 novo)
