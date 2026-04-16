export type JsonPrimitive = string | number | boolean | null;
export type JsonValue = JsonPrimitive | JsonValue[] | { [key: string]: JsonValue };

export interface ApiListResponse<T> {
  count?: number;
  next?: string | null;
  previous?: string | null;
  results: T[];
}

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: 'admin' | 'librarian' | 'assistant' | 'manager' | 'integration';
  library_branch: string | null;
  is_active: boolean;
  is_staff: boolean;
}

export interface LoginResponse {
  token: string;
  user: User;
}

export interface DashboardOverview {
  generated_at: string;
  institutions: number;
  branches: number;
  active_branches: number;
  bibliographic_records: number;
  item_copies: number;
  available_copies: number;
  active_loans: number;
  overdue_loans: number;
  queued_reservations: number;
  active_blocks: number;
  active_inventory_campaigns: number;
  matched_inventory_reads: number;
  unmatched_inventory_reads: number;
  inventory_accuracy_rate: number;
}

export interface Institution {
  id: string;
  name: string;
  code: string;
  email: string;
  is_active: boolean;
}

export interface Campus {
  id: string;
  institution: string;
  institution_name: string;
  name: string;
  code: string;
  city: string;
  state: string;
}

export interface LibraryBranch {
  id: string;
  campus: string;
  campus_name: string;
  institution_name: string;
  name: string;
  code: string;
  email: string;
  phone: string;
  is_active: boolean;
}

export interface Author {
  id: string;
  name: string;
}

export interface Subject {
  id: string;
  name: string;
}

export interface BibliographicRecord {
  id: string;
  title: string;
  subtitle: string;
  isbn: string;
  publication_year: number | null;
  publisher: string;
  language: string;
  edition_statement: string;
  classification_code: string;
  cutter: string;
  description: string;
  author_ids: string[];
  subject_ids: string[];
}

export interface ItemCopy {
  id: string;
  bibliographic_record: string;
  bibliographic_title: string;
  library_branch: string;
  asset_code: string;
  tomb_number: string;
  barcode: string | null;
  rfid_tag: string | null;
  shelf_location: string;
  status: 'available' | 'loaned' | 'reserved' | 'processing' | 'lost' | 'discarded';
  notes: string;
}

export interface Patron {
  id: string;
  user: string | null;
  library_branch: string | null;
  registration_code: string;
  full_name: string;
  email: string;
  category: 'student' | 'teacher' | 'staff' | 'external';
  status: 'active' | 'blocked' | 'inactive';
  expires_at: string | null;
}

export interface PatronBlock {
  id: string;
  patron: string;
  reason: string;
  is_active: boolean;
  expires_at: string | null;
  created_at: string;
}

export interface Loan {
  id: string;
  patron: string;
  patron_name: string;
  item_copy: string;
  item_asset_code: string;
  checked_out_by: string | null;
  loaned_at: string;
  due_at: string;
  returned_at: string | null;
  status: 'open' | 'returned' | 'overdue';
  fine_amount: string;
}

export interface Reservation {
  id: string;
  patron: string;
  patron_name: string;
  bibliographic_record: string;
  record_title: string;
  pickup_branch: string;
  fulfilled_item_copy: string | null;
  status: 'queued' | 'available' | 'fulfilled' | 'expired' | 'canceled';
  queue_position: number;
  expires_at: string | null;
}

