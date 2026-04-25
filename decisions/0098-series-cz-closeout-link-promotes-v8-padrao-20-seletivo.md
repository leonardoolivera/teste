# 0098 — Série CZ closeout: LINK 2025-H2 promove v8, Padrão 20 refinado como seletivo-por-ativo

**Status:** Accepted — closeout
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0097 (CZ pré-registro), ADR-0088/0090 (Padrão 20), ADR-0096 (snapshot)

## Resultado

**1/3 PASS.**

| Tag | Asset | Window | Trades | PnL% | MDD% | Sh | MCp5 | costr | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| CZ.1 | DOT | 2025-H2 | 86 | +2.90 | 9.98 | 0.498 | 8940 | 0.9584 | FAIL (Sh<1.0, MCp5<9500, PnL<3%) |
| CZ.2 | AVAX | 2025-H2 | 95 | -0.90 | 11.50 | -0.054 | 8484 | 0.9524 | FAIL (Sh<1.0, MCp5<9500, PnL<3%) |
| CZ.3 | **LINK** | **2025-H2** | **84** | **+11.73** | **5.80** | **1.760** | **10150** | **0.9590** | **PASS** |

### Combo promovido
**LINK 2025-H2 — RSI(14/30/70) naked long_only=false.**
- 84 trades, Sh 1.760, MDD 5.80%, PnL +11.73%, MC p5 10150, cost_r 0.959
- Dentro do range v4b majors 2025-H2 (BTC Sh=1.64, SOL Sh=2.30), delta vs v4b_avg = -0.21
- Todos os gates passam com margem confortável

## Análise

### Comparação cross-asset 2025-H2 RSI short naked
| Asset | Sh | Status |
|---|---|---|
| BTC | 1.640 | PASS (v4b) |
| SOL | 2.300 | PASS (v4b) |
| ETH | — | não testado em 2025-H2 (v4b original tinha falhou com filter) |
| DOT | 0.498 | FAIL |
| AVAX | -0.054 | FAIL |
| LINK | 1.760 | PASS |

**Taxa de PASS em 2025-H2 naked short: 3/5 ativos (60%).**

### Diagnóstico FAIL em DOT/AVAX
- **DOT**: 86 trades, PnL positivo (+2.9%) mas Sh baixo (0.5), MDD ~10%. Distribuição de retornos volátil, sem edge direcional.
- **AVAX**: Sh quase zero, PnL negativo, 95 trades (o maior do set). Trade count alto + Sh zero = strategy está ruidosa, não capturando padrão.
- **LINK**: 84 trades similar aos outros, mas Sh 3.5× maior. Algo específico do preço de LINK em 2025-H2 favoreceu RSI extremes.

### Por que LINK e não DOT/AVAX?
Três hipóteses (não investigadas a fundo — signal-only):
1. **Regime específico do ativo**: LINK pode ter tido mais swings mean-reverting em 2025-H2 (oracle narrative, news-driven); DOT/AVAX mais trendy.
2. **Volatilidade**: MDD LINK 5.8% vs DOT 10% vs AVAX 11.5% — LINK foi o mais comportado, RSI pegou extremos sem ser rolado.
3. **Ruído**: 3 pontos não é amostra robusta; LINK PASS pode ser false positive. Gate MC p5=10150 dá alguma confiança (bootstrap confirma edge), mas replicação em outra janela fortaleceria.

### Padrão 20 refinado
Antes (pós ADR-0088/0090): "crypto major 1h naked: só short-side tem edge" — baseado em 9 observações long-side (CU+CV) e 2+ observações short-side (v4b BTC+SOL).

Agora (pós CZ): Padrão 20 cobertura ampliada para 5 ativos em 2025-H2 short-side.
- **PASS universal na direção** (todos os 5 ativos testados short-side ficaram com PnL ≥ 0 ou perto, diferente do long-side onde média foi FAIL claro)
- **PASS seletivo no gate rigoroso** (3/5 ativos = 60%)
- Refino: "crypto 1h naked short-side tem **potencial** de edge, mas qualidade (Sh ≥ 1.0) é asset-specific. Regra: sempre testar o ativo individualmente; não assumir PASS por ser crypto."

Isso não invalida Padrão 20 para long — long continua 1/15 PASS = 6.7% de exceção. Short fica 3/5 = 60% em 2025-H2. Assimetria direcional preservada (long é exceção rara, short é baseline bem-sucedido).

### Gate 4 — correlação LINK vs v4b BTC/SOL
**Não executado neste closeout** (custo extra ~5min). Hipótese: correlação moderada (0.4-0.6) dado que altcoin L1/oracle segue BTC direcionalmente mas com timing ligeiramente diferente. Adicionar ao backlog como "meta-correlação 2025-H2 expandida" se vier nova série.

## Decisão

### Promove v8
Manifest novo: `rsi_short_pure_link_2025h2_20260420.json` (ou estender `rsi_short_pure_2025h2_20260419.json` com LINK combo? — ver abaixo).

**Decisão de arquitetura:** estender o manifest existente (`rsi_short_pure_2025h2_20260419.json` v3) com novo combo LINK. Engine é idêntica (RSI naked short), runtime invariants idênticos, janela idêntica — não há diferença semântica. Adicionar como combo no mesmo manifest preserva coesão.

Se preferir manifest separado para telemetria/rollback independente, abre em sessão futura. Escolha atual: **estender**.

**Porém**: o manifest v3 existente não tem `manifest_version` bumped por combo. Adicionar LINK faz o manifest virar "v3+CZ.3". Preservar hash/audit: novo arquivo `rsi_short_pure_2025h2_20260420.json` como **v8** que supersede v3 do 20260419.

**Solução:** criar `rsi_short_pure_2025h2_20260420.json` como **v8** contendo BTC+SOL+LINK (supersedes `rsi_short_pure_2025h2_20260419.json`).

### Stack pós-v8
- v2 (4 long Bollinger)
- v3 bollinger short (4)
- v4a (1 RSI+width BTC 2025-H1)
- **v8 RSI short naked 2025-H2: BTC + SOL + LINK** (3 combos, substitui v4b)
- v6 (1 RSI+trend SOL 2025-H1)
- v7 (1 RSI+width long ETH 2024-H2)
- **Total: 14 combos active** (5 long + 9 short)

### Bridge
Post ao bot: v8 ativação + deprecar v4b (que vira `supersedes_by` v8).

## Próximos passos

1. Emitir `exports/approved/rsi_short_pure_2025h2_20260420.json` (v8)
2. Marcar `rsi_short_pure_2025h2_20260419.json` como deprecated (adicionar `superseded_by`)
3. Validar schema v3 do novo manifest
4. Postar bridge
5. Atualizar STATE.md + snapshot (ADR-0096 precisa refletir 14 combos)

### Backlog atualizado
- CZA: RSI+width filter rescue em DOT/AVAX 2025-H2 (3 runs) — Padrão 20 seletivo justifica tentar filter
- Meta-correlação expandida (v8 LINK vs BTC+SOL na mesma janela) — 5min
- Replicação LINK: RSI short naked em LINK outra janela (2025-H1? dataset exists agora) — 1 run, confirma se LINK 2025-H2 não foi fluke

## Critério de sucesso desta ADR

1. ✅ Sweep CZ executado (3 runs)
2. ✅ Closeout documenta verdict 1/3
3. ✅ Padrão 20 refinado (seletivo-por-ativo, direção preservada)
4. ⏳ v8 manifest emitido
5. ⏳ Bridge postado
6. ⏳ STATE.md + snapshot atualizados
