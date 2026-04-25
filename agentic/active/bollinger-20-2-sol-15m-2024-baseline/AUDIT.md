# AUDIT.md — L.1 Bollinger 20/2 SOL 15m 2024

release_decision: fail

## release_decision

**`fail`** — primeiro `fail` de Bollinger no protocolo (10 `canary_only` anteriores).
Critério 3 violado por margem larga: `spread+10 / baseline = 0.871 < 0.95`.

| Gate                                    | Observado | Status |
| --------------------------------------- | --------- | ------ |
| Critério 1: hit_rate baseline ≥ 45%     | 63.10%    | OK     |
| Critério 2: max_drawdown ≤ 35%          | 5.53%     | OK     |
| Critério 3: spread+10 / baseline ≥ 0.95 | **0.871** | **VIOLADO** |

## Blockers

Edge existe mas é economicamente frágil neste timeframe — **fail por custos**, não por falta de edge.

## Findings

1. **Hit sobrevive timeframe menor.** 63.10% em 15m vs 67.82% em 1h — queda de 4.72 pp
   é pequena. Edge estatístico persiste.
2. **Custos engolem o edge em 15m.** +10 bps de spread (comum em execução real com
   liquidez média) derruba fe em 12.89% — 4× pior que em 1h.
3. **336 trades vs 87 em 1h.** Cada trade paga custos (entrada + saída). Timeframe menor
   multiplica a exposição cumulativa a fee/slip/spread.
4. **Fe baseline +4.34% ainda é positivo** — o edge NÃO desaparece, apenas fica frágil.
5. **ADR-0019 23ª confirmação** (`fee+10 ≡ spread+10 = 9088.47`).

## Lições

1. **Edge mean-reversion é específico de timeframe 1h.** Em 15m, edge estatístico
   persiste mas edge econômico quebra sob stress de custos. Descoberta crítica para
   handoff: qualquer tentativa de "multiplicar trades" em timeframe menor destrói o edge.
2. **Critério 3 de ADR-0025 é o que separa edge estatístico de edge operacional.** Até
   aqui, todos os 10 `canary_only` passavam folgado (ratio ~0.967). L.1 é o primeiro
   caso onde hit alto convive com violação do critério 3 — é exatamente o que o critério
   foi desenhado para capturar.
3. **Handoff BotBinance deve ficar em 1h.** J.2 BTC 1h 2024 segue como candidato primário;
   migração a 15m está formalmente refutada.

## Recomendações

- **Nenhuma nova ADR necessária.** ADR-0025 capturou o caso corretamente — protocolo
  funcionou como projetado.
- **Candidatos para Série M:**
  - M.1-M.3: Bollinger 4h (timeframe maior, trade-off oposto — menos trades mas menos
    sinais também). Testa se edge sobrevive redução de frequência ainda mais.
  - M.4-M.6: RSI oversold/overbought (segunda família mean-reversion, 1h, cross-asset).
    Requer nova ADR + implementação.
  - M.7+: regime filter + Bollinger 1h (adicionar filtro de volatilidade antes do sinal
    para reduzir trades em regime trend e preservar edge nos laterais).
