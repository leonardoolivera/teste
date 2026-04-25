# AUDIT.md — Q.2 Bollinger ETH 1h 2024 + atr_regime

release_decision: canary_only

## release_decision

**`canary_only`** — 38º piloto. **Domina J.3 em todas as dimensões
operacionais** (hit +1.99 pp, fe +142.46 com fe cruzando 10000, trades
−5.9%, MC p5 +20.34, ratio +0.0024). Segundo piloto a dominar sua
baseline; valida que ganho do filtro ATR é **não-universal mas
reproduzível em múltiplos assets com volatilidade moderada**.

| Gate                                    | Observado | Status |
| --------------------------------------- | --------: | ------ |
| Critério 1: hit_rate baseline ≥ 45%     |    73.75% |     OK |
| Critério 2: max_drawdown ≤ 35%          |     5.93% |     OK |
| Critério 3: spread+10 / baseline ≥ 0.95 |    0.9684 |     OK |

## Blockers

`canary-trade` inexistente.

## Findings

1. **Filtro ATR domina em ETH 2024-H2** — 80 trades vs 85 (−5.9%), hit
   73.75% vs 71.76% (+1.99 pp), fe 10119.65 vs 9977.19 (cruza 10000).
   Efeito positivo mas de magnitude menor que P.2 BTC.
2. **Q.2 corrige a única fe sub-capital entre Bollinger `canary_only`**:
   J.3 tinha fe=9977.19. Após filtro, fe=10119.65. Filtro é valor real
   operacional em ETH.
3. **Espectro cross-asset da atividade do filtro identificado:**
   - BTC 2024-H2: filtro ativa muito (85→72 trades, −15%) → ganho grande
   - ETH 2024-H2: filtro ativa médio (85→80, −5.9%) → ganho médio
   - SOL 2024-H2: filtro ativa mínimo (87→87, −1.1% por relocação) → ganho marginal
   Espectro segue volatilidade realizada: BTC < ETH < SOL.
4. **Fold 3 hit=93.75%** é um dos maiores single-fold hits do protocolo.
5. **ADR-0019 38ª confirmação** — `fee+10 ≡ spread+10 = 9799.73`.

## Lições

1. **Filtro de regime ATR é universalmente SAFE (não piora nenhum asset)
   mas não universalmente VALIOSO (só ganha material quando asset tem
   períodos de baixa volatilidade).** BTC 2024-H2 tem esses períodos;
   SOL 2024-H2 não tem; ETH fica entre os dois.
2. **Threshold ATR (50 bps) é calibrado implicitamente para BTC.** Para
   assets high-vol como SOL, threshold mais alto (~100 bps) pode ativar
   mais — mas isso é parametrização, não universalização.
3. **Série Q valida arquitetura:** mesmo filtro, zero código novo,
   aplicação a 2 assets, descobriu 2 comportamentos distintos. Infra
   ADR-0022 cumpre contrato de genericidade.

## Recomendações

- **P.2 BTC permanece handoff primário**. Q.2 ETH entra leaderboard
  abaixo de P.2/P.3/J.2 mas acima de J.3 (original).
- **Série R candidata**: calibração de threshold `atr_regime:min_atr_bps`
  por asset. Testar SOL com threshold 100 e 150 bps para verificar se
  filtro pode ganhar valor com parâmetro calibrado.
- **Ou Série S candidata**: aplicar filtro ATR sobre sweet spot RSI
  (N.2 BTC) para verificar se ganho generaliza cross-família.
- **Encerrar Série Q em 2 pilotos** — objetivo era validação cross-asset;
  resultado é nuance importante (valor depende de asset), não universalidade.
