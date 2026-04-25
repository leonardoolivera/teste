# 0208 — Governor rescalado (2/3/5-stop) no stack 13 — net negativo

**Status:** Accepted (diagnóstico; governor 2/3/5 dispara em 3/13 mas destrói edge em 1 combo)
**Date:** 2026-04-22
**Deciders:** Agente (follow-up proativo do ADR-0207 — não foi pedido direto do user; autopilot continua para a próxima frente natural listada no próprio ADR-0207)
**Relates to:** ADR-0207 (governor 3/5/7 inerte), ADR-0206 (fixed_notional 100% baseline), ADR-0030 (faithful sizing invariant).

## Contexto

ADR-0207 fechou com governor 3/5/7 **inerte** em 13/13 combos — regra desenhada para scalping intraday não dispara em 1h MR. A seção "Alternatives considered" do ADR-0207 listou `half_at=2, stop_day_at=3, stop_week_at_consec=5` como "efeito real, mas não foi o que user pediu; registro para referência futura; não rodado".

Em modo autopilot (memory `feedback_autopilot_handoff_continue`: refutada → closeout → próxima frente), rodei essa variante rescalada sobre os mesmos 13 combos / sizing B (fixed_notional 100%) / cost model / períodos.

Script: [`scripts/run_governor_stops_stack13.py`](../scripts/run_governor_stops_stack13.py) com constantes no topo editadas para `HALF_AT=2, STOP_DAY_AT=3, STOP_WEEK_AT=5`.
Artefato: [`exports/diag/governor_stops_stack13_235_20260422.json`](../exports/diag/governor_stops_stack13_235_20260422.json).

## Resultado

Governor dispara em **3/13 combos** (vs 0/13 no 3/5/7).

| # | Combo | base Sh / PnL% | gov Sh / PnL% | MDD% | half | skip_d | skip_w | ΔSh | ΔPnL% |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | BB-long ETH 2024-H1 | 2.085 / 25.38 | 2.085 / 25.38 | 8.1 | 0 | 0 | 0 | 0 | 0 |
| 2 | BB-long ETH 2025-H1 | 1.82 / 30.80 | 1.82 / 30.80 | 14.2 | 0 | 0 | 0 | 0 | 0 |
| 3 | BB-long BTC 2024-H2 | 0.646 / 5.36 | 0.646 / 5.36 | 12.4 | 0 | 0 | 0 | 0 | 0 |
| 4 | BB-long SOL 2024-H2 | 1.887 / 32.77 | 1.887 / 32.77 | 20.1 | 0 | 0 | 0 | 0 | 0 |
| 5 | BB-bidir SOL 2024-H2 | 0.921 / 17.45 | 0.901 / 16.91 | 24.0 | **1** | 0 | 0 | -0.020 | -0.54 |
| 6 | BB-bidir BTC 2025-H1 | 1.914 / 20.32 | 1.914 / 20.32 | 10.1 | 0 | 0 | 0 | 0 | 0 |
| 7 | BB-bidir ETH 2025-H1 | 3.009 / 82.60 | 3.009 / 82.60 | 17.5 | 0 | 0 | 0 | 0 | 0 |
| 8 | **BB-bidir SOL 2025-H1** | 1.931 / 69.68 | **0.784** / **16.27** | **35.5** | 0 | 0 | **20** | **-1.147** | **-53.4** |
| 9 | RSI-long ETH 2024-H2 | 1.293 / 11.84 | 1.293 / 11.84 | 10.5 | 0 | 0 | 0 | 0 | 0 |
| 10 | RSI-short BTC 2025-H2 | 1.782 / 29.15 | 1.604 / 26.07 | 18.6 | 0 | 0 | **4** | -0.178 | -3.09 |
| 11 | RSI-short SOL 2025-H2 | 2.003 / 69.18 | 2.003 / 69.18 | 27.6 | 0 | 0 | 0 | 0 | 0 |
| 12 | RSI-short trendhtf SOL 2025-H1 | 1.914 / 57.26 | 1.914 / 57.26 | 21.3 | 0 | 0 | 0 | 0 | 0 |
| 13 | RSI-short width BTC 2025-H1 | 2.197 / 27.88 | 2.197 / 27.88 | 5.8 | 0 | 0 | 0 | 0 | 0 |

