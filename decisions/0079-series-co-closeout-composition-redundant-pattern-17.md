# 0079 — Série CO closeout: composição AND width+TrendHTF é redundante (TrendHTF dominante) — Padrão 17

**Status:** Accepted — Gate 1 PASS analítico, Gate 2+4 FAIL, NÃO-promoção
**Date:** 2026-04-19
**Deciders:** Usuário + agente (AF)
**Relates to:** ADR-0078 (pré-registro CO), ADR-0075 (CK closeout — Padrão 15), ADR-0068 (Padrão 12 audit Gate B), ADR-0069 (v4a/v4b ativos)

## Resultado

3 runs CO + 4 runs Gate 4 audit (sem-width / sem-trend para cada PASS).

### CO principal (composto AND width+TrendHTF)

| Tag | Janela | Trades | PnL% | MDD% | Sharpe | MC p5 | cost_r | Verdict |
|---|---|---:|---:|---:|---:|---:|---:|---|
| CO.1 | SOL 2024-H2 | 29 | −2.89 | 7.08 | −0.880 | 9132 | 0.9817 | FAIL (trades=29, Sh, MCp5) |
| CO.2 | SOL 2025-H1 | 50 | +7.75 | 4.30 | +1.653 | 9683 | 0.9703 | PASS |
| CO.3 | SOL 2025-H2 | 46 | +10.98 | 4.87 | +2.920 | 10179 | 0.9776 | PASS |

### Gate 4 audit (load-bearing teste do composto)

| Variante | Trades | Sharpe | MDD% | MC p5 | cost_r | PASS isolada? |
|---|---:|---:|---:|---:|---:|---|
| CO.2 composto | 50 | 1.653 | 4.30 | 9683 | 0.9703 | PASS |
| **CO.2 noWidth (trend-only)** | 51 | **1.958** | 4.75 | 9712 | 0.9705 | **PASS — Sh > composto** |
| CO.2 noTrend (width-only) = CH.6 | 94 | 1.319 | 5.74 | 9558 | 0.9555 | PASS |
| CO.3 composto | 46 | 2.920 | 4.87 | 10179 | 0.9776 | PASS |
| **CO.3 noWidth (trend-only)** | 55 | 2.708 | 4.86 | 10144 | 0.9741 | **PASS — só −0.21 vs composto** |
| CO.3 noTrend (width-only) ≈ CH.9 | 80 | 1.918 | 4.57 | 9777 | 0.9620 | PASS |

Dados crus: `exports/diag/series_co_summary.json` + `results/validation/co-audit-*`.

## Avaliação dos gates pré-registrados

- **Gate 1 (≥2/3 PASS):** 2/3 → **PASS analítico**
- **Gate 2 (Sh ≥ max(legs)+0.3 em ≥2/3):** **FAIL 0/3**
  - CO.2: 1.65 vs max(width 1.32, trend 1.96) = 1.96 → **−0.31 (composto pior que melhor perna!)**
  - CO.3: 2.92 vs max(width 1.92, trend 2.71) = 2.71 → **+0.21 (lift insuficiente, precisava ≥+0.3)**
- **Gate 3 (trades≥30 em ≥2/3):** 2/3 → PASS (CO.1 ficou em 29, marginal)
- **Gate 4 (composto load-bearing — sem qualquer perna composto cai pra FAIL):** **FAIL inequívoco**
  - CO.2: tirar width → Sh sobe (1.65→1.96), tirar trend → Sh cai mas ainda PASS (1.32). **Composto não é load-bearing por nenhum lado.**
  - CO.3: tirar width → Sh cai marginal (2.92→2.71, ainda PASS), tirar trend → Sh cai mais (2.92→1.92, ainda PASS). **Composto não é load-bearing por nenhum lado.**
- **Gate 5 (Padrão 15 prevenção):** lift sem load-bearing = candidato edge fantasma → **bloqueia promoção**

**H-composto-redundante confirmada.** Composição preserva (no melhor caso) apenas a perna dominante (TrendHTF) e adiciona overhead que pode ser ativamente prejudicial (CO.2 width destrói edge: trend-only 1.96 > composto 1.65).

## Interpretação

### Por que composição AND width+TrendHTF não cria edge novo

Hipótese inicial era: width filtra para "regime apto" (volatilidade contraída) + TrendHTF filtra para "direção alinhada" (sma curta abaixo do close = trend down em 4h). Espectava-se intersecção AND = "regime apto **E** direção alinhada" = combo de qualidade superior.

