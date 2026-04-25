# 0053 — Série CE closeout: short side Bollinger/RSI FAIL, H2 reforçada

**Status:** Accepted — série arquivada. Manifest sem alteração.
**Date:** 2026-04-19
**Deciders:** Usuário + agente.
**Relates to:** ADR-0049 (meta-análise CA-CD), ADR-0051 (short side impl), ADR-0052 (pré-registro CE).

## Context

Série CE (ADR-0052) executou 18 pilotos short-only: Bollinger 20/1.5 + RSI 14/30/70, cross-period (2024-H2 / 2025-H1 / 2025-H2) × 3 ativos (BTC/ETH/SOL). Objetivo: resolver disputa H1 vs H2 de ADR-0049.

## Resultados

Dados crus: `exports/diag/ce_series_summary.json`. Tooling: `tools/run_ce_sweep.py`, `tools/summarize_ce.py`.

### Tabela completa

| Tag | Estrat | Ativo | Regime | trd | Sh | MDD% | fe | cost_r | MCp5 | Gate 1 |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|
| CE.1 | bol | btc | 2024-H2 | 115 | −0.87 | 12.69 | 9643 | 0.94 | 8925 | FAIL |
| CE.1 | rsi | btc | 2024-H2 | 62 | −2.77 | 15.20 | 8920 | 0.96 | 7905 | FAIL |
| CE.2 | bol | eth | 2024-H2 | 119 | −0.44 | 12.12 | 9755 | 0.94 | 8401 | FAIL |
| CE.2 | rsi | eth | 2024-H2 | 73 | −1.25 | 14.05 | 9356 | 0.96 | 8129 | FAIL |
| CE.3 | bol | sol | 2024-H2 | 123 | 0.80 | 9.34 | 10444 | 0.94 | 9378 | FAIL |
| CE.3 | rsi | sol | 2024-H2 | 65 | −1.09 | 19.33 | 9294 | 0.96 | 8043 | FAIL |
| CE.4 | bol | btc | 2025-H1 | 112 | −0.07 | 3.37 | 9957 | 0.94 | 9409 | FAIL |
| CE.4 | rsi | btc | 2025-H1 | 82 | 0.23 | 4.08 | 10070 | 0.96 | 9460 | FAIL |
| CE.5 | bol | eth | 2025-H1 | 130 | **2.45** | 7.00 | 11496 | 0.94 | 9978 | FAIL (cost_r) |
| CE.5 | rsi | eth | 2025-H1 | 100 | 0.55 | 7.25 | 10291 | 0.95 | 8780 | FAIL |
| CE.6 | bol | sol | 2025-H1 | 124 | **1.92** | 6.29 | 11346 | 0.94 | 9675 | FAIL (cost_r) |
| CE.6 | rsi | sol | 2025-H1 | 90 | 0.61 | 7.26 | 10372 | 0.96 | 8946 | FAIL |
| CE.7 | bol | btc | 2025-H2 | 118 | 1.06 | 8.00 | 10325 | 0.94 | 9653 | FAIL (cost_r) |
| CE.7 | rsi | btc | 2025-H2 | 92 | **1.64** | 4.97 | 10513 | 0.96 | 9796 | **PASS** |
| CE.8 | bol | eth | 2025-H2 | 115 | 0.37 | 8.59 | 10156 | 0.94 | 9051 | FAIL |
| CE.8 | rsi | eth | 2025-H2 | 84 | 1.15 | 8.57 | 10568 | 0.96 | 9298 | FAIL (MCp5) |
| CE.9 | bol | sol | 2025-H2 | 129 | **1.68** | 11.87 | 10995 | 0.94 | 9390 | FAIL (MCp5,cost_r) |
| CE.9 | rsi | sol | 2025-H2 | 86 | **2.30** | 5.13 | 11381 | 0.96 | 9898 | **PASS** |

