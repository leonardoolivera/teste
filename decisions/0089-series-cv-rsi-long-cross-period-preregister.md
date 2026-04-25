# 0089 — Série CV pré-registro: RSI long cross-period 2024-H2 + 2025-H2 (BTC/ETH/SOL)

**Status:** Accepted — pré-registro antes de rodar
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0088 (CU closeout + Padrão 20), ADR-0030 (runtime-faithful)

## Hipótese

CU refutou RSI long em chop 2025-H1 (0/3). Hipótese: **long funciona em janelas com drift positivo** (2024-H2 bull, 2025-H2 misto), refutado apenas em chop puro descendente.

Sub-hipóteses:
- **H1:** 2024-H2 (bull): RSI long pega oversold dentro de uptrend — setup clássico. Esperado PASS ≥1/3.
- **H2:** 2025-H2 (misto): drift positivo + reversões. RSI long deve pegar parte. Esperado PASS 1-2/3.
- **H-null:** RSI long não funciona em nenhuma janela (refuta long-side definitivamente).

## Design

**Pilotos (naked, sem regime filter):**

| Tag | Symbol | Window | Modo |
|---|---|---|---|
| CV.1 | BTCUSDT | 2024-H2 (20240705_20241231) | long |
| CV.2 | ETHUSDT | 2024-H2 | long |
| CV.3 | SOLUSDT | 2024-H2 | long |
| CV.4 | BTCUSDT | 2025-H2 (20250705_20251231) | long |
| CV.5 | ETHUSDT | 2025-H2 | long |
| CV.6 | SOLUSDT | 2025-H2 | long |

Engine: RSI(14/30/70) long_only=true. Naked. Runtime invariants ADR-0030 (faithful, fixed_notional=2000).

Total: 6 runs (~15min).

## Gates pré-registrados

### Gate 1 — Passes isolados
Por janela: ≥1/3 PASS (Sh≥1.0, trades≥30, MDD≤20%, MC p5>9500, cost_r≥0.95, PnL>3%).

### Gate 2 — Comparação com CU (2025-H1 chop refutado)
Para cada combo CV PASS, Sh > Sh correspondente em CU (mesmo ativo). Gate informacional, não bloqueador.

### Gate 3 — Promoção v7 candidato
Combos PASS → manifest v7 `rsi_long_cross_period.json` (escopo cross-period). Se 2024-H2 ≥2 PASS + 2025-H2 ≥1 PASS, v7 é manifest multi-combo robusto. Se apenas 1 combo PASS total, considerar candidato marginal (decidir no closeout).

### Gate 4 — Assimetria hipótese
Se 2024-H2 PASS >> 2025-H1/H2 PASS → confirma hipótese H1 (long precisa drift positivo). Se 2024-H2 FAIL também → refuta long-side definitivamente (ADR-0088 Padrão 20 reforçado).

## Riscos antecipados

1. **2024-H2 trade count alto mas Sh pode ser baixo** — bull pode não dar reversões suficientes para RSI(14) oversold. Se RSI long só pega tops antes correção, Sh baixo.
2. **2025-H2 já coberto no short-side (v4b)** — se long também passa, gera oportunidade **stack direcional misto** (long + short mesmo ativo/janela). Novo problema: sizing combinado. Decidir no closeout se PASS.
3. **SOL bull 2024-H2 pode dar Sh≥2** (SOL teve rally agressivo) — mas MDD pode estourar 20% em pull-backs. Monitorar.

## Critério de sucesso desta ADR

1. Sweep CV executado e arquivado
2. ADR-0090 closeout documenta verdict por janela
3. Se promoção: v7 manifest emitido
4. Se refutação cross-period: Padrão 20 reforçado (long-side irrelevante cross-period)
5. STATE.md atualizado
