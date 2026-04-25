# AUDIT.md — H.10 Donchian 20/10 SOL 180d

release_decision: fail

## release_decision

**`fail`** por critério 1 (`hit_rate=31.07% < 45%`). Critérios 2, 3 e corroboração auxiliar (fold máx hit > 45%) passam.

## Blockers

Nenhum. Pipeline limpo; validador verde.

## Findings

1. **Terceiro fold do protocolo cruza 45%:** fold 0 H.10 = 47.62%, após H.3 fold 2 e H.5 fold 1. **Evidência acumulada de que existem sub-períodos com edge** — três folds independentes de três configurações diferentes cruzam o piso, mas nenhum protocolo agregado cruza.
2. **SOL tem a maior dispersão fold-a-fold** — hit varia 47.62 → 9.52. Coerente com natureza mais volátil do asset.
3. **Tradeoff volatilidade/edge explicitado:** hit_rate cross-asset ordena-se BTC (25.45) < ETH (28.13) < SOL (31.07), mas max_drawdown inverso. Edge "extra" vem acompanhado de risco extra.
4. **ADR-0019 12ª confirmação** (`fee+10 ≡ spread+10 = 8709.91`).

## Lições transversais pós-12 pilotos

1. **Nenhum dos 12 pilotos cruzou critério 1 (`hit_rate ≥ 45%`).** Convergência consistente em faixa 25-32%.
2. **Três folds isolados cruzaram 45%** (H.3 fold 2, H.5 fold 1, H.10 fold 0) — sub-períodos com edge existem mas não são identificáveis ex-ante via filtros heurísticos causais disponíveis.
3. **Asset é variável mais importante que filtro** — diferença cross-asset (+5.62 pp hit BTC→SOL) supera diferença com vs sem filtro no mesmo asset (+4.37 pp em H.3).
4. **ADR-0019 inquebrável** — 12 execuções independentes sobre 3 assets, 4 configurações de filtro, 3 janelas diferentes.

## Recomendações (encerramento série H)

- **Série H encerrada.** Decisão operacional: abandonar o critério hit_rate ≥ 45% como piso absoluto OU mover para série I com mudança estrutural (outra família, outro timeframe, stops, regime latente).
- **Calibração de baseline revisível** — ADR-D calibrou TBDs antes dos 12 pilotos. Com evidência robusta de que 45% é inatingível nesta família, o piso pode ser irreal. Revisitar metas com dados pós-H.10.
- **Série I proposta**: mean-reversion (Bollinger Bands ou RSI) sobre SOL 1h 180d — hipótese "volatilidade gera mean-reversion onde Donchian breakout não encontra edge".
- **Rankeamento dos 12 pilotos** — infraestrutura `ranking/` não existe ainda; pode ser próxima fronteira antes de série I, para ordenar pilotos por fe, hit, robustez, fold-consistency.

---

## Re-auditoria 2026-04-18 (ADR-0025)

release_decision: fail

**Critério vigente:** híbrido (ADR-0025) — `canary_only` exige `hit_rate ≥ 45%` absoluto; `paper_only` exige top-3 por `composite_score` (ADR-0024) com N ≥ 9.

**Snapshot de ranking (2026-04-18, DEFAULT_WEIGHTS de ADR-0024):**

- Rank: **11/12**
- `composite_score`: **2.93**
- `hit_baseline`: **31.07%** (< piso de 45%)
- `fe_baseline`: **9119.73**
- `flags_digest`: `cbfceb8efba12132`

**Justificativa:** rank 11/12 por `composite_score`; fora do top-3 → permanece `fail` sob ADR-0025. `hit_rate`=31.07% < 45% também impede `canary_only`.

**Decisão original preservada acima.** Esta seção é append imutável; revogações futuras devem ser **nova seção**, nunca edit.
