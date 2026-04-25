# 0062 — Série CH closeout: RSI short + width 300 PASS 4/9 — padrão 10 generaliza

**Status:** Accepted — série arquivada com gate PASS; promoção pra manifest v4 elegível via ADR separada
**Date:** 2026-04-19
**Deciders:** Usuário + agente.
**Relates to:** ADR-0053 (closeout CE), ADR-0057 (closeout CG PASS), ADR-0060 (manifest v3 ativo), ADR-0061 (pré-registro CH).

## Context

ADR-0061 testou se padrão 10 (filtro composicional parametrizado ao regime eleva edge borderline) generaliza além de Bollinger. Hipótese: RSI short + width 300 também passa em cross-period. Testou 9 pilotos BTC/ETH/SOL × 2024-H2/2025-H1/2025-H2.

## Resultados

Dados crus: `exports/diag/ch_series_summary.json`.

### Tabela completa

| Tag | Ativo | Regime | trd | Sh | MDD% | fe | cost_r | MCp5 | vs CE | Gate 1 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| CH.1 | btc | 2024-H2 | 43 | −0.76 | 4.59 | 9837 | 0.9753 | 9387 | +cr | FAIL (Sh, MCp5) |
| CH.2 | eth | 2024-H2 | 52 | −1.52 | 8.36 | 9497 | 0.9711 | 8691 | +cr | FAIL (Sh, MCp5) |
| CH.3 | sol | 2024-H2 | 73 | −0.39 | 9.22 | 9783 | 0.9588 | 8734 | −cr | FAIL (Sh, MCp5) |
| **CH.4** | btc | 2025-H1 | 37 | **1.69** | 1.67 | 10407 | 0.9781 | 9913 | +cr | **PASS** |
| CH.5 | eth | 2025-H1 | 77 | 0.50 | 8.31 | 10217 | 0.9609 | 8907 | +cr | FAIL (Sh, MCp5) |
| **CH.6** | sol | 2025-H1 | 94 | **1.32** | 5.74 | 10794 | 0.9555 | 9558 | +cr | **PASS** |
| **CH.7** | btc | 2025-H2 | 49 | **2.63** | 1.39 | 10406 | 0.9791 | 10030 | +cr | **PASS** |
| CH.8 | eth | 2025-H2 | 77 | 0.81 | 5.97 | 10296 | 0.9608 | 9376 | +cr | FAIL (Sh, MCp5) |
| **CH.9** | sol | 2025-H2 | 80 | **1.92** | 4.57 | 10951 | 0.9620 | 9777 | −cr | **PASS** |

### Gates — avaliação final (pré-registrada)

- **Gate 1** (principal, ≥3/9): **4/9 → PASS**
- **Gate 2** (lift cost_r vs CE, ≥6/9): **7/9 → PASS**
- **Gate 3** (edge preservado, ≥6/9): **6/9 → PASS** (exato no limiar)
- **Gate 4** (falsificacionista, ≤1/3 em 2024-H2): **0/3 → PASS** (mais limpo que CG)

**Veredicto overall: PASS.** Segunda série cross-period PASS. Padrão 10 generalizou de Bollinger pra RSI.

## Interpretação

### Distribuição de passes: CH ≠ CG

CG passou 3 de 4 em 2025-H1 (regime chop). CH tem 2 em 2025-H1 (CH.4, CH.6) + 2 em 2025-H2 (CH.7, CH.9). **Complementaridade de regimes** — RSI short + width captura dinâmica que Bollinger não captura em 2025-H2.

Explicação estrutural: Bollinger e RSI usam informação diferente. Bollinger depende de desvio padrão (σ); RSI depende de média de ganhos/perdas recentes (RS). Em 2025-H2, se o regime tem média móvel deslizando mais rápido que σ ajusta, RSI detecta extremos que Bollinger perde ou confunde.

### CH.7 é a joia da série

BTC 2025-H2 Sharpe **2.63**, 49 trades, MC p5 **10030** (único combo de CH com MC p5 > 10000), cost_r 0.9791. **Maior Sharpe BTC curta de todo o projeto.** BTC em 2025-H2 tinha sido combo difícil — CG.7 falhou por Sharpe 0.77; CH.7 passa com folga.

### CH.3 e CH.9 têm vs CE = −cr

