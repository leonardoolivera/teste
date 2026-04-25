# 0071 — Série CI closeout: Donchian short + width 300 FAIL 0/9 — Padrão 10 é específico mean-rev

**Status:** Accepted — série arquivada com FAIL total
**Date:** 2026-04-19
**Deciders:** Usuário + agente (AF)
**Relates to:** ADR-0070 (pré-registro CI), ADR-0057 (CG closeout PASS), ADR-0062 (CH closeout PASS), ADR-0040 (CA Donchian long FAIL)

## Resultado

**PASS count: 0/9.** Gate pré-registrado em ADR-0070 exigia ≥3/9. Série **FAIL total**.

| Tag | Asset | Janela | Trades | PnL% | MDD% | Sharpe | MC p5 | cost_r | Verdict |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| CI.1 | BTC | 2024-H2 | 80 | −5.53 | 4.83 | −2.210 | 8902 | 0.9514 | FAIL (Sh, MCp5) |
| CI.2 | ETH | 2024-H2 | 105 | −2.65 | 5.42 | −0.720 | 8951 | 0.9462 | FAIL (Sh, MCp5, costr) |
| CI.3 | SOL | 2024-H2 | 149 | −14.60 | 8.32 | −2.770 | 7289 | 0.9099 | FAIL (Sh, MCp5, costr) |
| CI.4 | BTC | 2025-H1 | 62 | +0.51 | 3.33 | +0.209 | 9551 | 0.9610 | FAIL (Sh) |
| CI.5 | ETH | 2025-H1 | 114 | +0.08 | 6.25 | +0.055 | 8366 | 0.9361 | FAIL (Sh, MCp5, costr) |
| CI.6 | SOL | 2025-H1 | 152 | −16.98 | 11.18 | −2.546 | 6444 | 0.9154 | FAIL (Sh, MCp5, costr) |
| CI.7 | BTC | 2025-H2 | 68 | −4.74 | 4.06 | −2.474 | 9080 | 0.9667 | FAIL (Sh, MCp5) |
| CI.8 | ETH | 2025-H2 | 103 | −1.26 | 5.41 | −0.288 | 8874 | 0.9458 | FAIL (Sh, MCp5, costr) |
| CI.9 | SOL | 2025-H2 | 135 | −8.24 | 6.95 | −1.580 | 7899 | 0.9180 | FAIL (Sh, MCp5, costr) |

Dados crus: `exports/diag/series_ci_summary.json`.

## Avaliação dos gates pré-registrados

- **Gate 1 (≥3/9 PASS):** 0/9 → **FAIL forte**. Nenhum combo nem perto de Sharpe 1.0 — máximo é CI.4 BTC 2025-H1 com Sh=0.21
- **Gate 2 (lift cost_r vs CA sem filter):** N/A — gate ficou inviável de avaliar diretamente porque CA usou ATR gate, não no-filter; mas SOL CI.3/6/9 cost_r 0.91-0.92 vs CA SOL 0.95-0.97 mostra **degradação** de cost_r (filter aumenta custo sem aumentar edge). **Refuta lift.**
- **Gate 3 (preservação edge ≥6/9 com Sh>0):** 2/9 (apenas CI.4 +0.21 e CI.5 +0.06, ambos quase-zero) → **FAIL**
- **Gate 4 (falsificacionista 2024-H2 ≤1/3):** 0/3 PASS → trivialmente PASS (mas vazio de significado quando série inteira é 0/9)
- **Gate 5 (audit Gate B):** N/A — só aplicável se Gate 1 PASS

**Veredicto overall: FAIL refutador.** Hipótese H-especificidade-mean-rev (alternativa em ADR-0070) confirmada.

## Interpretação

### Por que filter width não compõe com Donchian short

1. **Direção do edge é estruturalmente oposta.** Mean-reversion (Bollinger/RSI short) entra contra o move recente — vendendo após pump rápido, esperando reversão. Width 300 filtra ambientes onde a banda já abriu (volatilidade alta sustentada) — nesses, o pump é mais provável de ser exaustão. Padrão 10 funciona pq o filter seleciona **regime favorável ao mean-rev**.
   
   Donchian short entra **a favor do move recente** — vendendo no rompimento da mínima 10-bar. Width 300 não está selecionando regime favorável a breakout; está apenas filtrando ambiente seco. Em ambiente seco, breakouts tendem a ser falsos (whipsaw curto). Filter está semanticamente desalinhado com a direção do edge.