Mecânica observada:
1. **TrendHTF SOL 2025+ é dominante.** Tanto CK (trend-only) quanto CO (composto) atingem Sh 1.96-2.71 em SOL 2025. Width adiciona, no melhor caso, +0.21 Sh (CO.3) e no pior, **−0.31 Sh** (CO.2).
2. **Trade count cai 30-50%.** CO.2 50 trades vs trend-only 51 vs width-only 94. CO.3 46 vs trend-only 55 vs width-only 80. AND é restritivo, mas a restrição não filtra qualidade — filtra ruído **ortogonal ao edge** quando trend já alinhou.
3. **CO.2 reverso (width destrói edge):** trend-only Sh 1.96 → composto 1.65. Hipótese: em SOL 2025-H1 (chop com tendência fraca), width 300 às vezes filtra **bons sinais** que TrendHTF aprovou (volatilidade tinha contraído mas tendência 4h ainda estava forte). O filter width é cego à direção — bloqueia entradas válidas.
4. **CO.1 SOL 2024-H2 FAIL com 29 trades:** combinação de filters reduziu sample para 29 (1 abaixo do gate). Width-only (CH.3) tinha 88 trades aqui mas Sh −0.39. TrendHTF-only (CK.1) Sh −1.02. Ambos FAIL em 2024-H2 — composto não salva onde nenhuma perna funciona.

### Por que isso é informação positiva

Refutar H-composto-load-bearing **fortalece** Padrão 15 (ADR-0075):
- TrendHTF mono-SOL 2025+ é o edge real (não composto, não width)
- v4b SOL 2025-H2 (RSI puro Sh=2.30) já cobre o caso onde TrendHTF não é necessário
- v4a SOL 2025-H1 (RSI+width Sh=1.32) **pode ser questionado**: trend-only daria 1.96 (melhor) ou RSI puro daria ~0.61 (FAIL). Width está fazendo algo — mas talvez o que faz seja apenas "filtrar ruído", não "criar edge alinhado a direção".

**Não justifica redesenho do v4a agora** — ele já está active e PASSOU validação independente. Mas registra: futuras séries SOL 2025+ devem testar trend-only como alternativa primária, não como amplificador de width.

### Padrão 17 (novo, derivado)

**"Composição AND de filters cria edge novo apenas se ambas as pernas forem load-bearing **na mesma direção semântica**. Quando uma perna domina (carrega o edge sozinha), a outra é redundante (no melhor caso) ou ativamente prejudicial (no pior). Antes de propor composição, verificar empiricamente que cada perna isolada **falha** o gate — se alguma perna isolada passa, composição é overhead. Audit Gate B reformulado para composto: sem qualquer perna, combo deve cair para FAIL; ambas as remoções precisam quebrar."**

Implicação prática:
- Composição defende-se apenas como mecanismo de redução de overfitting quando cada perna é fraca isolada (sinergia clássica), não como amplificação de perna forte (caso CO).
- Próximas séries de composição precisam pré-registrar **ambas perna-isolada-FAIL** como condição necessária (não suficiente) para hipótese ser válida.

## Decisão

**Arquivar CO.** Sem promoção, sem manifest novo. Stack inalterado.

### O que documentar

1. CO Gate 1 PASS analítico (2/3) mas Gate 2+4 FAIL → NÃO promove.
2. Padrão 17: composição AND só vale se ambas pernas isoladas falham.
3. Reafirmação Padrão 15: lift sem load-bearing é red flag, mesmo com lift real.
4. Refinamento Padrão 14 + nota a v4a: width em SOL 2025-H1 é "filtro de ruído", não "amplificador direcional"; trend-only seria alternativa válida (Sh 1.96 vs 1.32) — mas v4a permanece ativo (validação independente PASS, não há bug).

## Consequências

### Imediatas
- Série CO arquivada Gate 1 PASS / Gate 2+4 FAIL (não-promoção decisional).
- Stack manifests inalterado: v2 + v3 + v4a + v4b ativos.
- Bridge AF↔bot **não postar** (signal-only, stack inalterado).
- Padrão 17 documentado.

### Pesquisa
- Composição AND **eliminada do menu padrão** sem audit Gate B reforçado pré-registrado.
- Próxima exploração TrendHTF: testar **trend-only mono-SOL como possível alternativa a v4a** (se passar Gate B vs v4a width-load-bearing, abre track v4a-trend). Não fazer agora — v4a já active e operacional.

### Próximas séries (atualizado pós-CO)

1. **CM — Cross-timeframe 4h** (versão reduzida 3 pilotos 2024-H2, único 4h disponível) — testa generalidade de **timeframe** com v3/v4 params. Risco gate trade≥30 conhecido.
2. **CN — Cross-asset DOT/AVAX/LINK** — bloqueada (datasets ausentes, sem tooling de ingest). Decisão deferida pra usuário sobre escrever ingest.
3. **CP (futuro)** — track v4a-trend SOL: trend-only vs width como filter primário, mono-SOL.

Recomendação implícita pós-CO: **CM** (próxima desta sessão), depois decisão sobre CN.

## Critério de sucesso desta ADR

1. CO marcada Gate 1 PASS analítico, Gate 2+4 FAIL, NÃO-promoção ✓
2. Padrão 17 (composição AND exige ambas pernas FAIL isoladas) formalizado ✓
3. Bridge não postado ✓
4. STATE.md atualizado (pendente — junto com CM)
5. Próxima série iniciada (CM)
