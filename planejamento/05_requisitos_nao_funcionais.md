# Requisitos Nao Funcionais

## Seguranca

- RNF-001 Todo trafego externo deve usar HTTPS.
- RNF-002 Senhas locais devem ser armazenadas com hash forte.
- RNF-003 O sistema deve suportar MFA para perfis administrativos.
- RNF-004 Toda acao critica deve ser auditada.
- RNF-005 Dados pessoais devem seguir principios de minimizacao e consentimento aplicavel.

## Performance

- RNF-006 Consultas comuns do catalogo devem responder em ate 2 segundos em condicoes normais.
- RNF-007 Operacoes de emprestimo e devolucao devem concluir em ate 1 segundo na maioria dos casos.
- RNF-008 Rotinas pesadas devem ser processadas em background quando possivel.

## Escalabilidade

- RNF-009 A arquitetura deve suportar multiplas bibliotecas e campi em uma mesma instalacao.
- RNF-010 O sistema deve permitir crescimento horizontal da camada web e de workers.

## Confiabilidade

- RNF-011 O sistema deve possuir backup automatizado e testado.
- RNF-012 Deve existir estrategia de recuperacao de desastre.
- RNF-013 Falhas em integracoes externas nao podem derrubar o nucleo transacional.

## Observabilidade

- RNF-014 Logs devem ser estruturados.
- RNF-015 Metricas e traces devem estar disponiveis para diagnostico.
- RNF-016 Filas, emails e jobs agendados devem ter monitoramento proprio.

## Acessibilidade e UX

- RNF-017 O portal e o backoffice devem seguir boas praticas de acessibilidade.
- RNF-018 A interface deve ser responsiva para desktop e tablet.
- RNF-019 Fluxos de atendimento devem priorizar poucos cliques e baixa ambiguidade.

## Conformidade

- RNF-020 O sistema deve preservar historico legal e administrativo conforme politicas institucionais.
- RNF-021 Exportacoes e relatorios devem respeitar permissao e sensibilidade dos dados.

## Manutenibilidade

- RNF-022 O codigo deve ser modular e testavel.
- RNF-023 Regras de negocio devem ficar concentradas em servicos de dominio.
- RNF-024 Toda integracao externa deve ser encapsulada em adaptadores.
