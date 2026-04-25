# 0130 — Série CZ9 pré-registro: MACX 10/30 long (lag menor, última chance família)

**Status:** Pre-registered
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0129 (CZ8 família arquivada), Padrão 35

## Motivação

CZ6/7/8 arquivaram MACX 20/50 long em 3 variantes (naked + 2 filters). Padrão 35 sugeriu não rodar mais variantes filter, mas **parâmetros diferentes** seguem na fronteira. MACX 10/30 tem lag menor (~50% do 20/50), pode pegar bull mais cedo e ser menos agressivamente rejeitado em chop.

Hipótese: se 10/30 mostra perfil similar a 20/50 (3+/6 strict bull) **com viés menos extremo** (FAIL misto menos profundo), engine pode ser viável naked. Se também colapsa em misto, família trend-following encerrada definitivamente.

## Escopo

6 runs, MACX 10/30 long 1h naked, mesma matriz CZ6:

| Tag | Asset | Janela | CZ6 (20/50) baseline |
|---|---|---|---:|
| CZ9.1 | BTC | 2024-H2 bull | 2.39 |
| CZ9.2 | ETH | 2024-H2 bull | 1.88 |
| CZ9.3 | SOL | 2024-H2 bull | 1.22 |
| CZ9.4 | BTC | 2025-H2 misto | -2.17 |
| CZ9.5 | ETH | 2025-H2 misto | -1.47 |
| CZ9.6 | SOL | 2025-H2 misto | -2.44 |

## Gate pré-registrado

- **Engine viável naked**: ≥3/6 Sh≥1.0 + 3/6 Sh ≥ -0.5 (FAIL misto contido) → candidato real, abrir CZ10 com filter selecionado
- **Salvamento parcial**: ≥4/6 Sh≥0.5 (mais consistência que 20/50, sem strict explosivo) → exploração de params 10/30 em outras janelas
- **Refutação família**: <2/6 Sh≥0.5 → MACX completamente fechado (todas variantes), Padrão 36 sobre engine inviabilidade

Timebox: ~6min. Closeout em ADR-0131.