export interface ReturnReceipt {
  id: string;
  loan: string;
  loan_status: string;
  returned_by: string | null;
  return_token: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface ReturnReceiptLookup extends ReturnReceipt {
  patron_name: string;
  item_asset_code: string;
  record_title: string;
}

export interface PatronMe {
  id: string;
  registration_code: string;
  full_name: string;
  email: string;
  category: 'student' | 'teacher' | 'staff' | 'external';
  status: 'active' | 'blocked' | 'inactive';
  expires_at: string | null;
  library_branch: string | null;
  library_branch_name: string | null;
}

export interface PatronLoginResponse {
  token: string;
  patron: PatronMe;
}

export interface PatronPortalLoan {
  id: string;
  record_title: string;
  record_subtitle: string;
  asset_code: string;
  branch_name: string | null;
  loaned_at: string;
  due_at: string;
  returned_at: string | null;
  status: 'open' | 'returned' | 'overdue';
  fine_amount: string;
}

export interface PatronPortalReservation {
  id: string;
  record_title: string;
  pickup_branch: string;
  pickup_branch_name: string;
  status: 'queued' | 'available' | 'fulfilled' | 'expired' | 'canceled';
  queue_position: number;
  expires_at: string | null;
  created_at: string;
}

export interface InventoryCampaign {
  id: string;
  library_branch: string;
  name: string;
  status: 'draft' | 'active' | 'closed';
  opened_by: string | null;
  started_at: string | null;
  ended_at: string | null;
  notes: string;
  created_at: string;
}

export interface InventoryRead {
  id: string;
  campaign: string;
  session: string | null;
  operator: string | null;
  item_copy: string | null;
  item_asset_code: string;
  item_title: string;
  scanned_code: string;
  scan_source: 'patrimony' | 'barcode' | 'rfid' | 'camera' | 'manual';
  match_status: 'matched' | 'unmatched';
  device_label: string;
  read_at: string;
}

export interface InventoryScanInput {
  campaign_id: string;
  session_id?: string | null;
  scanned_code: string;
  scan_source: 'patrimony' | 'barcode' | 'rfid' | 'camera' | 'manual';
  device_label?: string;
}

export interface InventoryCampaignInput {
  library_branch: string;
  name: string;
  status: 'draft' | 'active' | 'closed';
  started_at?: string | null;
  ended_at?: string | null;
  notes?: string;
}

export interface LoanInput {
  patron: string;
  item_copy: string;
  due_at: string;
}

export interface ReservationInput {
  patron: string;
  bibliographic_record: string;
  pickup_branch: string;
  expires_at?: string | null;
}

export interface ReturnReceiptInput {
  loan: string;
  notes?: string;
}

export interface AuthorInput {
  name: string;
}

export interface SubjectInput {
  name: string;
}

export interface BibliographicRecordInput {
  title: string;
  subtitle?: string;
  isbn?: string;
  publication_year?: number | null;
  publisher?: string;
  language?: string;
  edition_statement?: string;
  classification_code?: string;
  cutter?: string;
  description?: string;
  author_ids?: string[];
  subject_ids?: string[];
}

export interface ItemCopyInput {
  bibliographic_record: string;
  library_branch: string;
  asset_code: string;
  tomb_number?: string;
  barcode?: string | null;
  rfid_tag?: string | null;
  shelf_location?: string;
  status: 'available' | 'loaned' | 'reserved' | 'processing' | 'lost' | 'discarded';
  notes?: string;
}

export interface UserInput {
  email: string;
  first_name?: string;
  last_name?: string;
  role: 'admin' | 'librarian' | 'assistant' | 'manager' | 'integration';
  library_branch?: string | null;
  is_active: boolean;
  is_staff?: boolean;
  password?: string;
}

export interface PatronInput {
  user?: string | null;
  library_branch?: string | null;
  registration_code: string;
  full_name: string;
  email?: string;
  category: 'student' | 'teacher' | 'staff' | 'external';
  status: 'active' | 'blocked' | 'inactive';
  expires_at?: string | null;
}

export class ApiError extends Error {
  status: number;
  payload: JsonValue | null;