2. **Trade count alto + PnL ruim = death by friction.** SOL CI.3/6/9 têm 135-152 trades cada (vs CH SOL 73-94). Donchian dispara mais que RSI no mesmo período — reverse-on-signal frequente, double cost (ADR-0012). Cost_r cai pra 0.91-0.92 (gate 0.95). Filter não reduz trade count o suficiente; aumenta-o em SOL inclusive.

3. **Sharpe quase-zero em BTC/ETH 2025-H1 ≠ edge fraco; é indecisão.** CI.4 e CI.5 têm Sh ≈ 0 com PnL ≈ 0 — strategy tá basicamente neutra após custos. Sem custos seria positivo magro; com custos colapsa. Edge bruto insuficiente pra sustentar mesmo um filter "neutro".

### Padrão 10 reformulado (era genérico mean-rev, agora explícito)

Antes (após CG+CH): "filter composicional parametrizado ao regime eleva edge borderline pra passer" — implicitamente assumindo qualquer família de estratégia.

Agora (Padrão 13, novo): **"filter de width só compõe com estratégias mean-reversion. Para breakout, width filtra contra a direção do edge — bloqueia ambientes secos onde breakouts falham, mas o cardinal de breakouts vencedores também cai. Width não é universal; é específico ao regime de payoff que a estratégia explora."**

Padrão 13 é refinamento natural do Padrão 12 (filter regime-específico): agora também direção-de-payoff-específico.

### Comparação CI vs CA (Donchian long)

| Métrica | CA (long, ATR gate) | CI (short, width 300) |
|---|---|---|
| PASS | 2/10 (mas só 2023-H2) | 0/9 |
| Trade count médio | 67 | 109 |
| Sharpe melhor | +2.14 (2023-H2) | +0.21 (BTC 2025-H1) |
| SOL pior | −3.33 | −2.77 (PnL −16.98%) |

Ambos formato Donchian falham cross-period. CA tinha pelo menos uma janela boa; CI nem isso. **Conclusão prática:** Donchian 1h crypto spot, qualquer direção, qualquer filter testado até agora — não tem edge estável. Próximas séries não devem testar Donchian no formato atual sem mudar pelo menos um eixo estrutural (timeframe, asset class, ou direção de filter inverso).

## Consequências

### Imediatas
- Série CI arquivada. `results/validation/ci-donchian-*` permanecem como registro; não entram em manifest.
- Stack manifests inalterado: v2 + v3 + v4a + v4b ativos.
- Bridge AF↔bot **não postar** (signal-only — FAIL não muda decisão do bot).

### Conhecimento ganho
- **Padrão 13 documentado:** filter composicional é payoff-direction-específico, não apenas regime-específico. Filtros futuros precisam justificar alinhamento semântico com direção do edge antes da série, não depois.
- **Donchian crypto 1h excluído** do formato CG/CH/CI (espelho 9 pilotos, mesmo filter, mesma DS). Não bloqueia testar Donchian 4h+, ou Donchian com filter direcional (ex.: SMA htf), ou Donchian em outras asset classes.

### Próxima série
Livre. Candidatos remanescentes (com Padrão 13 aplicado):
1. **RSI thresholds alternativos (9/25/75 ou 21/35/65)** — varia parametrização dentro de família já validada. Risco: overfit ao mesmo edge.
2. **Cross-timeframe 4h** — replica v3/v4 em 4h. Esperado: menos trades, talvez Sharpe maior por barra mas trade count abaixo do gate.
3. **Volume/orderflow filter** em RSI/Bollinger short — testa se filter alternativo lift mean-rev edge em janelas onde width não basta (CH.1/CH.2/CH.3 2024-H2 FAIL).
4. **Cross-asset** (DOT/AVAX/LINK) com manifest v4a/v4b params — testa generalidade asset-cross em vez de regime-cross.

Recomendação implícita do agente: **#3 (volume filter)** — explora gap conhecido (2024-H2 RSI short FAIL) e é compatível com Padrão 13 (volume é proxy de pressão direcional, alinhado com payoff de mean-rev).

## Critério de sucesso desta ADR

1. CI marcada FAIL e arquivada ✓
2. Padrão 13 formalizado e justificado ✓
3. Bridge AF↔bot não postado (regra signal-only) ✓
4. STATE.md atualizado ✓
5. Próximos candidatos enumerados com recomendação
