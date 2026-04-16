# `strategies/families/` — famílias de estratégias

Cada família mora em sua própria subpasta (ex: `breakout/`, `momentum/`, `mean_reversion/`). Regra: arquivo solto **não** é aceito aqui — se a família merece existir, merece subpasta e documentação.

## Famílias previstas (ainda não implementadas)

1. Breakout de volatilidade
2. Momentum multi-timeframe
3. Pullback em tendência forte
4. Mean reversion agressiva com filtro de regime
5. Liquidity sweep / washout reversal
6. Continuação pós-consolidação
7. Expansão de range
8. Snowball / pyramiding progressivo
9. Falha de rompimento
10. Estratégia híbrida com volume/volatilidade

## Documentação obrigatória por família (quando implementada)

Cada subpasta deve conter um `README.md` com:

- **Hipótese** — por que a gente acredita que isso gera edge.
- **Parâmetros** — lista tipada (pydantic).
- **Riscos** — modos de falha conhecidos.
- **Filtros** — quais filtros de tendência/vol/sessão são aplicáveis.
- **Regimes proibidos** — regimes onde a estratégia é bloqueada.
- **Modo de falha** — o que acontece quando a hipótese não se sustenta.
