# 0073 — Série CJ closeout: RSI short + TrendHTF FAIL 2/9 — filter direcional é asset-específico, não regime-genérico

**Status:** Accepted — série arquivada com FAIL principal mas sinal aproveitável em SOL
**Date:** 2026-04-19
**Deciders:** Usuário + agente (AF)
**Relates to:** ADR-0072 (pré-registro CJ), ADR-0062 (CH closeout PASS), ADR-0071 (CI closeout FAIL + Padrão 13), ADR-0068 (Padrão 12)

## Resultado

**PASS count: 2/9.** Gate 1 pré-registrado (≥3/9) → **FAIL**.

| Tag | Asset | Janela | Trades | PnL% | MDD% | Sharpe | MC p5 | cost_r | CH Sh | Δ vs CH | Verdict |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| CJ.1 | BTC | 2024-H2 | 25 | −3.10 | 2.17 | −1.513 | 9307 | 0.9811 | −0.76 | −0.75 | FAIL (trades<30, Sh, MCp5) |
| CJ.2 | ETH | 2024-H2 | 31 | −3.47 | 4.78 | −1.150 | 9054 | 0.9773 | −1.52 | +0.37 | FAIL (Sh, MCp5) |
| CJ.3 | SOL | 2024-H2 | 31 | −3.65 | 4.14 | −1.023 | 8938 | 0.9795 | −0.39 | −0.63 | FAIL (Sh, MCp5) |
| CJ.4 | BTC | 2025-H1 | 46 | −0.83 | 5.61 | −0.348 | 9175 | 0.9719 | **+1.69** | **−2.04** | FAIL (Sh, MCp5) |
| CJ.5 | ETH | 2025-H1 | 62 | +5.72 | 4.89 | +1.392 | 9429 | 0.9665 | +0.50 | +0.89 | FAIL (MCp5) |
| **CJ.6** | SOL | 2025-H1 | 51 | +9.64 | 4.75 | **+1.959** | 9712 | 0.9705 | +1.32 | +0.64 | **PASS** |
| CJ.7 | BTC | 2025-H2 | 57 | +1.41 | 2.09 | +0.610 | 9637 | 0.9696 | **+2.63** | **−2.02** | FAIL (Sh) |
| CJ.8 | ETH | 2025-H2 | 54 | +0.16 | 5.61 | +0.046 | 9071 | 0.9738 | +0.81 | −0.76 | FAIL (Sh, MCp5) |
| **CJ.9** | SOL | 2025-H2 | 55 | +11.30 | 4.07 | **+2.710** | 10144 | 0.9741 | +1.92 | +0.79 | **PASS** |

Dados crus: `exports/diag/series_cj_summary.json`.

## Avaliação dos gates pré-registrados

- **Gate 1 (≥3/9 PASS):** 2/9 → **FAIL**
- **Gate 2 (2024-H2 ≥1/3 PASS):** 0/3 → **FAIL** — hipótese H-direcional-recupera **refutada**. TrendHTF não salva 2024-H2 bull
- **Gate 3 (2025 ≥3/6 PASS):** 2/6 → **FAIL** — degradou vs CH 4/6 em mesma janela
- **Gate 4 (trades≥30 em ≥6/9):** 8/9 → PASS — TrendHTF não zera trade count
- **Gate 5 (audit Gate B):** N/A (Gate 1 FAIL)

## Interpretação

### Por que TrendHTF não recuperou 2024-H2

Hipótese era: TrendHTF short_only bloqueia entries durante uptrend HTF, evitando que RSI short opere against-trend em bull. **Refutada.** Em 2024-H2:
- BTC subiu de ~57k para ~95k (bull definido)
- TrendHTF(4h, sma=50) com close < SMA: ativa **só nos pullbacks dentro do bull** (que duram poucos candles)
- Resultado: trade count cai (25-31 vs 43-73 em CH) mas os trades restantes ainda perdem porque RSI overbought em pullback de bull dispara short na hora errada (reversão pra cima vem fast)
- Filter atua como restrição de quantidade sem mudar qualidade direcional do edge — é gate "anti-frequência" não "anti-erro"

### Por que CJ.6 SOL 2025-H1 e CJ.9 SOL 2025-H2 PASS forte

