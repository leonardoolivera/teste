# 0171 — Série KE Fase 1 closeout: Keltner naked refutado, Padrão 41 dispara novamente

**Status:** Accepted — Keltner naked arquivado em Fase 1. Fase 2 bloqueada.
**Date:** 2026-04-20
**Deciders:** Usuário (piloto automático) + agente
**Relates to:** ADR-0169 (assessment), ADR-0170 (pré-reg), Padrão 41

## Resultado Fase 1

| Tag | Combo | Trades | Sh | Baseline BB | Lift | PnL% |
|---|---|---:|---:|---:|---:|---:|
| KE.1 | BTC Keltner 20/14/2.0 short | 49 | 0.06 | 0.85 | **-0.79** | 0.06 |
| KE.2 | ETH Keltner 20/14/2.0 short | 48 | **2.40** | 0.68 | **+1.72** | 14.72 |
| KE.3 | SOL Keltner 20/14/2.0 short | 46 | 0.62 | 1.44 | -0.82 | 3.75 |

**1/3 Sh ≥ 1.5** → **Padrão 41 (signal divergente janela-específica)**. Gate pré-registrado (≥2/3) NÃO passa. Fase 2 bloqueada.

## Interpretação

### ETH outlier replica padrão de DE.2b

DE.2b (ADR-0168, RSI+trend_htf 1d ETH) também deu Sh=1.55 isolado enquanto BTC/SOL falharam. Mesmo comportamento agora em Keltner naked — **ETH 2025-H1** parece ser uma janela onde múltiplos signals mean-reversion discretos funcionam isoladamente, mas não generaliza.

Hipótese: ETH teve downtrend prolongado $3700→$2000 com múltiplos micro-reversions, onde qualquer signal de banda superior rompida → short captura o downleg. Não é edge de engine; é edge de **regime assumido pela janela**.

### Keltner não diferencia de BB em BTC/SOL

Prior em ADR-0170 estimou corr Keltner↔BB ~+0.7. Aqui BTC e SOL dão **Sh mais baixo** que BB naked, indicando que:
- ATR vs stdev não adiciona robustez em BTC/SOL 1h (vol é persistente, não outlier-driven)
- EMA(20) vs SMA(20) como center-line não move muito
- Thresholds em ATR×2 vs num_std×2 dão widths similares na maior parte do tempo

Keltner é **estritamente pior** que BB em 2/3 assets → não é dimensão nova, é variante degradada.

### Entrada curta ETH não promove porque Padrão 41 é regra dura

Mesmo que ETH Sh=2.40 seja altíssimo e trade count (48) seja válido, **1/3 não promove**. Padrão 41 foi explicitamente formulado para bloquear este tipo de outlier.

## Decisão

- **Arquivar Keltner naked** (ADR-0170). Não prosseguir com Fase 2/3.
- **Manter código Keltner** em `src/alpha_forge/strategies/families/keltner/` — foi implementado, testado (21/21), e fica disponível para futuras combinações (ex. Keltner + filter, Keltner com params alternativos). Custo de manter é zero; custo de re-implementar se precisar depois seria ~2-4h.
- Nenhuma edição de manifest.
- Stack permanece 13 combos.

## Lições

### Padrão 41 cria teto estrutural para engines vanilla

Após Donchian (CY), MACX (CZ6-9), trend_htf 1d (DE), e agora Keltner — **todo engine novo vanilla cross-asset 1h 2025-H1 bate em Padrão 41 no primeiro teste**. ETH sempre é o outlier. Isso sugere que ETH 2025-H1 é **janela peculiar**, não que os engines são ruins em geral.

### Candidato Padrão 45 (informal — não formalizar sem replicação adicional)

**"Quando um engine novo bate gate em ETH 2025-H1 mas falha em BTC/SOL, a hipótese default é regime-específico da janela ETH (downtrend persistente), não edge do engine. Gate 1/3 = refutação em engines naked."**

Requer mais uma replicação (ex. zscore naked) para formalizar.

## Implicação para piloto automático

Caminho para bot via novos engines vanilla está **exaurido em 2025-H1**. Opções remanescentes:

1. **Keltner + filter composition** (bollinger_width, trend_htf) — pode destravar BTC/SOL se filter corta lixo
2. **Zscore MR** (Candidato A) — ainda mais próximo de BB matematicamente; prior pessimista
3. **Testar Keltner em outras janelas** (2024-H1/H2, 2025-H2) — pode ser que ETH-outlier é efeito-2025H1 generalizado, e em outras janelas 2+/3 passa
4. **Parar frente "novos engines", abrir frente "re-test em janelas alternativas"** — explora se combos existentes no stack também se refinam

Recomendo Opção 3 + 1 paralelas. Próximo ADR de escopo.

## Não-alvo

- Não implementar zscore agora (prior muito ruim, ver ADR-0169)
- Não mexer em manifest
- Não revisar Padrão 41 (regra é clara)

## Ação executada

- ✅ ADR-0170 pré-reg
- ✅ Keltner engine implementado (21/21 testes)
- ✅ Wiring CLI completo
- ✅ 3 runs KE.1-3 executados
- ✅ ADR-0171 closeout
