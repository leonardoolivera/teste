# Roadmap e Estrutura do Repositorio

## Fases de entrega

### Fase 0: fundacao

- definicao do dominio
- setup do repositorio
- autenticacao e autorizacao
- base de auditoria
- CI, testes e padroes de codigo

### Fase 1: MVP operacional

- cadastro de usuarios e leitores
- catalogacao basica
- exemplares
- emprestimo, renovacao, reserva e devolucao
- comprovante e token de devolucao
- envio de emails automaticos

### Fase 2: consolidacao

- multas e bloqueios
- relatorios operacionais
- etiquetas
- importacao bibliografica
- inventario por barcode
- scanner de patrimonio para inventario anual

### Fase 3: expansao

- RFID
- integracoes institucionais
- portal do leitor completo
- dashboards gerenciais
- aquisicoes e doacoes

### Fase 4: diferenciais

- autoatendimento
- analytics avancado
- recomendacoes
- app mobile
- integracoes extras e APIs publicas controladas

## Estrutura sugerida do repositorio

```text
biblioteca-ifms/
  backend/
    apps/
      core/
      users/
      catalog/
      inventory/
      circulation/
      acquisitions/
      notifications/
      reports/
      integrations/
      portal/
    config/
    tests/
  frontend/
    apps/
      backoffice/
      portal-leitor/
    components/
    lib/
    tests/
  infra/
    docker/
    k8s/
    monitoring/
  docs/
  scripts/
```

## Regras de organizacao

- cada modulo deve ter dono funcional claro
- regras de negocio devem ser testadas no backend
- adaptadores de hardware e integracoes devem ficar isolados
- relatorios prontos e consultas customizadas devem ser separados
- documentos de produto devem evoluir junto com o codigo

## Proximo passo recomendado

Transformar esta estrutura em backlog tecnico executavel, criando epicos, historias e primeiros modulos de codigo para `core`, `users`, `catalog` e `circulation`.

