# VALIDATION.md — I.1 Bollinger 20/2 SOL 180d

## Testes executados

- Suíte `337 passed, 1 skipped` preservada (subiu de 312 com a adição dos 25 testes da família
  Bollinger — 23 unit + 2 property).
- Pipeline `alpha-forge validate` limpo; 4 JSONs persistidos em
  `results/validation/bollinger-20-2-sol-180d-baseline/`.
- Pipeline `alpha-forge rank` limpo; leaderboard N=13 persistido em `results/ranking/20260418T102235Z.json`.

## Conformidade (ADR-0025 híbrido)

| Critério                                  | Limite  | Observado              | Status    |
| ----------------------------------------- | ------- | ---------------------- | --------- |
| 1. hit_rate baseline                      | ≥ 45%   | **65.85%**             | **OK**    |
| 2. max_drawdown baseline                  | ≤ 35%   | 6.93%                  | **OK**    |
| 3. spread+10 / baseline                   | ≥ 0.95  | 9859.11/10189.15=0.968 | **OK**    |
| Corroboração: fold máx hit > 45%          | > 45%   | **76.47% (fold 3)**    | **OK**    |
| Corroboração: fold mín hit > 45%          | > 45%   | 50.00% (fold 2)        | **OK**    |
| Rank relativo (ADR-0024)                  | top-3   | **1/13**               | **OK**    |

**Todos os gates passam — primeiro piloto do protocolo a cruzar critério 1 (`hit_rate ≥ 45%`).**

## Invariantes

- **ADR-0019 13ª confirmação:** `fee+10 ≡ spread+10 = 9859.11` bit-a-bit (ambos reduzem
  `final_equity` identicamente em 2·(5 bps) efetivos).
- **ADR-0010 monotonicity:** `fe(fee+10)=9859.11 < fe(baseline)=10189.15`;
  `fe(slip+5)=10156.07 < baseline`; `fe(spread+10)=9859.11 < baseline`. ✅
- **ADR-0003:** MC com seed=42 produz `p50=10140.97`, `p5=9277.98`, `p95=10922.44` — MC preserva
  sinal positivo em p5 (acima do `capital_inicial=10000`? não: 9277.98 < 10000; MC cauda inferior
  vai a −7.2% em 500 resamples).
- **ADR-0025:** piloto aberto diretamente sob critério híbrido — AUDIT não carrega seção de
  re-auditoria (ADR-0025 §"Próxima série (I) abrir pilotos já sob ADR-0025 desde o início").
