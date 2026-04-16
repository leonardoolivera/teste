# Integracoes e Dispositivos

## Integracoes institucionais

- SSO com OAuth2, OpenID Connect ou SAML
- LDAP ou Active Directory
- ERP academico para alunos e professores
- RH para servidores
- AVA para experiencia academica integrada

## Integracoes bibliograficas

- MARC21
- Z39.50
- OAI-PMH
- importacao e exportacao CSV e XLSX

## Integracoes de comunicacao

- SMTP para emails transacionais
- provedor de email com webhooks de entrega
- opcional: SMS ou WhatsApp institucional

## Integracoes financeiras

- ERP financeiro
- gateway de pagamento, se a instituicao desejar quitar multas online

## Dispositivos e operacao fisica

- leitores de codigo de barras
- coletores de dados para inventario
- dispositivos moveis com camera para scanner de patrimonio
- impressoras de etiqueta
- impressoras termicas para comprovantes
- leitores e gravadores RFID
- antenas e portais antifurto
- kiosks de autoemprestimo e autodevolucao

## Protocolos e adaptadores

- API REST para integracoes modernas
- webhooks para eventos
- SIP2 ou adaptador equivalente para equipamentos bibliotecarios quando necessario
- conectores desacoplados por filas ou retries

## Regras para integracoes

- toda integracao deve ter log proprio
- toda integracao deve permitir reprocessamento
- falha de parceiro externo nao pode travar atendimento no balcao
- segredos e chaves devem ser rotacionaveis
- o scanner de patrimonio deve funcionar com baixa dependencia de hardware proprietario sempre que possivel


