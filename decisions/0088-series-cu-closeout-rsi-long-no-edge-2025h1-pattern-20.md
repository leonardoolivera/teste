# 0088 — Série CU closeout: RSI long FAIL 0/3 cross-asset 2025-H1 + Padrão 20 (assimetria direcional do chop)

**Status:** Accepted — refutação total, novo padrão metodológico
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0087 (pré-registro CU), ADR-0086 (CR closeout), Padrão 14 (asset-específico), todos manifests short ativos (v3/v4a/v4b/v6)

## Resultado

| Tag | Asset | Trades | PnL% | MDD% | Sharpe | MC p5 | cost_r | Verdict |
|---|---|---:|---:|---:|---:|---:|---:|---|
| CU.1 | BTC 2025-H1 | 58 | +1.67 | 2.50 | **+0.829** | 9782 | 0.9695 | **FAIL** (Sh, PnL) |
| CU.2 | ETH 2025-H1 | 68 | −1.91 | 5.70 | **−0.535** | 9079 | 0.9636 | **FAIL** (Sh, MCp5, PnL) |
| CU.3 | SOL 2025-H1 | 70 | +0.10 | 7.92 | **+0.074** | 8891 | 0.9635 | **FAIL** (Sh, MCp5, PnL) |

**PASS = 0/3.**

### Cross-check long vs short (mesma janela mesmo ativo)

| Asset | Long Sh (CU) | Short ref | Short Sh | Delta |
|---|---:|---|---:|---:|
| BTC | 0.829 | v4a width | 1.688 | **−0.859** |
| ETH | −0.535 | (sem incumbente) | — | n/a |
| SOL | 0.074 | v6 trend | 1.958 | **−1.884** |

**Short domina long em todos casos com incumbente.** ETH long é o único negativo absoluto.

## Avaliação dos gates pré-registrados

### Gate 1 (≥1/3 PASS): **FAIL 0/3**
Nenhum combo Sh≥1.0. BTC chega a 0.83 (próximo mas insuficiente).

### Gate 2 (PnL>3%): **FAIL 0/3**
Maior PnL é BTC +1.67% (após 6 meses). ETH negativo (−1.91%). SOL nulo (+0.10%).

### Gate 3 (Promoção): **BLOQUEADA 0/3**
Sem PASS Gate 1+2, sem candidatos. Nenhum manifest v7 emitido.

### Gate 4 (cross-check, descritivo): **assimetria confirmada**
Em todos casos com referência, short Sh > long Sh por margem grande (≥0.86 BTC, ≥1.88 SOL). **Chop 2025-H1 é direcionalmente short-favored.**

## Interpretação

Hipótese refutada. RSI long(14/30/70) **não tem edge** em chop 2025-H1 cross-asset.

**Por quê o chop é assimetricamente short?** Hipóteses:
1. **Bias de pesquisa convergente acidental:** todas séries CH/CK/CO/CP/CR/CR usaram short → estudei a perna que funciona, ignorando a que não. CU agora confirma que long realmente *não funciona* aqui — não foi viés.
2. **Microestrutura crypto 2025-H1:** chop 2025-H1 nominalmente "lateral" mas com **drift direcional descendente** (≥3 de 4 folds com closing baixo > opening alto em todos ativos). RSI long compra oversold em downtrend macro = "facas caindo", exit RSI≥50 raro chegar.
3. **Distribuição de retorno assimétrica em alts:** ETH/SOL têm crashes mais pronunciados que rallies em chop — short captura crash, long é stop-out implícito.

Não promove novo padrão "chop is short-favored" porque seria over-fit a 1 janela. Mas formaliza padrão **metodológico** sobre como interpretar refutação cross-direcional.

## Padrão 20 (novo, metodológico, ADR-0088)

**"Refutação cross-asset direcional (long FAIL 0/N enquanto short PASS) confirma que viés direcional do stack reflete edge real, não viés de pesquisa. Quando série existente é toda em uma direção, vale rodar a direção oposta como naked baseline mínimo (1 série, ~3 runs) para validar assimetria. Se long também passar, descobrimos diversificação. Se long FAIL, eliminamos hipótese 'só estudamos um lado'."**

Implicação prática:
- Antes de v7+, não precisa retestar long (CU já refutou para 2025-H1; janelas diferentes podem reabrir hipótese).
- Se 2024-H2 ou 2025-H2 vier com nova série, considerar incluir long-naked como Gate 0 informacional.
- Stack permanece intencionalmente short-heavy — agora *empiricamente* justificado.

## Decisão

### Não-promoção CU

Stack inalterado. v7 não emitido. Bridge AF↔bot **não postado** (signal-only).

### Documentar assimetria como insight de pesquisa, não padrão técnico

Padrão 20 é metodológico (sobre como pesquisar), não sobre como construir manifests. Lista de padrões atualizada (cumulativo desde Padrão 1).

## Padrões cumulativos (snapshot pós-CU)

1-15: ver ADRs anteriores (0042–0077)
16: ADR-0077 — threshold canônico = scope, não fragilidade
17: ADR-0079 — composição AND requer pernas FAIL isoladas
18: ADR-0081 — cross-timeframe exige matriz equivalente (fraco/metodológico)
19: ADR-0083 — Gate B múltiplas baselines (filter-vs-naked ≠ filter-vs-incumbente)
**20: ADR-0088 — refutação cross-direcional confirma assimetria do stack**

## Consequências

### Imediatas
- CU arquivado. Stack inalterado.
- STATE.md atualizado (próximo).
- Bridge não postado.

### Pesquisa futura
- **Próxima janela com nova série:** considerar long-naked como Gate 0 informacional (1 run extra cross-asset).
- **Cross-period long:** poderia testar long em 2025-H2 (regime misto, não só chop). Se long passar em 2025-H2, abre v7 long-side cross-period. Mas baixa prioridade — 2025-H2 mid year teve recuperação; chance de RSI long pegar reversão melhor.
- **Long em 2024-H2 (bull mkt):** RSI long em uptrend é tese diferente (compra oversold dentro de uptrend). Pode ter edge. Hipótese para futura série CV.

### Próximas séries candidatas

1. **CV — RSI long 2024-H2 + 2025-H2** (cross-period long, 6 runs). Hipótese: long funciona em janelas com drift positivo, refutado em chop puro 2025-H1.
2. **Pausar pesquisa direcional** — stack short maduro (8 combos), passar para meta-análise (correlação entre combos do stack, hedge ratios) ou validação operacional (paper-trade v6 e v4b).
3. **Ingest pendente** (CN/CM-completo) — bloqueia roadmaps cross-asset alts e cross-timeframe.

**Recomendação:** **CV** se quer continuar pesquisa offline. Pausa-paper se quer começar a observar comportamento dos combos novos (v4b 1 dia, v6 0 dias em paper).

## Critério de sucesso desta ADR

1. CU fechado ✓
2. Gate verdicts documentados ✓
3. Padrão 20 formalizado (metodológico) ✓
4. Cross-check long-vs-short documentado ✓
5. STATE.md atualizado (próximo)
6. Próxima série recomendada ✓