  constructor(message: string, status: number, payload: JsonValue | null = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.payload = payload;
  }
}

export interface ApiClientConfig {
  baseUrl?: string;
  token?: string | null;
}

function normalizeBaseUrl(baseUrl?: string): string {
  if (!baseUrl) {
    return '/api/v1';
  }
  return baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
}

function joinPath(baseUrl: string, path: string): string {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${baseUrl}${normalizedPath}`;
}

function extractMessage(payload: JsonValue | null, fallback: string): string {
  if (!payload || typeof payload === 'string') {
    return typeof payload === 'string' && payload ? payload : fallback;
  }

  if (Array.isArray(payload) && payload.length > 0) {
    return extractMessage(payload[0], fallback);
  }

  if (typeof payload === 'object') {
    const record = payload as { [key: string]: JsonValue };
    const detail = record['detail'];
    if (typeof detail === 'string' && detail) {
      return detail;
    }

    for (const value of Object.values(record)) {
      const nested = extractMessage(value, '');
      if (nested) {
        return nested;
      }
    }
  }

  return fallback;
}

function unwrapList<T>(payload: T[] | ApiListResponse<T>): T[] {
  if (Array.isArray(payload)) {
    return payload;
  }
  return payload.results ?? [];
}

export function formatDateTime(value?: string | null): string {
  if (!value) {
    return 'Sem data';
  }
  return new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(new Date(value));
}

export function formatCurrency(value?: string | number | null): string {
  const amount = typeof value === 'string' ? Number(value) : value ?? 0;
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(amount || 0);
}

export function createApiClient(config: ApiClientConfig = {}) {
  const baseUrl = normalizeBaseUrl(config.baseUrl);
  const token = config.token;

  async function request<T>(path: string, init: RequestInit & { bodyJson?: unknown } = {}): Promise<T> {
    const headers = new Headers(init.headers);
    headers.set('Accept', 'application/json');

    let body = init.body;
    if (Object.prototype.hasOwnProperty.call(init, 'bodyJson')) {
      headers.set('Content-Type', 'application/json');
      body = JSON.stringify(init.bodyJson ?? {});
    }

    if (token) {
      headers.set('Authorization', `Token ${token}`);
    }

    const response = await fetch(joinPath(baseUrl, path), {
      ...init,
      headers,
      body,
    });

    if (response.status === 204) {
      return undefined as T;
    }

    const contentType = response.headers.get('content-type') || '';
    const payload = contentType.includes('application/json')
      ? ((await response.json()) as JsonValue)
      : ((await response.text()) as JsonValue);

    if (!response.ok) {
      throw new ApiError(extractMessage(payload, 'Nao foi possivel concluir a operacao.'), response.status, payload);
    }

    return payload as T;
  }

  return {
    login(email: string, password: string) {
      return request<LoginResponse>('/users/auth/login/', {
        method: 'POST',
        bodyJson: { email, password },
      });
    },
    me() {
      return request<User>('/users/auth/me/');
    },
    logout() {
      return request<void>('/users/auth/logout/', {
        method: 'POST',
      });
    },
    getDashboardOverview() {
      return request<DashboardOverview>('/core/dashboard/overview/');
    },
    listInstitutions() {
      return request<Institution[] | ApiListResponse<Institution>>('/core/institutions/').then(unwrapList);
    },
    listCampuses() {
      return request<Campus[] | ApiListResponse<Campus>>('/core/campuses/').then(unwrapList);
    },
    listBranches() {
      return request<LibraryBranch[] | ApiListResponse<LibraryBranch>>('/core/branches/').then(unwrapList);
    },    listAuthors() {
      return request<Author[] | ApiListResponse<Author>>('/catalog/authors/').then(unwrapList);
    },
    createAuthor(input: AuthorInput) {
      return request<Author>('/catalog/authors/', {
        method: 'POST',
        bodyJson: input,
      });
    },    listSubjects() {
      return request<Subject[] | ApiListResponse<Subject>>('/catalog/subjects/').then(unwrapList);
    },
    createSubject(input: SubjectInput) {
      return request<Subject>('/catalog/subjects/', {
        method: 'POST',
        bodyJson: input,
      });
    },    listRecords() {
      return request<BibliographicRecord[] | ApiListResponse<BibliographicRecord>>('/catalog/records/').then(unwrapList);
    },
    createRecord(input: BibliographicRecordInput) {
      return request<BibliographicRecord>('/catalog/records/', {
        method: 'POST',
        bodyJson: input,
      });
    },
    updateRecord(recordId: string, input: BibliographicRecordInput) {
      return request<BibliographicRecord>(`/catalog/records/${recordId}/`, {
        method: 'PUT',
        bodyJson: input,
      });
    },    listCopies() {
      return request<ItemCopy[] | ApiListResponse<ItemCopy>>('/catalog/copies/').then(unwrapList);
    },
    createCopy(input: ItemCopyInput) {
      return request<ItemCopy>('/catalog/copies/', {
        method: 'POST',
        bodyJson: input,
      });
    },
    updateCopy(copyId: string, input: ItemCopyInput) {
      return request<ItemCopy>(`/catalog/copies/${copyId}/`, {
        method: 'PUT',
        bodyJson: input,
      });
    },    listOperators() {
      return request<User[] | ApiListResponse<User>>('/users/operators/').then(unwrapList);
    },
    createOperator(input: UserInput) {
      return request<User>('/users/operators/', {
        method: 'POST',
        bodyJson: input,
      });
    },
    updateOperator(userId: string, input: UserInput) {
      return request<User>(`/users/operators/${userId}/`, {
        method: 'PUT',
        bodyJson: input,
      });
    },
    deleteOperator(userId: string) {
      return request<void>(`/users/operators/${userId}/`, {
        method: 'DELETE',
      });
    },
    listPatrons() {
      return request<Patron[] | ApiListResponse<Patron>>('/users/patrons/').then(unwrapList);
    },
    createPatron(input: PatronInput) {
      return request<Patron>('/users/patrons/', {
        method: 'POST',
        bodyJson: input,
      });
    },
    updatePatron(patronId: string, input: PatronInput) {
      return request<Patron>(`/users/patrons/${patronId}/`, {
        method: 'PUT',
        bodyJson: input,
      });
    },
    listPatronBlocks() {
      return request<PatronBlock[] | ApiListResponse<PatronBlock>>('/users/patron-blocks/').then(unwrapList);
    },
    listLoans() {
      return request<Loan[] | ApiListResponse<Loan>>('/circulation/loans/').then(unwrapList);
    },
    createLoan(input: LoanInput) {
      return request<Loan>('/circulation/loans/', {
        method: 'POST',
        bodyJson: input,
      });
    },    listReservations() {
      return request<Reservation[] | ApiListResponse<Reservation>>('/circulation/reservations/').then(unwrapList);
    },
    createReservation(input: ReservationInput) {
      return request<Reservation>('/circulation/reservations/', {
        method: 'POST',
        bodyJson: input,
      });
    },
    createReturnReceipt(input: ReturnReceiptInput) {
      return request<ReturnReceipt>('/circulation/return-receipts/', {
        method: 'POST',
        bodyJson: input,
      });
    },
    lookupReturnToken(tokenValue: string) {
      return request<ReturnReceiptLookup>(`/circulation/return-token/${tokenValue}/`);
    },
    listInventoryCampaigns() {
      return request<InventoryCampaign[] | ApiListResponse<InventoryCampaign>>('/inventory/campaigns/').then(unwrapList);
    },
    createInventoryCampaign(input: InventoryCampaignInput) {
      return request<InventoryCampaign>('/inventory/campaigns/', {
        method: 'POST',
        bodyJson: input,
      });
    },
    listInventoryReads() {
      return request<InventoryRead[] | ApiListResponse<InventoryRead>>('/inventory/reads/').then(unwrapList);
    },
    createInventoryScan(input: InventoryScanInput) {
      return request<InventoryRead>('/inventory/scan-reads/', {
        method: 'POST',
        bodyJson: input,
      });
    },
    patronLogin(registration_code: string, password: string) {
      return request<PatronLoginResponse>('/portal/auth/login/', {
        method: 'POST',
        bodyJson: { registration_code, password },
      });
    },
    patronSetPassword(registration_code: string, password: string) {
      return request<PatronLoginResponse>('/portal/auth/set-password/', {
        method: 'POST',
        bodyJson: { registration_code, password },
      });
    },
    patronMe() {
      return request<PatronMe>('/portal/auth/me/');
    },
    patronMyLoans() {
      return request<PatronPortalLoan[]>('/portal/my/loans/');
    },
    patronMyReservations() {
      return request<PatronPortalReservation[]>('/portal/my/reservations/');
    },
    patronRenewLoan(loanId: string) {
      return request<PatronPortalLoan>(`/portal/my/loans/${loanId}/renew/`, {
        method: 'POST',
      });
    },
    async downloadInventoryReadsCsv(campaignId: string): Promise<Blob> {
      const headers = new Headers({ Accept: 'text/csv' });
      if (token) {
        headers.set('Authorization', `Token ${token}`);
      }

      const response = await fetch(joinPath(baseUrl, `/inventory/campaigns/${campaignId}/export-reads/`), {
        method: 'GET',
        headers,
      });

      if (!response.ok) {
        let payload: JsonValue | null = null;
        try {
          payload = (await response.json()) as JsonValue;
        } catch {
          payload = await response.text();
        }
        throw new ApiError(extractMessage(payload, 'Nao foi possivel exportar o inventario.'), response.status, payload);
      }

      return response.blob();
    },
  };
}



export type ApiClient = ReturnType<typeof createApiClient>;
