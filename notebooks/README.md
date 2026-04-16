# `notebooks/`

Jupyter para exploração e relatórios ad-hoc. **Notebooks não são produção.** Fluxos que se estabilizam migram para `src/alpha_forge/` ou `scripts/` → depois para `cli/`.

## Subpastas

- **`exploratory/`** — rascunhos, investigação rápida, análise pontual.
- **`reports/`** — relatórios preparados (ex: comparação entre estratégias), com outputs leves.

## Regras

- **Não comitar outputs pesados** (use `jupyter nbconvert --clear-output` ou `nbstripout`).
- Nenhuma lógica crítica nasce em notebook; se virar recorrente, promover para módulo.
