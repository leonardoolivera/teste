# `tests/`

Estrutura espelha a do pacote em `src/alpha_forge/`.

## Organização

- **`unit/`** — testes unitários rápidos. Meta NFR: suíte completa em **< 45 s**.
- **`integration/`** — testes end-to-end (pipeline data → backtest → validation → ranking). Meta NFR: **< 10 min**.
- **`property/`** — property-based (hypothesis). Inclui o corpus anti-lookahead (NFR: 0 falsos negativos). Marque com `@pytest.mark.property`.
- **`fixtures/`** — dados sintéticos pequenos e determinísticos. **Limite prático: < 5 MB por fixture.** Datasets reais vivem em `data/` (fora do git).

## Regras

- Nenhum teste unitário pode depender de arquivos em `data/` ou `results/` (estão fora do git).
- Testes de integração podem gerar artefatos em `results/` mas devem limpar depois (ou usar `tmp_path`).
- Testes property-based para enforcement anti-lookahead são **obrigatórios** antes de qualquer merge que toque `backtest/` ou `validation/`.
