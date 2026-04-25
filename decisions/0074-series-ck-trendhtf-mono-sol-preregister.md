# 0074 — Série CK: RSI short + TrendHTF mono-SOL (pré-registro)

**Status:** Accepted — pré-registro; execução autorizada
**Date:** 2026-04-19
**Deciders:** Usuário + agente
**Relates to:** ADR-0073 (CJ closeout, Padrão 14), ADR-0069 (v4a/v4b ativos), ADR-0062 (CH closeout PASS RSI+width)

## Contexto

CJ (RSI short + TrendHTF, 9 pilotos cross-asset) fechou 2/9 PASS. Os 2 PASS são **SOL** (CJ.6 2025-H1 Sh 1.96, CJ.9 2025-H2 Sh 2.71). BTC e ETH degradaram. Padrão 14 documentado: filter direcional HTF é asset-específico — amplifica em SOL, degrada em BTC chop.

CK testa Padrão 14 isoladamente: **mono-SOL, 3 janelas**. Se 2-3/3 PASS confirma efeito; abre caminho para manifest v5 SOL-amplified + audit dedicado vs v4a/v4b SOL.

## Diferenciação vs CJ

CJ rodou 9 pilotos cross-asset com TrendHTF. CK rerun apenas SOL nas 3 janelas — **2 já em CJ** (SOL 2025-H1=CJ.6, SOL 2025-H2=CJ.9), portanto seriam idênticas em re-run determinístico. **Não vou re-rodá-las.** Apenas re-uso os runs já em disco (`cj-rsi-14-30-70-sol-*-trendhtf-4h-50-short`). Nova run: **CK.1 SOL 2024-H2** (já existe em CJ.3, também idêntica). 

**Conclusão:** CK não exige novos runs. É **re-leitura analítica** focada nos 3 SOL de CJ (CJ.3, CJ.6, CJ.9) com gates específicos mono-asset. ADR registra a análise + decisão de promoção/não-promoção sem desperdiçar compute.

Trade-off da decisão: se o agente quiser variação real (htf=1d em vez de 4h, ou sma=100 em vez de 50), aí seria série CK separada com runs novos. Esta CK é **análise enxuta** + decisão.

## Decisão

Análise mono-SOL re-utilizando CJ.3, CJ.6, CJ.9. 3 pilotos:

| Tag | Asset | Janela | Reusa |
|---|---|---|---|
| CK.1 | SOL | 2024-H2 | CJ.3 |
| CK.2 | SOL | 2025-H1 | CJ.6 |
| CK.3 | SOL | 2025-H2 | CJ.9 |

### Gates pré-registrados (mono-SOL)

- **Gate 1 — principal mono-asset:** ≥ **2/3** PASS critério manifest (trades≥30, Sharpe≥1.0, MDD≤20, MCp5>9500, cost_r≥0.95)
- **Gate 2 — lift vs CH SOL** (RSI+width): em ≥ **2/3** janelas, CK Sh > CH Sh **E** CK PASS. Se TrendHTF não traz lift onde width já passa, é redundância cara.
- **Gate 3 — lift vs v4 SOL** (manifest ativo): em janelas onde v4a/v4b SOL ativos (2025-H1 v4a width, 2025-H2 v4b no-filter), CK precisa Sh > v4_sh para justificar substituir. v4a SOL 2025-H1 Sh=1.32; v4b SOL 2025-H2 Sh=2.30.
- **Gate 4 — audit Gate B obrigatório** (Padrão 12): se Gate 1 PASS, próxima ADR roda CK sem TrendHTF (= já existe via CH/audit-v4a-sol/audit-v4b-sol) e confirma TrendHTF load-bearing.
- **Gate 5 — seed stability** (Padrão 14 reforço): se Gate 1+2+3+4 PASS, exigir seed {1337, 2024} antes de promover (igual v4b).

### Critério de promoção (combinado)

Manifest v5 SOL-amplified TrendHTF criado **se e somente se**: Gate 1 PASS + Gate 2 PASS + Gate 3 PASS pelo menos parcial + Gate 4 PASS audit + Gate 5 PASS stability.

Se 2024-H2 SOL FAIL (esperado por CJ.3 Sh=−1.02), promoção fica escopada a 2025-H1+H2 SOL. Se BTC ou ETH adicionados em série futura também passam mono-asset, expansão em ADR separada.

## Hipóteses explícitas

1. **H-mono-SOL-confirma** (Gate 1 PASS 2/3): SOL 2025-H1+2025-H2 PASS, 2024-H2 FAIL. Padrão 14 confirmado. Promoção candidata.
2. **H-2024-H2-tambem** (Gate 1 PASS 3/3, surpresa): TrendHTF salva 2024-H2 SOL especificamente — improvável dado CJ.3 Sh=−1.02 já registrado, mas re-leitura confirma número.
3. **H-mono-SOL-redundante** (Gate 1 PASS mas Gate 2/3 FAIL): TrendHTF passa mas não bate width (CH SOL 2025-H1 Sh=1.32 < CK.2 1.96 — improvável FAIL Gate 2 nesse caso). Cenário menos provável.

## Alternativas consideradas

### Variar htf=1d ou sma_window=100
Rejeitado nesta série — variar parâmetros agora seria nova hipótese, não confirmação de Padrão 14. Se CK confirma, ADR futura pode varrer parâmetros.

### Adicionar BTC/ETH explicitamente
Rejeitado — CJ já registrou BTC/ETH FAIL com TrendHTF. Re-rodar não muda número. Mono-asset SOL é o foco.

### Composição AND TrendHTF + width
Rejeitado nesta série. Composição é hipótese ortogonal; teste isolado primeiro.

## Saída da série

- **Gate 1 + 2 + 3 PASS:** abre ADR-0075 audit Gate B (já tem dados, é re-leitura de CH SOL + audit-v4-a-sol/audit-v4-b-sol). Se PASS, ADR-0076 seed stability {1337, 2024} mono-SOL TrendHTF (2 runs novos). Se PASS, ADR-0077 promoção v5 SOL-amplified.
- **Gate 1 PASS mas Gate 2/3 FAIL:** TrendHTF redundante vs width pra SOL. Documenta como aprendizado e arquiva.
- **Gate 1 FAIL:** CK refuta Padrão 14 mono-SOL. Volta pro pool de hipóteses.

## Tooling

Sem novos runs. Análise inline reusa `exports/diag/series_cj_summary.json` filtrando SOL.

## Timebox

~5min análise + ADR-0075 (closeout) mesmo turno.

## Critério de sucesso desta ADR

1. Análise mono-SOL com gates 1-3 avaliados ✓
2. Decisão de promoção/não-promoção registrada
3. Se promover: roadmap claro (audit Gate B → seed stability → ADR promoção)