(Sharpe aqui é per-trade annualizado — consistente dentro desta linha mas não diretamente comparável ao Sharpe-1h de ADR-0206.)

**Resumo agregado:**
- 10/13 combos: inalterados (threshold 2/3/5 nunca atingido).
- 1/13 (#5): efeito desprezível — 1 trade halved; Sharpe -0.020, PnL -0.54 p.p.
- 1/13 (#10): efeito moderado — 4 trades skippados pela semana; Sharpe -0.178, PnL -3.09 p.p.
- 1/13 (#8): **destruição de edge** — 20 trades skippados pela semana; Sharpe cortado para ~40% do baseline, PnL cortado para ~23% do baseline. **MDD piora** (35.5% vs 43.3% no fixed_100 — mas o min_equity é pior relativo ao running-max, já que o combo foi cortado durante o período de recovery).

## Interpretação

O dano em #8 é o tell: em uma estratégia **mean-reversion**, uma streak de 5 perdas consecutivas frequentemente precede a reversão que gera os **winners** subsequentes. O week-stop `≥5 consec losses → bloqueia a semana ISO` corta precisamente os trades de recovery que monetizam a edge.

- Padrão 48 (novo): **em MR stacks, bloqueio por streak de perdas é asymmetric kill** — max perda evitada durante a streak < winner evitado depois da reversão (em expectation). Week-stop específicamente agrava porque a janela de reset (segunda-feira ISO) pode atrasar em dias o re-enable.
- Os outros 2 triggers (halve-at-2 em #5, stop-week em #10) são efeitos de ordem muito menor.

Este achado **contradiz** a hipótese implícita em ADR-0207 de que "rescalar para 1h daria efeito real e útil". O efeito é real, mas é **líquido negativo**.

## Consequences

- **Positive:** evidência quantitativa de que governor de streak **não é compatível com mean-reversion** no stack atual. Remove argumento para adotar qualquer variante (mais frouxa = inerte; mais apertada = destrutiva).
- **Negative:** nenhuma — diagnóstico.
- **Neutral:** stack 13 permanece sem governor. Manifests inalterados. `runtime_contract: faithful` mantido (governor nunca foi parte do manifest).

## Alternatives considered

- **Governor sem week-stop** (apenas half/stop dentro do dia): como o 3/5/7 já mostrou que intraday é inerte em 1h, versão apenas-diária de 2/3 também seria quase-inerte (máx. L/dia ∈ {1,2} em ADR-0207). Teria efeito só em #5 (1 halved trade) — irrelevante. Skip.
- **Governor por drawdown de equity** (ex. reduzir sizing se equity cai X%): ortogonal — não é o que o user pediu e substitui a mecânica de "contar perdas" por "observar equity". Registrar para probe futuro se user pedir.
- **Governor com reset em win** (streak zera só em W real, não em qualquer trade ≥0): já é o comportamento implementado (zera só em `pnl > 0`). Não muda o achado.
- **Governor por volatilidade do ativo** (reduzir sizing quando ATR cresce): orthogonal; não rodado.

## Follow-ups

- STATE.md: adicionar addendum 3 (2026-04-22, ADR-0208).
- Nenhum handoff. Stack 13 inalterado.
- Se user pedir outro variante (p.ex. governor por equity-drawdown, ou stop-day sem week-stop), reusar `scripts/run_governor_stops_stack13.py` — estrutura do replay já está genérica o suficiente.
- **Recomendação para o user:** governor de perdas, nas variantes testadas (3/5/7 e 2/3/5), não agrega valor no stack 13. Para este regime de trade density (1h MR, 0.16–0.77 trades/dia), o mecanismo correto de controle de risco é **sizing notional**, não **counting-based governor**. Padrão 48 registrado.