### Gates — avaliação final (pré-registrada, ADR-0052)

- **Gate 1** (≥6/18 passam critério manifest): **2/18 → FAIL**
- **Gate 2** (falsificacionista, ≤1/6 em 2024-H2): **0/6 → PASS** (short sangra em bull forte, como previsto)
- **Gate 3** (regime preferido, ≥3/6 em 2025-H1): **0/6 → FAIL** (Gate 3 é diagnóstico, não bloqueador)
- **Gate 4** (assimetria Bollinger vs RSI): bol=0/9, rsi=2/9, delta=2 (dentro do ruído)

**Veredicto overall (Gate 1 + Gate 2 coerência)**: **FAIL**. Série arquivada.

## Interpretação

### H2 de ADR-0049 reforçada, H1 falsificada

ADR-0049 colocou duas hipóteses:
- **H1**: short resgata o projeto (passa Gate 1 com ≥6/18)
- **H2**: regime domina; short também colapsa

Com 2/18 passando (≈11%, abaixo do 33% esperado), **H1 é rejeitada**. Short puro não tem edge material cross-period no universo testado.

### MAS: Gate 3 quase-pass informa

Apesar de Gate 3 ter FAIL (0/6 passam todas as métricas em 2025-H1), **4/6 dos pilotos 2025-H1 têm Sharpe positivo** (Bollinger: 2.45, 1.92; RSI: 0.23, 0.55, 0.61). Bloqueiam em cost_r (stress `fee+10`, `spread+10`) e em MC p5.

Os dois pilotos Bollinger 2025-H1 (ETH e SOL) têm **Sharpe > 1.9** e **fe > 11k** no baseline — falhas são todas em cost_r (0.94 < 0.95) e em algumas em MC p5. Ordem de grandeza próxima ao manifest v2 (Sharpe 1.21-2.40).

**Leitura**: existe edge **frágil** em 2025-H1 chop pra Bollinger short, mas é fino demais pra sobreviver ao cost stress +10bps. O problema é **custo operacional**, não ausência de edge. Mesma conclusão que ADR-0048 tirou do filtro: "o edge puro de mean-rev está lá, mas sozinho não passa cost stress".

### Coerência com audit ADR-0048

Audit B mostrou que Bollinger 30/1.5 **long** sem filtro tem MC p5=9968 (também < 10000 gate). Agora CE mostra Bollinger 20/1.5 **short** em chop tem Sharpe forte mas cost_r<0.95. **Simetria confirmada**: Bollinger puro (long OU short) é edge marginal — precisa de filtro composicional pra promover a gate-passer.

### Falsificação Gate 2 — crypto se comporta como esperado

Gate 2 PASS (0/6 em 2024-H2 passam) confirma que o universo se comporta como crypto historicamente se comporta: bull extendido mata short mean-rev (cada overbought é continuation). Isso é **garantia de sanidade** — se tivesse falhado (ex: 3/6 em 2024-H2), indicaria bug ou rótulo de regime errado.

### Direção do edge em chop vs bull — padrão cristalizado

Combinando CA-CE + audit:

| Regime | Long mean-rev | Short mean-rev | Long trend | Short trend |
|---|---|---|---|---|
| Bull forte (2024-H2) | **EDGE** (manifest) | SANGRA | neutro/flat | SANGRA |
| Chop (2025-H1) | fraco/borderline | **edge frágil** (cost-bound) | FLAT | fraco-borderline (CD.3 lift) |
| Bull moderado (2025-H2) | fraco | edge moderado (CE.7, CE.9 passam) | fraco/flat | fraco |

**Padrão 8** (novo, adicional aos 7 de ADR-0049): **"cada regime tem uma direcionalidade preferida; combinar sem filtro = ruído dominando"**. Manifest v2 exemplifica: edge só aparece com filtro (BollingerWidthFilter) que isola o sub-regime onde a direção é favorável.

## Consequences

### Imediatas

