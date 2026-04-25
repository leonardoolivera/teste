# 0087 — Série CU pré-registro: RSI long cross-asset BTC/ETH/SOL 2025-H1 (diversificação stack)

**Status:** Accepted — pré-registro antes de rodar
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0086 (CR closeout — Padrão 14 reforçado), ADR-0030 (runtime-faithful), ADR-0064 (Padrão diversificação stack)

## Hipótese

Stack atual é **todo short** (v3 Bollinger short, v4a/v4b/v6 RSI short). RSI long nunca foi testado manifest-faithful em BTC/ETH/SOL 2025-H1. Hipótese: **RSI long(14/30/70) tem edge em chop 2025-H1** — provê diversificação direcional ao stack short-heavy.

Sub-hipóteses:
- **H1:** RSI long funciona em chop (mesma janela 2025-H1 onde SOL/BTC short pegaram edge — chop deve ter reversões em ambas direções).
- **H2:** Long em alts é mais lucrativo que long em BTC (correlação chop × beta alta).

Refutação previne adicionar long ao stack se chop 2025-H1 é direcionalmente assimétrico (só short funciona).

## Design

**Pilotos (naked, sem regime filter):**

| Tag | Symbol | TF | Window | Modo |
|---|---|---|---|---|
| CU.1 | BTCUSDT | 1h | 2025-01-05..2025-07-04 | RSI(14/30/70) **long_only=true** |
| CU.2 | ETHUSDT | 1h | 2025-01-05..2025-07-04 | RSI(14/30/70) **long_only=true** |
| CU.3 | SOLUSDT | 1h | 2025-01-05..2025-07-04 | RSI(14/30/70) **long_only=true** |

**Engine:** RSI(14/30/70). Naked (sem filter). Mesmos invariantes runtime ADR-0030 (faithful, fixed_notional=2000, entry/exit market at open next bar, stop=disabled).

**Custos:** baseline 0.14%, stress 0.34% (fee +10%). Seed MC=42.

**Total:** 3 runs (~7min).

## Gates pré-registrados

### Gate 1 — Passes isolados
`≥1/3` PASS (Sh≥1.0, trades≥30, MDD≤20%, MC p5>9500, cost_r≥0.95).

### Gate 2 — Edge não-trivial
Para cada PASS: PnL%>3.0 (long em chop com 6 meses precisa render minimamente).

### Gate 3 — Promoção
Combos PASS Gate 1+2 → manifest **v7 candidato** (`rsi_long_2025h1.json`). Naked (sem filter, espelha v4b filosofia).

### Gate 4 — Cross-check vs short complementar
Comparar Sh long vs Sh short na **mesma janela mesmo ativo**:
- BTC long vs v4a BTC width (Sh=1.688)
- ETH long: sem incumbente
- SOL long vs v6 SOL trend (Sh=1.958)

**Não é gate bloqueador** — informação descritiva sobre simetria chop. Se long Sh dramaticamente > short Sh em mesmo ativo/janela, abre questionamento sobre por que short dominou estudo até agora (talvez viés de pesquisa).

## Interpretação dos resultados possíveis

| Cenário | Verdict | Ação |
|---|---|---|
| ≥1 PASS Gate 1+2 | RSI long funciona em chop 2025-H1 | promove v7 com combos PASS |
| 0 PASS Gate 1, todos baixo trade | RSI long não dispara em 2025-H1 | refutação; long-side fica fora; documenta assimetria |
| 0 PASS Gate 1 com Sh negativo | Chop 2025-H1 é direcionalmente short-only | confirma viés de pesquisa correto; encerra long sem manifest |
| Sh PASS mas PnL%<3 | Edge marginal, não vale custo operacional | não promove; documenta |

## Riscos antecipados

1. **Long em chop pode ter assimetria:** se entradas oversold acontecem em downtrend macro, long compra "facas caindo" — Sh negativo provável.
2. **Trade count baixo possível:** RSI(14) cross 30 é raro em uptrend; chop misto pode dar amostra suficiente, mas BTC pode ter <30.
3. **MDD pode estourar gate:** long em chop com stop=disabled tende a aguentar drawdowns longos esperando exit RSI≥50.

## Critério de sucesso desta ADR

1. Sweep CU executado e arquivado em `results/validation/`
2. ADR-0088 closeout documenta verdict por gate
3. Se promoção: v7 manifest emitido + ADR separada
4. Se refutação: assimetria short-only documentada como Padrão (se aplicável)
5. STATE.md atualizado
