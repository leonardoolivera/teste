# 0023 — Composite regime filter (AND/OR)

**Status:** Accepted
**Date:** 2026-04-18
**Accepted:** 2026-04-18
**Deciders:** Usuário (owner do projeto) + agente.

## Context

H.3 (`sma_slope`) e H.4 (`atr_regime`) refutaram critério 1 (`hit_rate ≥ 45%`) isoladamente mas têm padrões métricos complementares — SMA concentra valor em `p50`/`p95` de Monte Carlo, ATR concentra em `p5` + reduz `trade_count` em 35% (robustez a custos). A hipótese natural de H.5 é que **regime é multi-dimensional** — direção AND volatilidade juntas recuperariam edge onde cada eixo isolado falha. ADR-0022 §Consequences → Positive já preautorizou "novos filtros no mesmo contrato sem nova ADR — só nova implementação + nova linha de parser", mas **combinação lógica de filtros** não é um novo filtro heterogêneo; é um combinador estrutural que precisa de contrato próprio (quem compõe, com qual semântica, com que canonicalização, com que garantias de causalidade).

Sem esta ADR, o risco é implementar composição ad-hoc (e.g., hard-coded AND em `parse_spec`), quebrar a invariante "um filtro = uma linha canônica alfabética" de ADR-0017/ADR-0022, ou introduzir não-determinismo na ordem de serialização.

## Decision

Formalizar **combinador `CompositeFilter(filters: Sequence[RegimeFilter], mode: Literal["and", "or"])`** como `RegimeFilter` regular (cumpre o mesmo Protocol de ADR-0022). Semântica estrita: `mode="and"` → `all(f.is_active(window) for f in filters)`; `mode="or"` → `any(...)`. Canonicalização lexicográfica sobre os filtros aninhados; sintaxe CLI `and(f1,f2)` / `or(f1,f2)` via extensão de `parse_spec`.

```python
class CompositeFilter:
    name = "composite"  # não usado diretamente em canonical (prefixado por mode)

    def __init__(self, filters: Sequence[RegimeFilter], mode: Literal["and", "or"]) -> None:
        # valida len(filters) >= 2, mode in {"and","or"}, filters sem dupes
        ...

    def is_active(self, window: pd.DataFrame) -> bool:
        if self.mode == "and":
            return all(f.is_active(window) for f in self.filters)
        return any(f.is_active(window) for f in self.filters)
```

**Canonicalização (`canonical_string`):**

```
and(atr_regime:min_atr_bps=50:window=14,sma_slope:min_slope_bps=10:window=50)
```

Filtros internos ordenados alfabeticamente por `canonical_string(f)` — determinismo independe da ordem de passagem. Aninhamento permitido até N níveis (e.g., `and(or(f1,f2),f3)`) mas **escopo inicial limita a 1 nível** (sem aninhamento) para simplificar parser e reduzir superfície de ataque de combinatória.

**Parser (`parse_spec`):**

- `and(sma_slope:window=50:min_slope_bps=10,atr_regime:window=14:min_atr_bps=50)` → `CompositeFilter([...], mode="and")`.
- `or(...)` análogo.
- Rejeita: aninhamento (`and(and(...),...)`) com `ValueError`; lista com < 2 filtros; mesmo nome-filtro duplicado (e.g., `and(sma_slope:...,sma_slope:...)`).

**Propriedades derivadas obrigatórias (property-based):**

1. **AND é mais restritivo que cada filtro individual, a nível de signal-emission** — `sum(is_active_bars(and(f1,f2))) <= min(sum(is_active_bars(f1)), sum(is_active_bars(f2)))` sobre uma janela fixa. A propriedade **NÃO se sustenta a nível de `trade_count`**: a engine de execução força EXIT mid-trade quando qualquer filtro interno retorna `False` e permite re-entrada quando ambos voltam a `True`, fragmentando trades de um filtro-alone longo em múltiplos trades mais curtos. **Finding empírico registrado em H.5 (2026-04-18)**: AND produziu 74 trades enquanto `atr_regime` sozinho produziu 72 sobre BTC Donchian 180d — violação clara da leitura de trade_count, mas não da leitura de signal-emission. A propriedade correta é portanto sobre barras-ativas, não transações.
2. **OR é mais permissivo que cada filtro individual, a nível de signal-emission** — `sum(is_active_bars(or(f1,f2))) >= max(sum(is_active_bars(f1)), sum(is_active_bars(f2)))`. Mesma ressalva: trade_count pode variar por fragmentação.
3. **Causalidade preservada** — composição de filtros causais é causal (lookahead property herdada).
4. **Comutatividade canônica** — `canonical_string(CompositeFilter([f1,f2], "and")) == canonical_string(CompositeFilter([f2,f1], "and"))`.

## Consequences

- **Positive:** primeira hipótese multi-dimensional testável no protocolo (direção AND volatilidade). Gap de código minúsculo (~40 linhas para `CompositeFilter` + ~30 linhas para parser). Contrato `RegimeFilter` (ADR-0022) não muda — composição é uma implementação concreta como qualquer outra. 4 property-based obrigatórios herdam padrão de ADR-0022 (lookahead, monotonicity derivada, comutatividade canônica). Abre caminho para filtros mais complexos (majority-vote, weighted AND) no mesmo arcabouço, se justificado por pilotos.
- **Negative:** `parse_spec` agora tem dois níveis de sintaxe (`name:k=v:k=v` para filtros terminais, `mode(f1,f2,...)` para composição), aumentando complexidade do parser. Canonicalização exige ordenação por string — custo O(n log n) no número de filtros (irrelevante na prática; n ≤ 3). Aninhamento deferred — se um piloto futuro justificar `and(or(f1,f2),f3)`, ADR-0024 removerá restrição e estende parser com recursão.
- **Neutral:** `CompositeFilter` **não** implementa `mode="xor"`, `mode="majority"`, ou pesos; estes são deferred até haver consumidor concreto. ADR-0022 permanece inalterada — composição é extensão aditiva do contrato, não mudança. `run.json.flags["regime_filter"]` continua sendo uma única string canônica; schema não muda.

## Alternatives considered

- **Composição implícita via múltiplas flags `--regime-filter`** — rejeitado: quebra semântica "uma flag = um filtro canônico", exige CLI aggregator, dificulta `compare` (ambiguidade em ordem).
- **Classe-base abstrata com `__and__`/`__or__`** (`sma & atr`) — rejeitado: idiomático em Python mas depende de ordem de importação em `parse_spec`; string canônica fica obscura ("qual é o nome do filtro composto?"). Prefere-se forma explícita.
- **Aninhamento ilimitado desde o início** — rejeitado: combinatória explode testes property-based, parser recursivo é maior superfície de bug. Abrir conservador; estender sob demanda.
- **`xor` / `majority` como modos iniciais** — rejeitado: nenhum consumidor concreto ainda; ADR-0020 "gap mínimo primeiro" aplica.

## Follow-ups

Cada item é pending work em STATE.md:

- Implementar `CompositeFilter` em `src/alpha_forge/regimes/filter.py` + estender `canonical_string`/`parse_spec`.
- Adicionar 4 property-based: AND-restritivo, OR-permissivo, lookahead, comutatividade canônica.
- Adicionar integration test CLI para sintaxe `and(...)`.
- Abrir piloto **H.5 `donchian-20-10-btc-180d-regime-sma-and-atr`** combinando `sma_slope:window=50:min_slope_bps=10` e `atr_regime:window=14:min_atr_bps=50` com AND.
- Atualizar `system/api.md` com `CompositeFilter` + nova sintaxe de `parse_spec`.
