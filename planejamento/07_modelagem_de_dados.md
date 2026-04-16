# Modelagem de Dados

## Entidades centrais

### Institucional

- Institution
- Campus
- LibraryBranch
- Sector
- HolidayCalendar

### Seguranca e acesso

- User
- Role
- Permission
- AuditLog
- ApiClient

### Leitores

- Patron
- PatronCategory
- PatronStatus
- PatronBlock
- PatronEnrollment

### Catalogacao

- BibliographicRecord
- Title
- Edition
- Author
- Subject
- AuthorityRecord
- Publisher
- Collection

### Exemplares

- ItemCopy
- ItemStatus
- ShelfLocation
- Barcode
- RfidTag
- LabelTemplate

### Circulacao

- Loan
- LoanPolicy
- Renewal
- Reservation
- ReservationQueue
- ReturnReceipt
- ReturnToken
- Fine
- FineWaiver

### Aquisicoes

- PurchaseRequest
- Supplier
- PurchaseOrder
- Invoice
- DonationEntry
- AccessionBatch

### Comunicacao

- NotificationTemplate
- NotificationJob
- NotificationDispatch
- EmailEvent

### Relatorios e operacao

- InventoryCampaign
- InventoryRead
- InventoryScanSession
- InventoryDivergence
- DashboardSnapshot

## Relacoes principais

- um `BibliographicRecord` possui muitos `ItemCopy`
- um `Patron` possui muitos `Loan` e `Reservation`
- um `Loan` pode gerar um `Fine`
- uma `ReturnReceipt` gera um `ReturnToken`
- um `ItemCopy` pode ter um `Barcode` e um `RfidTag`
- uma `LibraryBranch` possui politicas, acervo, campanhas e equipe
- uma `InventoryScanSession` possui muitas `InventoryRead`

## Observacoes de modelagem

- separar obra bibliografica de exemplar fisico e obrigatorio
- status de exemplar deve ser historizado
- leituras de inventario devem guardar origem da leitura, operador e dispositivo usado
- tokens devem ter validade, assinatura e trilha de consulta
- multas nao devem depender apenas do valor atual, mas do historico de calculo
- usuarios internos e leitores podem compartilhar identidade, mas nao necessariamente o mesmo perfil de negocio



