# VALIDATION.md — H.3 Donchian+regime SMA slope

> Gate ativo: **validação**. Pipeline `validate` rodou end-to-end sobre o comando canônico de IMPLEMENTATION.md; 4 JSONs persistidos.

## Testes executados

- **Suíte repo (estrutural):** `pytest -q` → **295 passed, 1 skipped** (ADR-0022 contribui 3 property-based + 3 integration CLI; linha de base pré-piloto).
- **Pipeline `validate`:** walk-forward 4 folds + Monte Carlo 500 resamples seed=42 + cost_stress baseline + 3 cenários.
- **`compare` H.1 vs H.3:** 23 flags iguais, 2 divergentes (`regime_filter`, `run_id`) — experimento controlado validado.

## Conformidade com SPEC — item por item

| SPEC § | Conformidade |
|---|---|
| §1 Hipótese | **GAP** — hit_rate 29.82% < 45% e final_equity 9195.59 < 9500 (refuta hipótese original). |
| §2 Mercado BTCUSDT spot | OK — dataset `btcusdt_1h_20250705_20251231_binance_spot` (SHA256 verificado pelo loader). |
| §3 Timeframe 1h 180d | OK — `bars=4320`. |
| §4 Entrada Donchian | OK — ADR-0011 `entry_window=20`. |
| §5 Saída rompimento-baixo 10 | OK — `exit_window=10`. |
| §6 Sem stops | OK — engine não aplica stops. |
| §7 Sizing fracao=0.1 lev=2 | OK — notional por trade = 2000 USDT. |
| §8 Fee 5bps | OK. |
| §9 Slip 2bps/unit_notional | OK. |
| §10 Spread 0 baseline | OK + cost_stress spread+10. |
| §11 Funding N/A | OK — spot. |
| §11-bis Regime SMAslope | OK — `run.json.flags.regime_filter = "sma_slope:min_slope_bps=10:window=50"` (canonicalização alfabética). |
| §12 long_only=True | OK — ADR-0013 NÃO ativado. |
| §13 Limitações | OK — apenas um filtro testado (conforme SPEC). |
| §Critério refutação 1 (hit_rate ≥ 45%) | **VIOLA** — 29.82%. |
| §Critério refutação 2 (mdd ≤ 35%) | OK — 9.60%. |
| §Critério refutação 3 (spread+10 Δ ≥ −5%) | OK por folga de 0.06 pp — Δ = −4.94%. |
| §Critério corroboração (trade_count < 110) | **VIOLA** — trade_count = 114 no baseline. |

## Propriedades estruturais confirmadas

- **ADR-0019 `fee+Δ ≡ spread+Δ` (5ª confirmação, now via regime filter):** fee+10 e spread+10 produzem `final_equity = 8741.66` bit-a-bit idêntico em H.3. Filtro não quebra a propriedade estrutural (esperado — filtro altera trade_count mas não `notional/capital_inicial`).
- **ADR-0010 monotonicidade:** `cost_stress` não levantou `ValidationError` — custo maior com mesmo filtro resultou em `final_equity` menor em todos os 3 cenários.
- **ADR-0022 canonicalização:** `run.json.flags.regime_filter` contém forma alfabética esperada; `compare` detecta divergência vs H.1 que não tinha a chave.

## Saída `compare` H.1 vs H.3

Ver AUDIT.md §Comparação transversal.
