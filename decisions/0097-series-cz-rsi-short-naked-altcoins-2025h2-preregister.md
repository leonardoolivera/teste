# 0097 — Série CZ pré-registro: RSI short naked em altcoins (DOT/AVAX/LINK 2025-H2)

**Status:** Accepted — pré-registro
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0088/0090 (Padrão 20), ADR-0095 (ingest expansion), ADR-0096 (snapshot)

## Hipótese

Padrão 20 (crypto major 1h naked: só short-side tem edge) foi estabelecido em BTC/ETH/SOL com 9 observações (CU+CV). **É regra específica de majors ou vale para crypto em geral?**

Altcoins L1/oracle (DOT, AVAX, LINK) são:
- Mais voláteis que majors (especialmente 2025-H2 bull-to-mixed)
- Correlacionados mas não idênticos (cada um tem narrativas específicas)
- Liquidez menor → custos de execução reais tendem a ser maiores, mas gate `cost_r ≥ 0.95` já stress-testa isso

Se Padrão 20 vale universal: RSI short naked deve funcionar em ≥1 dos 3 altcoins em 2025-H2 (janela onde v4b PASS em BTC Sh=1.64 e SOL Sh=2.30).

**Refutação:** se 0/3 PASS, Padrão 20 é restrito a majors — altcoins precisam de filter (explorar CZA depois).

## Design

### Parâmetros canônicos
- Engine: RSI(14/30/70) naked short
- `long_only=false` (reverse-on-signal ADR-0013 ativo; mas como queremos short-side dominante, vai disparar both e pós-analisa)
- Runtime faithful ADR-0030 (entry/exit market_at_open_next_bar, fixed_notional=2000, stop_loss=disabled)

### Pilotos (3 runs)
| Tag | Symbol | Window | Dataset |
|---|---|---|---|
| CZ.1 | DOTUSDT | 2025-H2 | dotusdt_1h_20250705_20251231_binance_spot |
| CZ.2 | AVAXUSDT | 2025-H2 | avaxusdt_1h_20250705_20251231_binance_spot |
| CZ.3 | LINKUSDT | 2025-H2 | linkusdt_1h_20250705_20251231_binance_spot |

Total: 3 runs (~7min).

## Gates pré-registrados

### Gate 1 — Passes isolados (mesmos de v4b)
Sh ≥ 1.0, trades ≥ 30, MDD ≤ 20%, MC p5 > 9500, cost_r ≥ 0.95, PnL > 3%.

### Gate 2 — Comparação com v4b majors 2025-H2
v4b PASS:
- BTC Sh=1.64 PASS
- SOL Sh=2.30 PASS

Gate informacional: se altcoin PASS com Sh ≥ 1.0 e dentro de ±40% do range majors, assume-se simetria cross-universo. Sh muito acima = altcoin mais explorável (makes sense dada volatilidade). Sh muito abaixo (mas ≥ 1.0) = edge presente mas decaído.

### Gate 3 — Promoção v8 candidato
≥ 1 PASS → emite manifest `rsi_short_pure_altcoins_2025h2_<data>.json` agregando os PASS.

### Gate 4 — Correlação vs v4b majors (se PASS)
Pearson retornos bar-a-bar entre CZ.X e v4b combos na mesma janela. Se r < 0.5, diversificação real; se r > 0.7, redundante.

## Riscos antecipados

1. **Liquidez baixa em altcoins pode comer edge** — cost_r pode failar em ≥ 1 (especialmente LINK que tem book mais fino em Binance spot). Gate informacional: se cost_r < 0.90 em algum, documenta como limite de liquidez executável.
2. **Altcoins seguem BTC direcionalmente** — retornos bar-a-bar vão ter r > 0.6 com v4b BTC/SOL com alta probabilidade. Gate 4 pode falhar diversificação mesmo se isolados PASS.
3. **Trade count baixo em altcoin** — RSI extremos acontecem menos frequentemente em altcoin que trend mais suave. Pode ficar < 30.
4. **2025-H2 é mixed regime** — não sabemos exatamente como altcoins performaram vs majors (não auditado previamente).

## Interpretação dos resultados possíveis

| Cenário | Verdict | Ação |
|---|---|---|
| 3/3 PASS | Padrão 20 universal em crypto | v8 cross-universe, monitorar correlação |
| 2/3 PASS | Padrão 20 majority-vale, asset-specific | v8 parcial, documenta qual altcoin FAIL e por quê |
| 1/3 PASS | Padrão 20 seletivo | v8 single combo, investiga se é edge real ou ruído |
| 0/3 PASS | Padrão 20 restrito a majors | não promove, abre CZA (RSI + filter em altcoin) |

## Critério de sucesso desta ADR

1. Sweep CZ executado
2. ADR-0098 closeout documenta verdict
3. Se promoção: v8 manifest
4. STATE.md atualizado
5. Padrão 20 refinado: universal vs major-restrito
