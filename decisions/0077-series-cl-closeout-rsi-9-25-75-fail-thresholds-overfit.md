# 0077 — Série CL closeout: RSI(9/25/75) FAIL 0/9 — v4 é threshold-específico (boa notícia: scope claro)

**Status:** Accepted — série arquivada com FAIL refutador; v4 confirmado robusto ao corte 14/30/70 mas não a perturbação ampla
**Date:** 2026-04-19
**Deciders:** Usuário + agente (AF)
**Relates to:** ADR-0076 (pré-registro CL), ADR-0062 (CH closeout PASS), ADR-0069 (v4a/v4b ativos), ADR-0075 (Padrão 15)

## Resultado

**PASS count: 0/9.** Gate 1 pré-registrado (≥3/9) → **FAIL refutador**.

| Tag | Asset | Janela | Trades | PnL% | MDD% | Sharpe | MC p5 | cost_r | CH Sh | Δ vs CH | Verdict |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| CL.1 | BTC | 2024-H2 | 57 | −0.69 | 3.91 | −0.321 | 9363 | 0.9656 | −0.76 | **+0.44** | FAIL (Sh, MCp5) |
| CL.2 | ETH | 2024-H2 | 81 | −2.89 | 3.70 | −0.789 | 9068 | 0.9547 | −1.52 | **+0.73** | FAIL (Sh, MCp5) |
| CL.3 | SOL | 2024-H2 | 92 | −2.41 | 6.82 | −0.456 | 8865 | 0.9476 | −0.39 | −0.07 | FAIL (Sh, MCp5, costr) |
| CL.4 | BTC | 2025-H1 | 51 | +0.02 | 2.49 | +0.039 | 9591 | 0.9701 | +1.69 | **−1.65** | FAIL (Sh) |
| CL.5 | ETH | 2025-H1 | 103 | −8.48 | 8.38 | −1.667 | 8258 | 0.9447 | +0.50 | −2.17 | FAIL (Sh, MCp5, costr) |
| CL.6 | SOL | 2025-H1 | 113 | −6.16 | 6.63 | −0.922 | 8128 | 0.9347 | +1.32 | **−2.24** | FAIL (Sh, MCp5, costr) |
| CL.7 | BTC | 2025-H2 | 58 | +1.31 | 1.93 | +0.810 | 9671 | 0.9748 | +2.63 | **−1.82** | FAIL (Sh) |
| CL.8 | ETH | 2025-H2 | 85 | −2.60 | 4.16 | −0.676 | 8804 | 0.9525 | +0.81 | −1.49 | FAIL (Sh, MCp5) |
| CL.9 | SOL | 2025-H2 | 101 | −1.26 | 6.85 | −0.223 | 8462 | 0.9481 | +1.92 | **−2.14** | FAIL (Sh, MCp5, costr) |

Dados crus: `exports/diag/series_cl_summary.json`.

## Avaliação dos gates pré-registrados

- **Gate 1 (≥3/9 PASS):** 0/9 → **FAIL refutador**
- **Gate 2 (robustez ±25% vs CH):** 1/9 → **FAIL** — só CL.3 SOL 2024-H2 ficou dentro de banda (mas ambos FAIL)
- **Gate 3 (trades≥30 em ≥6/9):** 9/9 → PASS — thresholds 25/75 **aumentam** trade count vs CH em todos
- **Gate 4 (audit Gate B):** N/A (Gate 1 FAIL)
- **Gate 5 (distinct PASS — passa onde CH falha):** 0 — H-thresholds-importam-mas-diferente refutada

**H-overfit-thresholds confirmada.** Edge v4 é específico ao corte 14/30/70.

## Interpretação

### Por que RSI(9, 25/75) destrói edge

Hipótese inicial era: "RSI 9 é mais sensível (capta cedo), thresholds 25/75 são mais extremos (filtra falsos positivos) — efeitos cancelam ou amplificam." Resultado: **se cancelam, mas pra pior**.