Ambos PASS com lift significativo de Sharpe vs CH (1.32→1.96, 1.92→2.71). Padrão emergente: **SOL tem mais volatilidade direcional** que BTC/ETH; quando entra em downtrend HTF, vai mais fundo. RSI overbought em downtrend forte = short com follow-through real. TrendHTF amplifica esse efeito ao filtrar fora os falsos sinais em micro-uptrends.

BTC e ETH em chop (2025) não têm essa amplitude. TrendHTF acaba bloqueando **bons** sinais em mini-pullbacks porque close 4h cruza SMA com pouca margem — filter ruidoso. Resultado: CJ.4 BTC 2025-H1 Sh 1.69→−0.35 (CH passava limpo, CJ destrói).

### Padrão 14 (novo, derivado)

**"Filter direcional HTF amplifica edge em ativos de alta volatilidade direcional (SOL-like) e degrada em ativos de baixa volatilidade direcional (BTC-like) em janelas chop."**

Implicações:
1. Filter direcional não é genérico cross-asset — é amp em SOL, ruído em BTC.
2. Padrão 12 (regime-específico) refinado: agora também **asset-específico** quando filter direcional.
3. Composição filter+ativo precisa ser justificada por característica do ativo, não apenas regime.

### Por que isso não vira manifest

Apesar de CJ.6 e CJ.9 serem PASS forte (Sh 1.96 e 2.71), promovê-los exigiria:
- Manifest v5 escopado a SOL 2025-H1 + 2025-H2 com TrendHTF
- Mas v4b já cobre SOL 2025-H2 sem filter (Sh 2.30, MCp5 9898) — **CJ.9 não é claramente superior** em base risk-adjusted (Sh 2.71 > 2.30 mas MCp5 10144 ≈ 9898; ambos PASS folgado)
- v4a já cobre SOL 2025-H1 com width (Sh 1.32) — CJ.6 com Sh 1.96 seria **lift real**

**Decisão:** CJ.6 (SOL 2025-H1 com TrendHTF) é candidato a substituir SOL 2025-H1 do v4a se audit Gate B passar. Mas **não nesta ADR** — exigiria:
1. Audit Gate B isolado pra CJ.6 (rodar sem filter — já temos: CH.6 SOL 2025-H1 com width Sh 1.32, sem width seria audit-v4-a-sol equivalente que já passou pra v4a)
2. Comparação direta CJ.6 (TrendHTF) vs CH.6 (width): qual é o filter de melhor explicação?
3. Seed stability {1337, 2024} pra CJ.6
4. ADR de promoção dedicada

Como o ganho (Sh 1.32→1.96) é parcial e v4a já está active, **arquivar a série e abrir promoção dedicada se Leo quiser explorar SOL+TrendHTF separadamente** é mais limpo. Bridge AF↔bot **não postar** — manifest stack inalterado.

## Consequências

### Imediatas
- Série CJ arquivada com FAIL no Gate 1, mas **resultado positivo isolado em SOL** documentado.
- Stack manifests inalterado: v2 + v3 + v4a + v4b ativos.
- Bridge AF↔bot **não postar** (regra signal-only).

### Padrão 14 documentado
Filter direcional HTF é asset-específico. Próximas séries com TrendHTF devem pré-registrar matriz **mono-asset** (3 janelas BTC OU ETH OU SOL), não cross-asset 9 pilotos. Gate `lift vs no-filter` por asset.

### Próximos candidatos (atualizado pós-CJ)

1. **CK — TrendHTF mono-SOL** (3 pilotos: SOL 2024-H2, 2025-H1, 2025-H2 com TrendHTF; comparar contra v4a/v4b SOL existentes). Pequena, 3 runs, decide se SOL+TrendHTF entra como track novo.
2. **RSI thresholds alternativos** (9/25/75) — varia parametrização dentro de família validada.
3. **Cross-timeframe 4h** com v3/v4 params — replica em timeframe maior.
4. **Cross-asset DOT/AVAX/LINK** com v4a/v4b params — testa generalidade asset-cross.

Recomendação implícita: **#1 (CK SOL+TrendHTF mono-asset)** — barato (3 runs), responde diretamente se Padrão 14 sustenta isolamento mono-asset, e potencialmente abre track v5 SOL-amplified.

## Critério de sucesso desta ADR

1. CJ marcada FAIL no Gate 1 ✓
2. Padrão 14 (filter direcional asset-específico) formalizado ✓
3. CJ.6/CJ.9 sinais positivos preservados pra exploração futura ✓
4. STATE.md atualizado com Padrão 14 + CK candidato
5. Bridge não postado ✓
