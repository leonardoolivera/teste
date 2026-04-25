# 0024 — Ranking contract (leaderboard sobre pilotos validados)

**Status:** Accepted
**Date:** 2026-04-18
**Accepted:** 2026-04-18
**Deciders:** Usuário (owner do projeto) + agente.

## Context

A série H encerrou com **12 pilotos agentic** (H.1 a H.10 + H.5b + H.2a/b/c/...) todos refutados no critério 1 (`hit_rate ≥ 45%`), mas com **dispersão grande em eixos secundários** (`final_equity`, `max_drawdown`, `trade_count`, `p5` Monte Carlo, robustez a custos, fold-consistency). O dashboard manual em `STATE.md` (tabela 12 linhas) já mostrou trade-offs não-triviais — H.8 tem pior `hit_rate` mas melhor robustez a custos; H.9 tem melhor `final_equity` do protocolo mas ainda falha critério 1; H.10 tem fold 0 cruzando 45% mas pior `max_drawdown`.

O north star do usuário — *"quero ter tudo pronto pra quando começar a testar estratégias vocês saiam testando centenas 1 por 1 e ranqueando"* — exige formalizar **como ordenar N pilotos validados** antes de crescer N. Sem este contrato, comparação cross-piloto depende de inspeção manual de JSONs dispersos em `results/validation/<slug>/`, não escala para centenas, e decisões "qual piloto avança para canary/paper_only" viram política ad-hoc.

O módulo `src/alpha_forge/ranking/` já existe (scaffold de `vision/02-scope.md` §7) mas é vazio (README + `__init__.py` + subdirs vazios). Esta ADR é o primeiro contrato real desse módulo.

## Decision

Formalizar um **contrato de ranking determinístico, read-only, sobre diretórios `results/validation/<slug>/`**, com output imutável `RankedLeaderboard` e CLI dedicado `alpha-forge rank`. Score composto em v1 é **linear ponderado** sobre métricas normalizadas — configurável por arquivo de pesos, default documentado, tiebreak por `slug` alfabético.

### Input

- **Diretórios fonte:** lista de `results/validation/<slug>/` (ou auto-discovery em `results/validation/*/` via flag). Cada um deve conter os 4 JSONs canônicos: `run.json`, `walk_forward.json`, `monte_carlo.json`, `cost_stress.json`. Diretórios incompletos são **puladores com warning** — nunca causam erro fatal; o ranking continua com os válidos.
- **Arquivo de pesos opcional:** TOML com `[weights]` mapeando métricas a multiplicadores. Omisso → usa `DEFAULT_WEIGHTS` (abaixo).
- **Critério de elegibilidade opcional:** filtro booleano declarativo (e.g., `release_decision != "fail"`). Default: inclui todos.

### Output (`RankedLeaderboard`)

Pydantic frozen model, `extra="forbid"`:

```python
class LeaderboardRow(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    rank: int  # 1-indexed, atribuído após ordenação
    slug: str
    fe_baseline: float
    hit_baseline: float
    mdd_baseline: float
    trade_count: int
    spread_stress_ratio: float   # fe(spread+10) / fe(baseline), 1.0 = sem degradação
    mc_p5: float
    mc_p50: float
    mc_p95: float
    fold_max_hit: float
    fold_min_hit: float
    fold_std_hit: float
    release_decision: Literal["fail", "paper_only", "canary_only"]
    composite_score: float       # score ponderado final
    flags_digest: str            # sha256[:16] de run.flags canonical — invariante de config

class RankedLeaderboard(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    generated_at: str            # ISO-8601 UTC
    alpha_forge_version: str
    weights: dict[str, float]    # pesos efetivamente usados
    eligibility: str             # expressão declarativa ou "all"
    rows: list[LeaderboardRow]   # ordenadas por rank ascendente
```

### Score composto v1 — linear ponderado normalizado

Cada métrica é normalizada para [0, 1] sobre a **amostra atual** via min-max, com direção canônica (maior = melhor):

```
score = w_fe        * norm(fe_baseline, higher_better=True)
      + w_hit       * norm(hit_baseline, higher_better=True)
      + w_mdd       * norm(mdd_baseline, higher_better=False)
      + w_stress    * norm(spread_stress_ratio, higher_better=True)
      + w_p5        * norm(mc_p5, higher_better=True)
      + w_fold_min  * norm(fold_min_hit, higher_better=True)
      + w_fold_std  * norm(fold_std_hit, higher_better=False)
```

**DEFAULT_WEIGHTS (v1):**

```toml
[weights]
w_fe       = 1.0   # final equity baseline
w_hit      = 2.0   # hit rate baseline (critério 1 primário)
w_mdd      = 1.5   # max drawdown baseline (critério 2)
w_stress   = 1.0   # robustez a spread+10 (ADR-0019 / critério 3)
w_p5       = 1.5   # cauda inferior Monte Carlo
w_fold_min = 1.0   # pior fold (consistência)
w_fold_std = 0.5   # dispersão fold-a-fold (consistência)
```

**Soma dos pesos não precisa somar 1.0** — a normalização por min-max já escala cada termo; a soma apenas determina a magnitude do score final. Documentado no README do módulo.

### Ordenação e tiebreak

1. Ordenar por `composite_score` **descendente**.
2. Empate em `composite_score` → ordenar por `slug` **ascendente** (estável, lexicográfico). Garante determinismo puro.

### Invariantes obrigatórios (property-based)

