# 0075 — Série CK closeout: TrendHTF mono-SOL é amplificador, não load-bearing — não promover

**Status:** Accepted — análise concluída, decisão de NÃO promover apesar de Sharpe lift confirmado
**Date:** 2026-04-19
**Deciders:** Usuário + agente (AF)
**Relates to:** ADR-0074 (pré-registro CK), ADR-0073 (CJ closeout, Padrão 14), ADR-0068 (Padrão 12 audit Gate B), ADR-0069 (v4a/v4b ativos)

## Resultado

Re-leitura mono-SOL dos runs CJ.3, CJ.6, CJ.9 (sem novos runs).

| Tag | Janela | Trades | Sharpe | MC p5 | cost_r | Gate 1 | CH SOL Sh | Δ vs CH | v4 SOL Sh | Δ vs v4 |
|---|---|---:|---:|---:|---:|---|---:|---:|---:|---:|
| CK.1 | SOL 2024-H2 | 31 | −1.02 | 8938 | 0.9795 | FAIL | −0.39 | −0.63 | (n/a) | (n/a) |
| **CK.2** | SOL 2025-H1 | 51 | **+1.96** | 9712 | 0.9705 | **PASS** | +1.32 | +0.64 | +1.32 (v4a) | +0.64 |
| **CK.3** | SOL 2025-H2 | 55 | **+2.71** | 10144 | 0.9741 | **PASS** | +1.92 | +0.79 | +2.30 (v4b) | +0.41 |

## Avaliação dos gates pré-registrados

- **Gate 1 (mono-SOL ≥2/3 PASS):** 2/3 → **PASS**
- **Gate 2 (lift vs CH ≥2/3):** 2/3 → **PASS** (lift +0.64 e +0.79 nos 2 PASS)
- **Gate 3 (lift vs v4 SOL):** 2/2 → **PASS** (lift +0.64 vs v4a; lift +0.41 vs v4b)
- **Gate 4 (audit Gate B — TrendHTF load-bearing):** **FAIL**

### Por que Gate 4 FAIL bloqueia promoção

Padrão 12 (ADR-0068) define filter "load-bearing" como: **sem o filter, combo deve cair para FAIL** (Sharpe < 1.0 ou MC p5 < 9500). Audit Gate B é o teste empírico.

Para CK.2 e CK.3, o "sem TrendHTF" equivalente já existe em manifests ativos:
- **CK.2 SOL 2025-H1 sem TrendHTF** = CH.6 (RSI+width 300) Sh **1.32**, MC p5 **9558** → **PASS** sem TrendHTF
- **CK.3 SOL 2025-H2 sem TrendHTF** = audit-v4-b-sol-...-nofilter (RSI puro) Sh **2.30**, MC p5 **9898** → **PASS** sem TrendHTF

**Sem TrendHTF, ambos combos já passam folgado.** TrendHTF não é load-bearing — é **amplificador** (eleva Sharpe, mas o edge subjacente já existe sem ele).

Padrão 12 explicitamente bloqueia promover filter não load-bearing por causa do trade-off:
- Filter adiciona complexidade ao manifest (mais um param, mais superfície de auditoria)
- Filter reduz trade count (CH.6 94 trades vs CK.2 51; v4b CH.9 80 vs CK.3 55) → ~40% menos exposição
- Sem load-bearing, ganho de Sharpe pode ser overfit ao caminho de equity (poucos sinais filtrados foram "sortudos") em vez de edge estrutural

## Decisão

**NÃO promover CK para manifest v5.** Apesar de Gate 1+2+3 PASS, Gate 4 FAIL refutador.

### Por que não relaxar Gate 4

Tentação: "Sharpe lift +0.41 a +0.79 é real, vamos promover assumindo que filter agrega mesmo sem ser load-bearing." Resposta:

1. **Padrão 12 foi formalizado em ADR-0068 exatamente pra evitar isso.** Histórico recente (manifest v4 original com 4 combos) tinha 2/4 filter não load-bearing — foi split em v4a/v4b. Tolerar agora seria regressão de processo.
2. **MEMORY feedback_audit_red_flags** lista "Sharpe lift sem audit Gate B" como red flag de edge fantasma. Lift CK.2/CK.3 sem load-bearing entra exatamente nessa categoria.
3. **Trade count caiu ~40%.** Em paper trade real (BotBinance), menos trades = mais variance no resultado curto prazo. Sharpe ex-post pode parecer melhor em backtest mas live performance deveria assumir distribuição mais larga.
4. **v4b SOL 2025-H2 já está active com Sh 2.30 sem filter.** Substituir por CK.3 com Sh 2.71 + TrendHTF é trocar simplicidade por +0.41 Sharpe que não é load-bearing — péssimo trade.

### O que documentar

Padrão 14 (ADR-0073) **confirmado mono-SOL** mas com qualificação:
- TrendHTF amplifica edge SOL onde já existe
- TrendHTF **não cria edge** onde não existe (CK.1 SOL 2024-H2 ainda FAIL)
- TrendHTF **não é load-bearing** quando combinado com RSI mean-rev — RSI sozinho já basta em SOL 2025

Reformulação do Padrão 14: "Filter direcional HTF é amplificador asset-específico, não condição necessária. Útil para análise de robustez/sensibilidade; **não justifica entrar em manifest** sem load-bearing."

### Padrão 15 (novo, derivado)

**"Lift de Sharpe sem load-bearing é candidato a edge fantasma. Promoção de filter exige Padrão 12 PASS (audit Gate B confirma combo cai sem filter), não apenas Sharpe lift bruto. Lift sem load-bearing pode ir pra notas de pesquisa (futura série de robustez/composição), nunca direto pra manifest."**

## Consequências

### Imediatas
- Série CK arquivada como **PASS analítico, NÃO-promoção decisional**.
- Stack manifests inalterado: v2 + v3 + v4a + v4b ativos.
- Bridge AF↔bot **não postar** (signal-only, stack inalterado).
- Padrão 14 refinado + Padrão 15 documentado.

### Pesquisa
- TrendHTF arquivado como filter-de-amplificação válido para **análise**, não para **promoção isolada**.
- Próxima exploração potencial de TrendHTF: composição AND com width 300 — testaria se composto eleva edge ALÉM do que cada um isolado faz, mas exigiria nova série e Gate 4 explicitando "load-bearing relativo ao composto".

### Próximas séries (atualizado pós-CK)

1. **CL — RSI thresholds alternativos (9/25/75)** — varia parametrização dentro de família validada (RSI). Hipótese: thresholds mais extremos selecionam menos sinais mas mais qualitativos. Baseline RSI 14/30/70 já está no v4b.
2. **CM — Cross-timeframe 4h** com v4a/v4b params — testa generalidade timeframe.
3. **CN — Cross-asset DOT/AVAX/LINK** com v4a/v4b params — testa generalidade asset-cross sem mudar engine.

Recomendação implícita: **CL (RSI thresholds)** — mais barato (9 runs reusando tooling CH), responde diretamente se v4b SOL Sh=2.30 sobrevive a thresholds 9/25/75 ou se é overfit ao 14/30/70 específico.

## Critério de sucesso desta ADR

1. CK marcada como PASS-analítico, NÃO-promoção ✓
2. Padrão 14 refinado com qualificação de não-load-bearing ✓
3. Padrão 15 (lift sem load-bearing = candidato edge fantasma) formalizado ✓
4. Bridge não postado ✓
5. STATE.md atualizado
