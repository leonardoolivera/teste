# 0021 — CI agentic: estender `ci.yml` com gates de ADR-0020

**Status:** Accepted
**Date:** 2026-04-17
**Deciders:** autônomo (agente), autorizado pelo usuário em sessão 2026-04-17

## Context

ADR-0020 entregou o overlay agentic localmente: `check_gates.py` roda em Stop (opt-in), `validate_artifacts.py` roda por CLI, `block_live_trading.py` bloqueia PreToolUse. Mas os gates só executam na máquina do operador.

O repositório **já tem CI** em `.github/workflows/ci.yml` — `ubuntu-latest`, `astral-sh/setup-uv@v3`, Python 3.12, jobs de `ruff check` + `ruff format --check` + `pyright` + `pytest -q`. Isto cobre `src/` e `tests/`. Não cobre os novos gates da ADR-0020: `scripts/validate_artifacts.py` (opt-in) e o gate anti-hardcode `grep -rE 'BTC|ETH|SOL' src/`.

O fork tinha workflow separado `.github/workflows/agentic.yml`. Neste repositório, criar um workflow separado é desnecessário: CI já existe, e os novos gates são baratos (~1s cada). Adicionar como steps extras no `ci.yml` existente é a intervenção mínima.

## Decision

**Adicionar dois steps no job `check` de `.github/workflows/ci.yml`**, logo após `Tests (pytest)`:

```yaml
- name: Validate agentic artifacts (ADR-0020)
  run: uv run python scripts/validate_artifacts.py

- name: Anti-hardcode gate (ADR-0009 §2-ter)
  run: |
    if grep -rE '\b(BTC|ETH|SOL)\b' src/; then
      echo "Symbol hardcode detected in src/ — ver ADR-0009."
      exit 1
    fi
```

- **Step `Validate agentic artifacts`** executa `scripts/validate_artifacts.py` no modo opt-in (exit 0 se `agentic/active/` vazio ou inexistente; exit 1 se algum piloto ativo tem artefato ausente/placeholder). Sem piloto ativo, o step custa ~200ms.
- **Step `Anti-hardcode gate`** garante que nenhum símbolo de ativo foi hardcoded em `src/` (ADR-0009 proíbe). Hoje o match é 0; manter assim é invariante do projeto. `grep` retorna 1 quando não encontra e 0 quando encontra (por isso o `if grep ...; then exit 1`). `\b...\b` evita match em palavras maiores (ex: `ethics`, `solid`).

**Não** criar workflow separado `agentic.yml` — duplicação de setup (checkout, uv, sync) sem benefício. Estender o workflow existente é a menor superfície possível.

**Não** mover para Python 3.13 neste ADR — repositório declara `requires-python = ">=3.12"`; trocar CI para 3.13 é decisão independente (se tomada, outro ADR).

## Alternatives considered and rejected

1. **Workflow separado `.github/workflows/agentic.yml`** — duplica setup de ~40s (checkout + uv + sync). Sem benefício: os dois novos steps são leves e rápidos; colocar no mesmo job reutiliza a instalação.
2. **Job paralelo no mesmo workflow** — paralelizar economizaria ~5s mas custa outro setup de ~40s. Matematicamente ruim.
3. **Anti-hardcode como teste pytest em vez de step CI** — tentador, mas grep-based rules são melhores como step shell (visibilidade no log CI, feedback imediato, não mistura "código quebrado" com "símbolo hardcoded" no relatório de pytest).
4. **Validar YAML localmente com `yamllint`** — overkill; YAML de 2 steps extras é visualmente trivial e GitHub Actions rejeita YAML inválido no push.
5. **Step de `block_live_trading.py` simulado no CI** — hook é PreToolUse (roda dentro do Claude Code, não em Python puro); simular no CI exigiria feature específica só para CI. Gate anti-hardcode já cobre deriva em `src/` por grep.
6. **Rodar `pytest` em Python 3.13 no CI** — discrepância com declaração do projeto (3.12+). Se bumpar mínimo, ADR separado.
7. **Cache de pip/uv** — `uv sync` já é rápido; caching complica invalidação e não entrega ganho proporcional.
8. **Badge de CI no README** — cosmético; pode ser adicionado fora de ADR.
9. **Mover todos os gates agentic para pre-commit hook local** — ortogonal; pre-commit é bom, mas não substitui CI (colaboradores podem pular pre-commit).
10. **Matrix de OS (windows/macos)** — `playbooks/setup.md` foi validado em Windows 11 localmente; runtime é cross-platform. Abrir matrix só se houver bug OS-específico reportado.

## Consequences

**Positivas:**

- Qualquer PR é cobrado pelos gates da ADR-0020 (artefatos agentic + anti-hardcode).
- Zero duplicação de setup no CI.
- `validate_artifacts.py` e gate anti-hardcode ganham consumidor real — não dependem de humano lembrar de rodar.
- Reversível: deletar os dois steps restaura o CI anterior sem side-effect.

**Negativas:**

- ~2s adicionais por corrida de CI (tolerável; setup dominante).
- Se algum símbolo de ativo aparecer legitimamente em `src/` no futuro (ex: comentário documentando ADR-0009), o gate falha. Aceitar: pressão para manter a invariante, comentários devem usar `<symbol>` ou similar.

**Neutras:**

- `src/alpha_forge/` **zero mudanças**.
- `tests/` **zero mudanças**.
- Nenhum workflow novo; apenas 2 steps adicionados.
- Pré-requisito: ADR-0020 (fornece `scripts/validate_artifacts.py`).

## Guardrails

1. Workflow editado **depois** desta ADR.
2. Apenas 2 steps novos; sem reorganização do workflow existente.
3. Nenhum secret.
4. Nenhum `continue-on-error` — falhas são bloqueantes.
5. `actions/*` permanecem pinados em versão major existente (`@v4` / `@v3`); ADR-0021 não muda versões de actions.

## References

- ADR-0009 §2-ter — invariante "nenhum hardcode de símbolo em `src/`".
- ADR-0020 — fornece `scripts/validate_artifacts.py`.
- `.github/workflows/ci.yml` (pré-ADR-0021) — job `check` existente com ruff/pyright/pytest.
