# 0092 — Série CW closeout: 1/9 PASS → ETH 2024-H2 promove v7 (primeiro long RSI-based)

**Status:** Accepted — promoção condicional v7 candidato (1 combo)
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0091 (pré-registro CW), ADR-0090 (CV closeout), ADR-0088 (Padrão 20), v2 Bollinger long (precedente filter-based long)

## Resultado

| Tag | Asset | Window | Trades | PnL% | Sharpe | Naked | Delta | MC p5 | Verdict |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| CW.1 | BTC | 2024-H2 | 17 | +0.81 | +0.751 | +0.886 | −0.135 | 9957 | FAIL (trades) |
| **CW.2** | **ETH** | **2024-H2** | **30** | **+3.09** | **+1.774** | +0.651 | **+1.123** | 10045 | **PASS** |
| CW.3 | SOL | 2024-H2 | 36 | −0.84 | −0.286 | −0.103 | −0.183 | 9561 | FAIL |
| CW.4 | BTC | 2025-H1 | 16 | +2.04 | +1.409 | +0.829 | +0.580 | 10076 | FAIL (trades) |
| CW.5 | ETH | 2025-H1 | 43 | −0.72 | −0.221 | −0.535 | +0.314 | 9219 | FAIL |
| CW.6 | SOL | 2025-H1 | 54 | −0.19 | −0.006 | +0.074 | −0.080 | 8969 | FAIL |
| CW.7 | BTC | 2025-H2 | 28 | −0.58 | −0.482 | −2.343 | +1.861 | 9700 | FAIL (trades) |
| CW.8 | ETH | 2025-H2 | 48 | +1.13 | +0.476 | +0.669 | −0.193 | 9504 | FAIL |
| CW.9 | SOL | 2025-H2 | 45 | +0.84 | +0.318 | +0.401 | −0.083 | 9177 | FAIL |

**PASS = 1/9 (CW.2 ETH 2024-H2).**

## Avaliação dos gates

### Gate 1 (≥1 PASS): **PASS 1/9**
Apenas CW.2. Gate 1 cleared com margem (Sh=1.77, todos subgates OK):
- Trades: 30 (no limite)
- PnL: 3.09% (> 3% gate)
- MDD: 3.21%
- MC p5: 10045 (> 9500)
- cost_r: 0.984 (> 0.95)

### Gate 2 (load-bearing vs naked): **PASS**
CW.2 Sh=1.77 vs CV.2 naked Sh=+0.651 → **+1.12 lift**. Filter width load-bearing estrito (naked FAIL Gate 1 → filter promove a PASS). Padrão 19 satisfeito.

### Gate 3 (Promoção): **PASS candidato v7**
1 combo qualifica. v7 candidato `rsi_long_width_2024h2_eth.json` a emitir.

### Gate 4 (overlap v2 Bollinger long): **SEM CONFLITO**
v2 cobre ETH 2024-H1 (não H2), BTC 2024-H2, SOL 2024-H2. **ETH 2024-H2 é gap do v2** — CW.2 preenche. Não há duplicação Padrão 12.

### Observação Padrão 20 refinado

CV.1 BTC 2024-H2 naked Sh=0.89 → CW.1 BTC 2024-H2 filter Sh=0.75 **piorou**. Filter cortou trades (47→17) e não recuperou edge. BTC não é candidate long mesmo com filter em 2024-H2.

CW.4 BTC 2025-H1 Sh=1.41 mas trades=16 FAIL (Padrão 12). Setup interessante mas sub-sampled — documentar como hipótese futura cross-period não-explorada (sem promoção).

CW.7 BTC 2025-H2 delta +1.86 vs naked −2.34 (filter recupera de catastrófico para neutro) — filter salva mas não cria edge. Não PASS.

**Padrão 20 permanece válido** (só CW.2 quebra o 0/15 long-FAIL combinado CU+CV+CW). Long-side é exceção rara, quase-aleatória (1/15 = 6.7%). ETH 2024-H2 é o combo de escape — merecerá monitoramento em paper-trade.

## Decisão

### 1. Emitir v7 `rsi_long_width_eth_2024h2_20260420.json` com 1 combo

- Engine: RSI(14/30/70) long_only=true
- Filter: bollinger_width(window=30, num_std=1.5, min_width_bps=300)
- Combo: ETHUSDT 1h 2024-07-05..2024-12-31
- Runtime invariants ADR-0030 (faithful, fixed_notional=2000, entry/exit market at open next bar, stop=disabled)
- source_run_id: cw-eth-rsi-long-width300-2024h2

### 2. Bridge AF↔bot posta v7 (mudança de stack, segunda desde 2026-04-19T17Z)

Ações bot:
- Adicionar v7 ao whitelist
- Re-validar envelope localmente
- Paper-trade (sem pressa live)

### 3. Não-promoção demais 8 combos CW

CW.1/CW.4/CW.7 FAIL por trade count (subamostragem pós-filter). CW.3/5/6/8/9 FAIL geral (Sh, PnL, MC).

### 4. Não-abrir CW-H2 (trend_htf long_only)

H1 (width) PASS suficiente. Abrir H2 agora seria especulativo. Deixar como hipótese futura se usuário retomar long-side.

## Stack pós-v7

| Manifest | Família | Direção | Combos |
|---|---|---|---:|
| v2 | Bollinger | long | 3 |
| v3 | Bollinger | short | 4 |
| v4a | RSI width | short | 1 |
| v4b | RSI naked | short | 2 |
| v6 | RSI trend | short | 1 |
| **v7 (NOVO)** | **RSI width** | **long** | **1** |

**Total: 12 combos** (4 long + 8 short). Primeira expansão long RSI-based.

## Padrão insight (não formalizado como novo padrão)

Long em crypto 1h: **filter-rescued** é a receita. Naked não funciona (Padrão 20), width filter pode funcionar em janelas específicas. Taxa de sucesso pós-filter: 1/9 CW vs 0/9 naked CU+CV. Filter eleva baseline mas não garante edge — combo-específico.

Não promove padrão formal porque amostra é pequena (1/9). Se segunda série de long-filter vier com taxa similar (~10%), formalizar.

## Critério de sucesso desta ADR

1. CW fechado com verdict ✓
2. v7 candidato emitido (próximo)
3. Bridge AF↔bot posta (próximo)
4. STATE.md atualizado (próximo)
5. Padrão 20 preservado com exceção documentada ✓
