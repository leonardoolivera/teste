# VALIDATION.md — H.4 Donchian+regime ATR

> Gate ativo: **validação**. Pipeline `validate` rodou end-to-end sobre o comando canônico; 4 JSONs persistidos. Suíte expandida (295→298) passa com `--regime-filter atr_regime:...` no CLI.

## Testes executados

- **Suíte repo (estrutural):** `pytest -q` → **298 passed, 1 skipped** (+3 vs pré-H.4: 2 property ATR + 1 integration CLI).
- **Pipeline `validate`:** walk-forward 4 folds efetivos + Monte Carlo 500 resamples seed=42 + cost_stress baseline + 3 cenários.
- **`compare` H.1 vs H.4:** 23 flags iguais, 2 divergentes (`regime_filter`, `run_id`).
- **`compare` H.3 vs H.4:** 23 flags iguais, 2 divergentes (`regime_filter` — valores distintos, mesmo chave — `run_id`). **Primeiro uso protocolar de `compare` entre dois pilotos com filtro ativo** — isola família de filtro como única variável.

## Conformidade com SPEC — item por item

| SPEC § | Conformidade |
|---|---|
| §1 Hipótese | **GAP** — hit_rate 26.39% < 45% e final_equity 9180.45 < 9500 (refuta hipótese "regime de volatilidade recupera edge"). |
| §2 Mercado BTCUSDT spot | OK. |
| §3 Timeframe 1h 180d | OK — `bars=4320`. |
| §4 Entrada Donchian | OK — `entry_window=20`. |
| §5 Saída rompimento-baixo 10 | OK — `exit_window=10`. |
| §6 Sem stops | OK. |
| §7 Sizing fracao=0.1 lev=2 | OK. |
| §8 Fee 5bps | OK. |
| §9 Slip 2bps/unit_notional | OK. |
| §10 Spread 0 baseline | OK + cost_stress spread+10. |
| §11 Funding N/A | OK — spot. |
| §11-bis Regime filter ATR | OK — `run.json.flags.regime_filter = "atr_regime:min_atr_bps=50:window=14"`. |
| §12 long_only=True | OK. |
| §13 Limitações | OK. |
| §Critério refutação 1 (hit_rate ≥ 45%) | **VIOLA** — 26.39%. |
| §Critério refutação 2 (mdd ≤ 35%) | OK — 8.80%. |
| §Critério refutação 3 (spread+10 Δ ≥ −5%) | OK com folga — Δ = −3.12%. |
| §Critério corroboração (trade_count < 114) | **OK** — trade_count = 72 (−42 vs H.3, −38 vs H.1). Primeira vez no protocolo que o critério de corroboração passa, mas critério 1 ainda reprova. |

## Propriedades estruturais confirmadas

- **ADR-0019 `fee+Δ ≡ spread+Δ` (6ª confirmação; 2ª com filtro ativo, 1ª com ATR no caminho):** `fee+10` e `spread+10` produzem `final_equity = 8894.38` bit-a-bit. Nova família de filtro não quebra a propriedade estrutural (esperado — propriedade depende de `notional/capital_inicial`, não de filtro).
- **ADR-0010 monotonicidade:** `cost_stress` não levantou `ValidationError`; cada cenário com custo maior produz equity menor ou igual ao baseline.
- **ADR-0022 canonicalização:** `run.json.flags.regime_filter` em forma alfabética; `parse_spec` aceita `atr_regime:window=14:min_atr_bps=50` e emite `"atr_regime:min_atr_bps=50:window=14"`.
- **ADR-0022 contrato genérico:** 2 consumidores reais (H.3 `sma_slope`, H.4 `atr_regime`) compartilham integração engine + propagação walk_forward + cost_stress sem nenhuma mudança no engine ou na validação. **Contrato validado como estável**.

## Saída `compare` (dupla)

Ver AUDIT.md §Comparação transversal tripla H.1/H.3/H.4.