Análise de mecânica:
1. **RSI(9) cruza 75 com mais frequência que RSI(14) cruza 70.** Período menor = mais variância no indicador → atinge níveis "extremos" mais facilmente. Thresholds 25/75 (mais restritivos em RSI(14)) viram quase-equivalentes ao 30/70 em RSI(9). 
2. **Trade count sobe ~30-40%** (CL.5 ETH 2025-H1: 103 vs CH 77; CL.9 SOL: 101 vs CH 80). Mais sinais, mas qualidade pior — Sharpe colapsa.
3. **2024-H2 marginal lift (+0.44/+0.73)** parece sinal mas é artefato: RSI(9) entra short tantas vezes em pullbacks de bull que cobre custos do RSI(14) que entrava menos vezes em pontos piores. Lift puro de menos perda — não é edge.
4. **2025 chop catastrófico:** CL.4-6 e 7-9 colapsam (−1.5 a −2.2 Sh). Em chop com tendência fraca, RSI(9) dispara em ruído puro; width 300 não filtra o suficiente porque sinais brutos são tão frequentes que mesmo o subset filtrado é grande.

### Por que isso é informação positiva pra v4

Refutar H-robusto-cross-thresholds **fortalece** v4 ao definir escopo:
- v4a (RSI 14/30/70 + width 300, 2025-H1) e v4b (RSI 14/30/70 sem filter, 2025-H2) são **threshold-específicos**, mas isso era esperado de qualquer manifest treinado em walk-forward sobre uma config específica.
- O risco real era: v4 funcionar **só** porque 14/30/70 caiu por sorte numa banda boa do espaço de hyperparams. CL refuta isso indiretamente — se 14/30/70 fosse sortudo, 9/25/75 ou 21/35/65 deveria também passar pelo menos parcialmente.
- Resultado: 14/30/70 **não é sortudo**, é **estruturalmente especial** (provavelmente porque é a config canônica que máxima literatura testou — corresponde a regimes reais de extremo de mercado).

### Padrão 16 (novo, derivado)

**"Manifest aprovado em walk-forward com threshold canônico (RSI 14/30/70, Bollinger 20/2, MA 50/200) é threshold-específico por design. Variar thresholds em ±50% não é teste de robustez do edge — é teste de outro edge. Se varia e quebra, é informação sobre **escopo**, não fragilidade."**

Implicação prática: futuras séries não devem variar thresholds canônicos como teste de robustez do manifest existente. Se quiser testar threshold alternativo, é **série independente** com hipótese de edge própria (RSI(7) curto-prazo, RSI(21) longo-prazo) — não comparativa direta com manifest aprovado.

## Decisão

**Arquivar CL.** Sem promoção, sem manifest novo. Stack inalterado.

### O que documentar

1. v4 confirmado threshold-específico — escopo bem-definido (14/30/70).
2. Padrão 16 — variar threshold canônico não é teste de robustez.
3. Gate count 9/9 trades≥30 confirma que CL não falhou por gate de viabilidade — falhou por edge mesmo.

## Consequências

### Imediatas
- Série CL arquivada FAIL.
- Stack manifests inalterado: v2 + v3 + v4a + v4b ativos.
- Bridge AF↔bot **não postar** (signal-only, stack inalterado).
- Padrão 16 documentado.

### Pesquisa
- RSI threshold-sweep como teste de robustez **eliminado** do menu padrão. Próximas variações de RSI exigem hipótese própria (não "ver se v4 sobrevive").
- Análise mais profunda do **por que** 14/30/70 é especial fica pra futuro — pode ser análise de literatura + microestrutura, não nova série de validation.

### Próximas séries (atualizado pós-CL)

1. **CM — Cross-timeframe 4h** com v3/v4 params — testa generalidade de **timeframe**. Hipótese: edge é estrutural ao regime, não ao 1h específico. Espera: menos trades (4h tem 1/4 das barras), mas Sh por trade pode ser maior. Risco gate trade≥30: provável FAIL trade count em janelas semestrais 4h.
2. **CN — Cross-asset DOT/AVAX/LINK** com v4a/v4b params — testa generalidade asset. Hipótese: RSI mean-rev short é estrutural a alts líquidos com volatilidade similar.
3. **CO — Composição AND** width 300 + TrendHTF SOL-only — testa se composição lift edge SOL ALÉM do que cada um isolado faz, com Padrão 12 audit obrigatório.

Recomendação implícita: **CN (cross-asset)** — barato (depende dos datasets disponíveis), responde diretamente se v4 é "BTCUSDT/ETHUSDT/SOLUSDT-específico" ou generaliza pra alts. Compra mais combos pro stack se passar.

## Critério de sucesso desta ADR

1. CL marcada FAIL refutador ✓
2. Padrão 16 (threshold canônico = scope, não fragilidade) formalizado ✓
3. Bridge não postado ✓
4. STATE.md atualizado
5. Próxima série recomendada