1. **Permutação-invariância:** `rank(permute(input)) == rank(input)` — ordem de entrada dos diretórios não afeta output (modulo `rank` sendo reatribuído).
2. **Min-max bem-definido:** se todos os pilotos têm mesmo valor em uma métrica, `norm(.)` retorna `0.5` (constante) — evita divisão por zero; documentado.
3. **Determinismo bit-a-bit:** rodar `rank` duas vezes sobre mesmo input produz mesmo `RankedLeaderboard` exceto `generated_at` (ISO timestamp).
4. **flags_digest estável:** mudança em `run.flags` altera digest; mesma config produz mesmo digest cross-run (ADR-0017 canonical string preserve-order já garante).
5. **Eligibility puramente filtra:** aplicar eligibility reduz `len(rows)` mas não reordena o subconjunto sobrevivente vs ranking sem filter.

### CLI contract

```
alpha-forge rank \
    [--runs-dir PATH]                   # default: results/validation
    [--slug SLUG] [--slug SLUG] ...     # explícito; incompatível com --runs-dir
    [--weights-file PATH]               # TOML; default DEFAULT_WEIGHTS
    [--eligibility EXPR]                # e.g., "release_decision != 'fail'"
    [--output PATH]                     # default: results/ranking/<timestamp>.json
    [--format json|table]               # default: json; table prints markdown-ish
```

- Read-only; **não** modifica `results/validation/`.
- Exit 0 mesmo com diretórios incompletos (pula com warning em stderr).
- Exit 1 apenas se **zero** pilotos elegíveis após filtros.

## Consequences

- **Positive:** primeiro caminho determinístico para ordenar N pilotos sem inspeção manual — pré-requisito do north star "centenas 1 por 1 e ranqueando". Contrato pydantic frozen + property-based garante que scaling para N=100+ não introduz non-determinismo. Pesos configuráveis permitem redefinir prioridade sem recompilar (e.g., "maximize p5, penalize trades" para regime de paper trading). Persistência JSON permite diff histórico entre rankings (próxima ADR poderia definir `alpha-forge rank-diff`). `flags_digest` fornece identidade invariante do piloto (sha truncado das flags canônicas), resistente a renomeação de slug. Integration test com os 12 pilotos já existentes como fixture — infraestrutura "live" de validação imediata. Reuso 100% de `load_walk_forward_folds` / `load_monte_carlo_summary` / `load_cost_stress_report` / `load_run_metadata` — zero duplicação de I/O.
- **Negative:** min-max normalização é **sensível à amostra** — adicionar um piloto outlier pode deslocar todo o ranking. Documentado como tradeoff consciente (alternativa: z-score, rejeitada abaixo). Score linear ponderado é **compensatório** — um piloto ruim em `hit` pode compensar com `fe` alto; em v1 isso é aceito, pois Pareto-dominance + tiebreak seria mais complexo e não há demanda concreta ainda. `eligibility` é expressão mini-DSL — v1 limita a comparações simples sobre campos de `LeaderboardRow`; expressões complexas deferred.
- **Neutral:** ranking não consome `fold_max_hit` no score — aparece apenas como coluna informativa (descobrir "piloto cujo melhor fold cruza 45%" é read-only). `release_decision` NÃO entra no score — é metadado de gate, não métrica de desempenho; pode entrar em `eligibility`. Nenhuma das 12 entradas da série H produz ranking definitivo; esta é infraestrutura para séries futuras.

## Alternatives considered

- **Pareto dominance layer + tiebreak por sum-of-ranks** — rejeitado para v1: N≥3 métricas produzem fronteira Pareto tipicamente com ≥80% dos pilotos não-dominados sobre amostras pequenas (observado nos 12 atuais); colapsa ordenação. Pode voltar como v2 se ranking linear mostrar patologias.
- **Z-score normalização** — rejeitado: assume distribuição aproximadamente gaussiana sobre métricas que são fortemente não-gaussianas (hit_rate bounded [0,1]; fe bounded por [0, capital*alav]). Min-max é agnóstico de distribuição.
- **Peso fixo sem config TOML** — rejeitado: usuário explicitou demanda de "ranquear" como atividade contínua com prioridades que podem mudar (hoje: maximize hit; amanhã: minimize drawdown em regime de volatilidade extrema). Flexibilidade é barata.
- **Absolute scoring (sem normalização)** — rejeitado: somar `fe_baseline ≈ 9000` com `hit ≈ 0.3` sem normalizar distorce pesos relativos — `fe` dominaria sempre.
- **Incluir `release_decision` no score** — rejeitado: decisão de gate (fail/paper_only/canary_only) é categórica e não ordinal (paper_only NÃO é "meio-caminho" entre fail e canary_only; é um gate distinto). Filtro de elegibilidade é o lugar correto.
- **Deferir todo o módulo ranking e resolver via planilha externa** — rejeitado: o ponto do Alpha Forge é ser auto-contido e reprodutível; planilha externa não versiona, não passa property-based, não integra a CI.

## Follow-ups

Cada item é pending work em STATE.md:

- Implementar `src/alpha_forge/ranking/scoring/schemas.py` com `LeaderboardRow` + `RankedLeaderboard` + `ScoreWeights` (TOML loader).
- Implementar `src/alpha_forge/ranking/scoring/leaderboard.py` com função `rank_pilots(slugs, runs_dir, weights, eligibility) -> RankedLeaderboard`. Reusa `load_*` de `validation/persistence.py`.
- Registrar `alpha-forge rank` em `src/alpha_forge/cli/app.py`.
- Property-based tests: permutação-invariância, min-max constante, determinismo bit-a-bit, `flags_digest` estável, eligibility puramente filtra (5 propriedades mínimas).
- Integration test com os 12 pilotos atuais como fixture — smoke test "rank produz JSON válido com 12 rows ordenadas".
- Atualizar `system/api.md` (seção nova `ranking/`) + `system/flows.md` (fluxo "validate → rank → diff") + README de `src/alpha_forge/ranking/`.
- Criar `results/ranking/` no .gitignore (outputs persistidos, não versionados).