- **Manifest não muda.** Nenhum combo short é adicionado. ADR-0030 (runtime-faithful) e ADR-0017/0031 preservados.
- **Bot BotBinance não é notificado** (signal-only rule: nenhuma mudança de decisão pra ele).
- **ADR-0051 permanece válida**: código curto (short Bollinger/RSI) fica no repo como capability arquitetural, independente de evidence empírica. É pré-requisito pra séries futuras de composição.

### Futuras direções (priorizadas)

Baseado em CE + revisão de ADR-0050:

1. **Prioridade 1 — Série CF: Bollinger short + BollingerWidthFilter** (composicional). Replicar template do manifest v2 mas na direção oposta. Se Bollinger long+width passa em bull 2024-H2, Bollinger short+width **deveria** passar em chop 2025-H1 — simétrico ao sucesso do manifest. Teste direto: isola se o problema do short é custo (cost_r) ou edge puro.

2. **Prioridade 2 — ADR-0050 §D3 (volatility-adjusted sizing)**. Observação empírica: CE mostra 4-5 pilotos 2025-H1 com fe > 10k mas bloqueados em cost_r, e Sharpe flutuando 0.23-2.45 no mesmo regime. **Sizing fixo ignora essa variação**. Reduzir fração em períodos de alto overbought falseamento poderia estabilizar edge. Escopo maior, payoff incerto, mas vira plausível agora.

3. **Prioridade 3 (backlog) — ADR-0050 §D5 (regime-gated ensemble)**. Usar `trend_htf` não pra filtrar **dentro** de uma estratégia, mas pra **switchar** entre long e short. Long-only quando htf bullish, short-only quando htf bearish. CE mostra que o *sinal* existe em cada direção — só não sobrevive sozinho. Ensemble gated é caro de implementar (3 estados long/flat/short, capital alocação), mas é a evolução lógica.

**Escolhido como próximo passo**: **Série CF (Bollinger short + BollingerWidthFilter)**. Razão:
- Reusa infraestrutura (filter já existe).
- Testa hipótese específica e falsificável (simetria com manifest).
- Se falhar, condena definitivamente mean-rev short como família; se passar, temos **segundo combo composicional** pra manifest, duplicando o universo aprovável.
- Custo: ~30min compute + 2 ADRs.

### Regra ressaltada

- **Cost stress é a fronteira real.** 4 pilotos 2025-H1 têm Sharpe > 0.5 e fe > 10k, mas cost_r=0.94 é o corte. `fee+10bps` (mais 100% do taker atual) e `spread+10bps` consomem o edge. Gate `cost_r ≥ 0.95` existe por boa razão (ADR-0014): o edge precisa sobreviver a degradação operacional. Série CF vai enfrentar esse mesmo gate — se não reduzir turnover ou isolar sub-regime produtivo, falha simétrica.

## Critério de sucesso deste closeout

1. `ce_series_summary.json` arquivado ✓
2. Gates 1-4 avaliados com veredicto registrado ✓
3. Direção próxima escolhida (Série CF) ✓
4. Padrão 8 documentado em meta-estrutura ✓

## Fora do escopo

- Re-interpretar os 2 pilotos PASS (CE.7 rsi btc 2025-H2 Sharpe 1.64, CE.9 rsi sol 2025-H2 Sharpe 2.30). Passam Gate 1 isoladamente mas 2/18 é **abaixo** do gate de série. Não promoveremos os 2 individualmente — densidade de pass rate é critério, não quantidade absoluta. Alinhado com ADR-0049 §Padrão 5 (anti-cherry-pick).
- Re-rodar com seeds diferentes. ADR-0048 Audit A mostrou que seed não move Sharpe (determinístico no WF); apenas MC percentis, e mudança típica é < 30 pontos.
- Grid-search em (window, num_std) ou (period, os, ob). Alinhado com ADR-0049 §Padrão 5.
