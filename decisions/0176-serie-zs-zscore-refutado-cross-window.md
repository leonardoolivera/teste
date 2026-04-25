# 0176 — Série ZS closeout: zscore MR refutado em cross-window

**Status:** Accepted — zscore arquivado, edge não sobrevive fora de 2025-H1.
**Date:** 2026-04-20
**Deciders:** Usuário (piloto automático) + agente
**Relates to:** ADR-0175 (pré-reg), ADR-0169 (candidatos)

## Resultado consolidado

9 runs (3 ativos × 3 janelas semestrais), mesma config `zscore 20/2.0 short --no-long-only`.

| Tag | Dataset | Trades | Sharpe | PnL% | Pass |
|---|---|---:|---:|---:|:---:|
| ZS.1 | BTC 2025-H1 | 67 | -0.19 | -0.87 | ❌ |
| ZS.2 | ETH 2025-H1 | 80 | **2.37** | 14.46 | ✅ |
| ZS.3 | SOL 2025-H1 | 77 | **3.01** | 21.81 | ✅ |
| ZS.4 | BTC 2025-H2 | 73 | 0.56 | 1.64 | ❌ |
| ZS.5 | ETH 2025-H2 | 90 | 1.42 | 7.09 | ❌ (0.08 short) |
| ZS.6 | SOL 2025-H2 | 76 | **2.74** | 16.64 | ✅ |
| ZS.7 | BTC 2024-H2 | 78 | -0.66 | -2.74 | ❌ |
| ZS.8 | ETH 2024-H2 | 83 | 0.35 | 1.40 | ❌ |
| ZS.9 | SOL 2024-H2 | 82 | 0.80 | 4.41 | ❌ |

**Fase 1 (2025-H1): 2/3 pass** (gate Padrão 41 satisfeito).
**Fase 2 cross-window 6 runs: 1/6 pass** (só SOL 2025-H2).
**Total 9 runs: 3/9 pass.**

## Interpretação

### Trade count OK, edge não-estrutural

Diferente de Keltner (que falhou por sparse+ruído), zscore teve **67-90 trades por fold** em todas as 9 janelas — sample adequado. Refutação é de edge real, não de estatística insuficiente.

### Decaimento cross-era

Pattern nítido em todos 3 ativos:

| Ativo | 2025-H1 | 2025-H2 | 2024-H2 |
|---|---:|---:|---:|
| BTC | -0.19 | 0.56 | -0.66 |
| ETH | **2.37** | 1.42 | 0.35 |
| SOL | **3.01** | **2.74** | 0.80 |

ETH decay 2.37→1.42→0.35. SOL mantém em 2025 mas colapsa em 2024. **Edge específico do regime 2025** — provavelmente associado ao regime de volatilidade do segundo bull pós-halving.

### SOL 2025 = edge real mas não-diversificado

SOL passa em 2025-H1 (3.01) e 2025-H2 (2.74) — consistência in-era. Mas falha Padrão 43 (diversification):
- 1 ativo / 3 → falha
- 0 timeframes alternativos testados
- Cross-era 2024 mostra 0.80 — edge não persiste

Promover SOL-only seria violação Padrão 8 (overfit a ativo+janela específica).

### ETH outlier 2025-H1 = pattern conhecido

ETH 2025-H1 como outlier único é o mesmo pattern que apareceu em DE (Donchian) e KE (Keltner) — Padrão 45. Não é edge estrutural, é artefato de janela.

## Fase 3 salvage +width filter 2025-H1 (adendo, Padrão 45)

Testado `zscore + bollinger_width:30:1.5:300bps`, 3 runs 2025-H1:

| Tag | Dataset | Trades | Sh vs Sh_naked | PnL% |
|---|---|---:|---:|---:|
| ZS.10 | BTC | 21 | -0.17 vs -0.19 | -0.48 |
| ZS.11 | ETH | 57 | 0.62 vs 2.37 | 2.81 |
| ZS.12 | SOL | 82 | **4.94** vs 3.01 | 33.84 |

**1/3 pass** (SOL outlier único Padrão 41). ETH **caiu** de 2.37→0.62 com filter (oposto do que ADR-0172 Padrão 45 previa). BTC trade count 21 < 30. SOL amplificou mas é outlier isolado.

Filter canônico **não salva** zscore. Diferente de Keltner (onde filter normalizou 3 ativos para ~1.2), aqui filter divergiu os ativos. Hipótese: zscore naked SOL já era edge-like local 2025, filter só intensificou; ETH dependia de sinais de trend+MR que filter cortou.

## Decisão

- **zscore MR arquivado definitivamente**. 12 runs totais (9 cross-window + 3 +width), apenas 4/12 acima gate, sempre com ≤1 ativo diferente passando.
- Código preservado em `src/alpha_forge/strategies/families/zscore/` (custo zero de manter).
- Prior ADR-0169 (90% redundante com Bollinger) **parcialmente correto**: perfil diferente mas resultado igualmente não-deployable.
- **Piloto automático avança para próximo frontier**.

## Próximo candidato

Candidatos restantes em ADR-0169 esgotados:
- Donchian/MA-X refutados (DE, DX)
- Bollinger, RSI — já aprovados com filtro, em produção
- Keltner refutado (KE)
- zscore refutado (ZS)

**Novos frontiers possíveis** (ordem por prior):

1. **Filter composition** — testar combinações 2-filter (BB+RSI, BB+Keltner_width). Baixo custo, não requer engine nova. **Escolhido como próximo**.
2. **Cross-sectional / portfolio** — mudança de escopo grande. Requer engine novo (pair trading, rank-based). Prior bom mas custo alto.
3. **Different timeframes** (15m, 30m, 1d) com engines aprovadas — rápido de testar.
4. **Pausar** — declarar frontiers atuais esgotados, aguardar user.

## Não-alvo

- Não promover SOL-only (viola Padrão 43)
- Não retry zscore com threshold 1.5/2.5 (decay cross-era indica edge não-estrutural)
- Não testar zscore long-only (mesma família, mesmo edge fantasma)