2/9 pilotos onde filtro width **reduziu** cost_r vs CE RSI puro. Ambos em SOL (CH.3 2024-H2, CH.9 2025-H2). Hipótese: SOL tem width alto genericamente — filtrar por width pode adicionar menos valor em SOL do que em BTC/ETH. CH.9 ainda passa Gate 1 porque edge SOL é forte o bastante; CH.3 falha por outras razões (bull hostil).

**Não é refutação do padrão 10** — Gate 2 exigia 6/9 lift, entregou 7/9. Mas documenta limitação: filtro width funciona "em média" mas tem heterogeneidade entre ativos.

### Gate 4 zero-em-três

CH não passou **nenhum** piloto em 2024-H2 (bull). CG.3 tinha passado 1 (SOL). Limpeza diferente — RSI não tem "ruído positivo" em bull regime que Bollinger tem. Isto é mais coerente com Padrão 8 (cada regime tem direcionalidade preferida): em bull, short mean-rev é simplesmente errado, e RSI mostra isso sem ruído.

### Gate 3 apertado (6/9 exato)

3 pilotos em 2024-H2 têm Sharpe < 0 com trades ≥ 30 — falham Gate 3 por Sharpe. Edge RSI é claramente regime-dependente. Não muda PASS mas informa: se gate 3 fosse ≥7/9, CH teria falhado. Pré-registro estava bem calibrado.

### Padrão 10 agora empírico, não teórico

**Padrão 10 (ADR-0057)** era hipótese com 1 observação (Bollinger). Agora tem 2 observações (Bollinger + RSI). Upgrade epistêmico: de "regra indicativa" pra "regularidade empírica em N=2 famílias". Próxima ADR promoção documentará isso no manifest v4.

### Complementaridade CG + CH

4 combos CG (3×2025-H1 + 1×2024-H2) + 4 combos CH (2×2025-H1 + 2×2025-H2) = **8 combos cross-regime**. Zero overlap em (ativo, regime, família), porque famílias são diferentes. Manifests v3 (Bollinger short) e v4 (RSI short) são complementares estruturalmente, não redundantes.

**Padrão 11 (novo)**: "**famílias mean-rev diferentes (Bollinger, RSI) com mesmo filtro composicional geram combos cross-regime complementares, não redundantes**". Não promover uma bloqueia a outra.

## Consequences

### Imediatas
- **Elegível pra manifest v4** via ADR-0063 (promoção separada, espelho ADR-0058).
- **Bot não notificado** até audit v4 (espelho ADR-0059/0060).
- **ADR-0061 gates honrados.**

### Próxima ADR proposta — ADR-0063 Manifest v4 promoção RSI short

Escopo:
1. Schema separado `rsi_short_width_20260419.json` v3 schema (análogo a v3 Bollinger).
2. `engine.params`: `{family: rsi, period: 14, oversold: 30, overbought: 70, long_only: false, regime_filter: bollinger_width(30, 1.5, 300)}`.
3. 4 combos aprovados: CH.4, CH.6, CH.7, CH.9.
4. `expansion_policy` excluindo CH.1/2/3/5/8 com razões quantitativas.
5. Runtime invariants (ADR-0030), mesmos 5 literais.
6. Audit ADR-0064 (pré-registro) + ADR-0065 (closeout ativação) — espelho 0059/0060.
7. Notificação BotBinance após audit PASS.

### Regras consolidadas

- ADR-0030 runtime faithful continua válido.
- Manifests v3 + v4 são complementares; bot roda paralelo.
- Padrão 10 agora é empírico (N=2); Padrão 11 documenta complementaridade.

## Critério de sucesso deste closeout

1. `ch_series_summary.json` arquivado ✓
2. Gates 1-4 avaliados com veredicto pré-registrado ✓
3. Padrão 11 documentado ✓
4. Próxima ADR proposta com escopo definido ✓

## Fora do escopo

- Promoção imediata.
- Rodar outras parametrizações RSI (9/25/75). Se ADR-0063 audit encontrar problema, adiar.
- Testar Donchian short + width (nova série se ADRs 0063-0065 fecharem bem).
- Estudar redundância entre CG.3 (SOL 2024-H2) — único combo CG em 2024-H2 que CH refuta. Provavelmente artefato Bollinger-específico; fora do escopo.
