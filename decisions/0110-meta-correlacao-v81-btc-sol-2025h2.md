# 0110 — Meta-correlação v8.1: BTC+SOL RSI short 2025-H2 corr=0.58 (diversificação OK no limite)

**Status:** Accepted — closeout
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0098 (Gate 4 pendente), ADR-0106 (v8.1 rollback)

## Motivação

ADR-0098 (v8 promoção original) listava "Gate 4 correlação LINK vs BTC+SOL 2025-H2 não executado" como débito. Pós-rollback v8→v8.1 (LINK removido), Gate 4 reduz a BTC vs SOL 2025-H2.

## Resultado

**Correlação de retornos bar-a-bar OOS (2025-07-05 a 2025-12-31):**

| Métrica | Valor |
|---|---:|
| Bars alinhadas por timestamp | 3455 |
| Correlação Pearson (all bars) | **0.583** |
| Correlação Pearson (both exposed) | **0.584** |
| Ambos expostos | 3343 / 3455 (96.8%) |

Correlação "both exposed" praticamente idêntica a "all bars" porque RSI short mantém posição quase contínua em 2025-H2 (alta frequência de sinais alternados; equity curve continuous).

## Interpretação

**Diversificação OK no limite.** Threshold canônico: < 0.6 = diversificação útil; > 0.8 = redundância. 0.58 fica **logo abaixo do limite superior de "OK"**.

**Contexto crypto 1h 2025-H2:** BTC e SOL são ambos majors com beta de mercado alto entre si. Correlação 0.58 em retornos da estratégia (não de preço bruto) é razoável dado que:
- Preço BTC vs SOL no período teve correlação ~0.8
- Estratégias RSI short naked capturam mesma classe de setups (mean reversion topos)
- Filter = none em ambos

**Não é duplicação:** 0.58 < 0.7 significa que há ~66% de variância não-compartilhada entre os dois combos (1 - 0.58² ≈ 0.66). Stack beneficia da inclusão de ambos vs apenas um.

**Não é ortogonal:** 0.58 > 0.3 significa que drawdowns tendem a coincidir. Em eventos de mercado adversos (reversão súbita tipo short squeeze), ambos vão sofrer juntos. Tail risk combinado > tail risk individual.

## Ação

Nenhuma — resultado está dentro do aceitável. Gate 4 ADR-0098 está agora **PASS** (diversificação no limite mas positiva).

Atualiza manifest v8.1 com meta dado:

```json
"meta_stats": {
  "cross_combo_corr_returns": 0.584,
  "cross_combo_corr_adr": "decisions/0110-meta-correlacao-v81-btc-sol-2025h2.md",
  "diversification_verdict": "OK_at_limit"
}
```

## Lição para stack futuro

Correlação ~0.6 sugere que adicionar **3º combo short RSI mesma janela mesmo regime** (se aparecer via ingest futuro) vai provavelmente estar nessa mesma faixa — adicionando valor marginal. Combos genuinamente diversificadores requerem:
- Direção diferente (long vs short) — mas long-side tem edge rara (Padrão 20)
- Engine diferente (Bollinger short é na v3, descorrelaciona em timing dos sinais)
- Regime diferente (2025-H1 vs 2025-H2) — mas 2025-H1 é janela única ainda

## Critério de sucesso

1. ✅ Correlação computada (0.584)
2. ✅ Verdict OK no limite
3. ✅ Gate 4 pendente ADR-0098 preenchido
4. ⏳ Manifest v8.1 atualizado com meta_stats (próximo)
5. ⏳ STATE.md atualizado

## Raw data

`exports/diag/meta_corr_v81.json`
