# 0081 — Série CM closeout: 4h cross-timeframe INCONCLUSIVO — confound de janela

**Status:** Accepted — FAIL inconclusivo (gate 1 FAIL mas hipótese não testada limpa)
**Date:** 2026-04-19
**Deciders:** Usuário + agente (AF)
**Relates to:** ADR-0080 (pré-registro CM), ADR-0077 (CL closeout — Padrão 16), ADR-0069 (v4a/v4b ativos)

## Resultado

3 runs 4h, janela única 2024-H2 (única disponível processada).

| Tag | Asset | Janela | Trades | PnL% | MDD% | Sharpe | MC p5 | cost_r | Verdict |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| CM.1 | BTC | 2024-H2 4h | 14 | −11.58 | 12.74 | −3.177 | 8054 | 0.9886 | FAIL (trades, Sh, MCp5) |
| CM.2 | ETH | 2024-H2 4h | 11 | −13.46 | 16.13 | −3.017 | 8775 | 0.9907 | FAIL (trades, Sh, MCp5) |
| CM.3 | SOL | 2024-H2 4h | 13 |  −7.42 | 10.48 | −1.307 | 9701 | 0.9907 | FAIL (trades, Sh) |

Dados crus: `exports/diag/series_cm_summary.json`.

## Avaliação dos gates pré-registrados

- **Gate 1 (≥1/3 PASS):** 0/3 → **FAIL**
- **Gate 2 (trades≥30 em ≥2/3):** 0/3 → **FAIL** — trade counts 11-14 em todos
- **Gate 3 (Sh 4h ≥ Sh 1h em ≥1/3):** 0/3 — todos pioram vs 1h (já compromised na 1h também)
- **Gate 4 (não-promoção):** N/A (Gate 1 FAIL)

## Interpretação

### Por que resultado é INCONCLUSIVO, não REFUTADOR

Pré-registro ADR-0080 já antecipava o risco — janela única 2024-H2 confunde duas coisas:

1. **Janela 2024-H2 é universalmente ruim para RSI short cripto.** Em 1h também: CK.1 SOL 2024-H2 Sh=−1.02; CH.3 SOL 2024-H2 Sh=−0.39; ETH/BTC 2024-H2 1h sem filter não têm PASS arquivado. Bull market H2 destrói RSI-short structurally.
2. **4h reduz amostra a 1/4 das barras.** ~1100 barras vs ~4400. Trade count cai de 30-90 (1h) para 11-14 (4h) — gate 30 era impossível em janela única.

CM 0/3 não distingue:
- "Edge 1h NÃO generaliza para 4h" (refutação real do cross-timeframe)
- "Janela 2024-H2 é ruim em qualquer timeframe" (confirmação de janela ruim, não diz nada sobre timeframe)
- "Sample 4h pequeno demais" (problema metodológico, não de edge)

**Resultado é dominado pelo confound — não é evidência refutadora.** A pergunta "edge generaliza pra 4h?" segue **não respondida**.

### Por que isso é ainda informação útil

1. **Documenta limitação do dataset:** apenas 1 janela 4h no repo. Para responder cross-timeframe sério, precisa ingerir 2024-H1, 2025-H1, 2025-H2 4h (mesma matriz CH/CL).
2. **Confirma viés esperado:** janela 2024-H2 é o **pior caso** para RSI short — não surpresa que 4h também colapse. Útil para calibrar expectativas de séries futuras nessa janela.
3. **Trade count gate 30 incompatível com 4h em janela semestral.** Próxima série 4h pode considerar:
   - Janela anual (2024-completo, 2025-completo) → ~2200 barras → potencial trade count ~50-70
   - Manter janela semestral mas relaxar gate trade count para 4h (ex: ≥15)
   - Ambos exigem decisão metodológica explícita pré-registrada

### Padrão 18 (novo, derivado, fraco)

**"Cross-timeframe sweep com janela única confunde edge generalization com janela específica. Não-resposta. Para testar generalidade de timeframe, é necessário **mesma matriz de janelas** que validou o timeframe original. Sample reduzido 1/N (4h vs 1h: 1/4) exige pelo menos N janelas para amostra equivalente."**

Implicação prática:
- Cross-timeframe **honesto** exige ingest de N janelas no novo timeframe antes de rodar série.
- Atalho com 1 janela é metodologicamente fraco — gera resultado inconclusivo independente do que aconteça.

Padrão é "fraco" porque é mais uma **lição metodológica** que padrão estrutural sobre estratégias — fica como aviso pra próximas séries cross-timeframe.

## Decisão

**Arquivar CM como inconclusivo.** Sem promoção. Stack inalterado.

### Pendência registrada (não auto-execução)

Para responder cross-timeframe de verdade:
1. Ingerir BTC/ETH/SOL 4h: 2024-H1, 2025-H1, 2025-H2 (3 janelas × 3 ativos = 9 datasets faltantes)
2. Decidir tooling de ingest (não existe atualmente em `tools/`)
3. Re-rodar Série CM-completo (9 pilotos espelho CH/CL) com gate trade count ajustado a 4h (sugestão: ≥15-20)

Esta pendência fica deferida ao usuário — mesma decisão que CN cross-asset DOT/AVAX/LINK. Ambas dependem de tooling de ingest novo.

## Consequências

### Imediatas
- Série CM arquivada inconclusiva.
- Stack manifests inalterado: v2 + v3 + v4a + v4b ativos.
- Bridge AF↔bot **não postar** (signal-only, stack inalterado).
- Padrão 18 (metodológico fraco) documentado.

### Pesquisa
- Cross-timeframe e cross-asset **ambos bloqueados** pela mesma pendência: tooling de ingest binance_vision para datasets faltantes.
- Próximas séries factíveis sem novo ingest: variação de params dentro família validada (ex: BollingerWidth + ATRRegime composto SOL — análogo CO mas com filters não-direcionais), ou nova hipótese de filter usando dados existentes.

### Próximas séries (atualizado pós-CM)

1. **(Bloqueada) CN — Cross-asset DOT/AVAX/LINK** — depende de ingest.
2. **(Bloqueada) CM-completo — Cross-timeframe 4h 9 pilotos** — depende de ingest.
3. **CP — TrendHTF mono-SOL como filter primário (alternativa a v4a)** — usa dados existentes; testa se trend-only Sh=1.96 (CO.2 audit) generaliza pra 2024-H2/2025-H2 (já temos CK.1=−1.02, CK.3=2.71). Pré-registrar com Gate B contra v4a width. Próximo candidato natural.
4. **CQ — Composição OR width|trend SOL** — análogo CO mas com OR em vez de AND. Hipótese fraca (OR não restringe sample, só relaxa).

Recomendação implícita: **CP** (testa v4a-trend como variante a v4a-width, dados existentes) ou **decisão usuário sobre escrever ingest** pra desbloquear CN/CM-completo.

## Critério de sucesso desta ADR

1. CM marcado inconclusivo com confound documentado ✓
2. Padrão 18 (cross-timeframe exige mesma matriz) documentado ✓
3. Pendência ingest registrada (não auto-execução) ✓
4. Bridge não postado ✓
5. STATE.md atualizado (próximo)
