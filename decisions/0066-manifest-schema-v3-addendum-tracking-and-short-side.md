# ADR-0066 — Adenda ao schema v3: campos de rastreabilidade + short-side no execution_hints

- **Data:** 2026-04-19
- **Status:** Aceita — patch de dívida técnica descoberta durante promoção v4 (ADR-0065)
- **Relacionadas:** ADR-0031 (schema original), ADR-0051 (bollinger short), ADR-0058 (manifest v3 CG), ADR-0065 (promoção v4 RSI)

## Contexto

Durante a preparação do manifest v4 (RSI short, ADR-0065) tentei validar via `alpha_forge.exports.validate_manifest` — operação que a AGENTS.md §8 declara obrigatória pré-export. Resultado: **40 erros de validação**. Pior, re-validei o manifest v3 CG ativo (ADR-0060 ativou em `live_status: active`): **também falha com 40 erros**.

Causa raiz: o schema ADR-0031 foi escrito antes de ADR-0051 (short-side) e antes do projeto estabilizar a prática de incluir campos de rastreabilidade no manifest. Os manifests v3 CG e v4 RSI contêm campos úteis que o schema `extra="forbid"` rejeita:

### Campos rejeitados presentes nos manifests

**Top-level:**
- `complementary_to` — aponta para manifest sibling (v3→v2 ou v4→v3)
- `live_status` + `live_status_since` — estado de ativação
- `audit_adr` + `audit_closeout_adr` — ADRs de audit pré-registrado (ADR-0059/0066)
- `series_source` — objeto com tag da série, ADRs de pré-registro/closeout, raw_data path

**approved_combos[i]:**
- `regime` — rótulo qualitativo (chop, bull, misto) usado em análises
- `cost_stress_ratio_min` — duplica o global mas por combo (útil pra debug)
- `mc_p5_final_equity` — p5 do Monte Carlo por combo (documentado, gate é global)
- `source_tag`, `source_run_id`, `note` — rastreabilidade pra replays

**execution_hints:**
- Schema exige `entry_rule` singular mas manifests usam `entry_rule_long` + `entry_rule_short` (após ADR-0051)
- `reverse_on_signal` — documenta semântica de reversão

**expansion_policy:**
- `regime_dependence_note` — nota sobre limitação regime-específica
- `excluded_combos[i].source_tag` — rastreabilidade

Nenhum dos campos extras compromete o contrato runtime-faithful (ADR-0030). Todos são metadata documental útil, não instrução pro runtime.

**Impacto prático:** validator nunca foi chamado em produção — manifest v3 CG passou pra `active` sem validar. Dívida técnica descoberta agora. Bot já consumiu v3 sem problema porque seu adapter ignora campos extras.

## Decisão

Relaxar o schema v3 (pydantic + JSON Schema canônico em paralelo) para aceitar os campos acima, preservando **estritamente** os campos runtime-relevantes:

### Mudanças pydantic (`src/alpha_forge/exports/schema.py`)

1. `ApprovedCombo` — adicionar `regime`, `cost_stress_ratio_min`, `mc_p5_final_equity`, `source_tag`, `source_run_id`, `note` como opcionais.
2. `ExcludedCombo` — adicionar `source_tag` opcional.
3. `ExecutionHints` — tornar `entry_rule` opcional; aceitar `entry_rule_long` + `entry_rule_short` como alternativa (exatamente um dos dois caminhos precisa estar presente). Adicionar `reverse_on_signal` opcional.
4. `ExpansionPolicy` — adicionar `regime_dependence_note` opcional.
5. `ManifestV3` top-level — adicionar `complementary_to`, `live_status`, `live_status_since`, `audit_adr`, `audit_closeout_adr`, `series_source` (dict opaco) como opcionais.

**Não relaxar:**
- `runtime_contract: "faithful"` literal
- `runtime_invariants` strict (5 literais ADR-0030)
- `execution_hints.position_sizing: "fixed_notional_per_trade"` literal
- Regex de `alpha_forge_commit`, `symbol`, `timeframe`, `window_tag`, `validation_window`
- Bounds de `oos_sharpe ≥ 1.0`, `oos_mdd_pct ≤ 20`, `cost_stress_ratio_min ≥ 0.95`

### Validação cross-field de execution_hints

Se `entry_rule` ausente, exigir **ambos** `entry_rule_long` e `entry_rule_short`. Caso contrário, erro claro ("one of: entry_rule, or both entry_rule_long + entry_rule_short").

### JSON Schema canônico (`exports/approved/manifest.schema.json`)

Mesma relaxação, usando `oneOf` para entry_rule e `additionalProperties: false` preservado nos objetos strict (runtime_invariants).

## Consequências

### Imediatas
- Manifest v3 CG (`bollinger_short_width_20260419.json`) agora valida sem edições ao JSON — apenas schema se adapta.
- Manifest v4 RSI (`rsi_short_width_20260419.json`) valida e segue pro audit (ADR-0067).
- Tests `tests/unit/test_manifest_schema.py` atualizados — adicionar casos positivos (manifests reais v3/v4 validam) + negativos (runtime_invariants alterados ainda rejeitam).

### Retrocompatibilidade
- Manifests v1/v2 continuam legados (rejeitados por `manifest_version` regex).
- Schema strict para runtime-critical fields preservado — bot pode confiar que `runtime_invariants` + `position_sizing` + `alpha_forge_commit` são sempre exatos.

### Bridge AF↔bot
- Nenhuma notificação necessária — schema relaxamento é interno a AF. Bot não usa schema AF, tem o próprio adapter.

## Critério de sucesso

1. `validate_manifest(bollinger_short_width_20260419.json)` PASS ✓
2. `validate_manifest(rsi_short_width_20260419.json)` PASS ✓
3. Test negativo: manifest com `runtime_invariants.sizing: "snowball"` continua FAIL ✓
4. Test negativo: `execution_hints` sem nenhum entry_rule falha ✓
5. JSON Schema canônico em paralelo consistente com pydantic ✓
