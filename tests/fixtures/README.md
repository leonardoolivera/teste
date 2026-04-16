# `tests/fixtures/`

Dados sintéticos pequenos e determinísticos para testes unitários e de integração.

## Regras

- **< 5 MB por fixture** (NFR).
- Deterministic: mesma seed → mesmos bytes.
- Sintéticos, nunca dados reais de mercado (datasets reais vivem em `data/`, fora do git).
