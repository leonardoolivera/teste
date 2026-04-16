
import { useCallback, useDeferredValue, useEffect, useState } from 'react';
import type { FormEvent, ReactNode } from 'react';
import { ApiError, createApiClient, formatCurrency, formatDateTime } from '@biblioteca-ifms/shared';
import { CatalogOperationsSection } from './sections/CatalogOperationsSection';
import { OperatorOperationsSection } from './sections/OperatorOperationsSection';
import { PatronOperationsSection } from './sections/PatronOperationsSection';
import type {
  Author,
  BibliographicRecord,
  DashboardOverview,
  InventoryCampaign,
  InventoryRead,
  ItemCopy,
  LibraryBranch,
  Loan,
  Patron,
  PatronBlock,
  Reservation,
  ReturnReceiptLookup,
  Subject,
  User,
} from '@biblioteca-ifms/shared';

type SectionKey = 'overview' | 'circulation' | 'catalog' | 'patrons' | 'operators' | 'inventory';

const tokenStorageKey = 'ifms-biblioteca-backoffice-token';
const sectionOrder: SectionKey[] = ['overview', 'circulation', 'catalog', 'patrons', 'operators', 'inventory'];
const sectionLabels: Record<SectionKey, string> = {
  overview: 'Radar operacional',
  circulation: 'Circulacao',
  catalog: 'Catalogacao',
  patrons: 'Leitores',
  operators: 'Operadores',
  inventory: 'Scanner patrimonial',
};
const scanSourceLabels: Record<string, string> = {
  patrimony: 'Patrimonio',
  barcode: 'Codigo de barras',
  rfid: 'RFID',
  camera: 'Camera',
  manual: 'Manual',
};

function toDateTimeLocalValue(date: Date) {
  const timezoneOffset = date.getTimezoneOffset() * 60000;
  return new Date(date.getTime() - timezoneOffset).toISOString().slice(0, 16);
}

function toApiDateTime(localValue: string) {
  return localValue ? new Date(localValue).toISOString() : '';
}

function displayUserName(user: User | null) {
  if (!user) {
    return '';
  }
  const fullName = `${user.first_name || ''} ${user.last_name || ''}`.trim();
  return fullName || user.email;
}

function toneClass(value: string) {
  if (['active', 'available', 'matched', 'returned', 'fulfilled'].includes(value)) {
    return 'tone tone--positive';
  }
  if (['overdue', 'blocked', 'lost', 'discarded', 'unmatched', 'expired'].includes(value)) {
    return 'tone tone--critical';
  }
  if (['queued', 'reserved', 'processing', 'draft'].includes(value)) {
    return 'tone tone--warning';
  }
  return 'tone tone--neutral';
}

function StatCard(props: { label: string; value: string; detail: string }) {
  return (
    <article className="stat-card">
      <span className="stat-card__label">{props.label}</span>
      <strong className="stat-card__value">{props.value}</strong>
      <span className="stat-card__detail">{props.detail}</span>
    </article>
  );
}

function Panel(props: { eyebrow: string; title: string; subtitle: string; children: ReactNode }) {
  return (
    <section className="panel-card">
      <div className="panel-card__header">
        <span className="eyebrow">{props.eyebrow}</span>
        <h2>{props.title}</h2>
        <p>{props.subtitle}</p>
      </div>
      {props.children}
    </section>
  );
}

export default function App() {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1';
  const [token, setToken] = useState(() => {
    if (typeof window === 'undefined') {
      return '';
    }
    return window.localStorage.getItem(tokenStorageKey) || '';
  });
  const [activeSection, setActiveSection] = useState<SectionKey>('overview');
  const [sessionUser, setSessionUser] = useState<User | null>(null);
  const [summary, setSummary] = useState<DashboardOverview | null>(null);
  const [branches, setBranches] = useState<LibraryBranch[]>([]);
  const [authors, setAuthors] = useState<Author[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [records, setRecords] = useState<BibliographicRecord[]>([]);
  const [copies, setCopies] = useState<ItemCopy[]>([]);
  const [patrons, setPatrons] = useState<Patron[]>([]);
  const [patronBlocks, setPatronBlocks] = useState<PatronBlock[]>([]);
  const [loans, setLoans] = useState<Loan[]>([]);
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [campaigns, setCampaigns] = useState<InventoryCampaign[]>([]);
  const [reads, setReads] = useState<InventoryRead[]>([]);
  const [loginForm, setLoginForm] = useState({ email: '', password: '' });
  const [loanForm, setLoanForm] = useState({
    patron: '',
    item_copy: '',
    due_at: toDateTimeLocalValue(new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)),
  });
  const [returnForm, setReturnForm] = useState({ loan: '', notes: '' });
  const [reservationForm, setReservationForm] = useState({ patron: '', bibliographic_record: '', pickup_branch: '', expires_at: '' });
  const [campaignForm, setCampaignForm] = useState({
    library_branch: '',
    name: '',
    status: 'active',
    notes: '',
  });
  const [scanForm, setScanForm] = useState({
    campaign_id: '',
    scanned_code: '',
    scan_source: 'patrimony',
    device_label: 'coletor-01',
  });
  const [tokenLookup, setTokenLookup] = useState('');
  const [lookupResult, setLookupResult] = useState<ReturnReceiptLookup | null>(null);
  const [catalogSearch, setCatalogSearch] = useState('');
  const [inventorySearch, setInventorySearch] = useState('');
  const [loading, setLoading] = useState(Boolean(token));
  const [busyAction, setBusyAction] = useState('');
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [lastSyncAt, setLastSyncAt] = useState('');

  const deferredCatalogSearch = useDeferredValue(catalogSearch);
  const deferredInventorySearch = useDeferredValue(inventorySearch);
  const loadWorkspace = useCallback(async () => {
    if (!token) {
      return;
    }

    setLoading(true);
    setError('');

    try {
      const nextApi = createApiClient({ baseUrl: apiBaseUrl, token });
      const [summaryData, me, branchData, authorData, subjectData, recordData, copyData, patronData, patronBlockData, loanData, reservationData, campaignData, readData] = await Promise.all([
        nextApi.getDashboardOverview(),
        nextApi.me(),
        nextApi.listBranches(),
        nextApi.listAuthors(),
        nextApi.listSubjects(),
        nextApi.listRecords(),
        nextApi.listCopies(),
        nextApi.listPatrons(),
        nextApi.listPatronBlocks(),
        nextApi.listLoans(),
        nextApi.listReservations(),
        nextApi.listInventoryCampaigns(),
        nextApi.listInventoryReads(),
      ]);

      setSummary(summaryData);
      setSessionUser(me);
      setBranches(branchData);
      setAuthors(authorData);
      setSubjects(subjectData);
      setRecords(recordData);
      setCopies(copyData);
      setPatrons(patronData);
      setPatronBlocks(patronBlockData);
      setLoans(loanData);
      setReservations(reservationData);
      setCampaigns(campaignData);
      setReads(readData);
      setLastSyncAt(summaryData.generated_at || new Date().toISOString());
      setCampaignForm((current) =>
        current.library_branch || !branchData[0] ? current : { ...current, library_branch: branchData[0].id },
      );
      setReservationForm((current) =>
        current.pickup_branch || !branchData[0] ? current : { ...current, pickup_branch: branchData[0].id },
      );
      setScanForm((current) =>
        current.campaign_id || !campaignData[0] ? current : { ...current, campaign_id: campaignData[0].id },
      );
    } catch (caughtError) {
      const friendlyMessage = caughtError instanceof ApiError ? caughtError.message : 'Nao foi possivel sincronizar o backoffice.';
      setError(friendlyMessage);
      if (caughtError instanceof ApiError && caughtError.status === 401) {
        setToken('');
      }
    } finally {
      setLoading(false);
    }
  }, [apiBaseUrl, token]);

  const api = createApiClient({ baseUrl: apiBaseUrl, token });

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }

    if (token) {
      window.localStorage.setItem(tokenStorageKey, token);
    } else {
      window.localStorage.removeItem(tokenStorageKey);
    }
  }, [token]);

  useEffect(() => {
    if (!token) {
      setSessionUser(null);
      setSummary(null);
      setAuthors([]);
      setSubjects([]);
      return;
    }

    void loadWorkspace();
  }, [token, loadWorkspace]);

  async function handleLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusyAction('login');
    setError('');
    setMessage('');

    try {
      const response = await api.login(loginForm.email, loginForm.password);
      setToken(response.token);
      setSessionUser(response.user);
      setMessage('Sessao iniciada com sucesso.');
    } catch (caughtError) {
      setError(caughtError instanceof ApiError ? caughtError.message : 'Nao foi possivel autenticar o operador.');
    } finally {
      setBusyAction('');
    }
  }

  async function handleLogout() {
    setBusyAction('logout');
    setError('');
    setMessage('');

    try {
      await api.logout();
    } catch {
      // If the backend token is gone already, local cleanup is still valid.
    } finally {
      setToken('');
      setSessionUser(null);
      setBusyAction('');
      setMessage('Sessao encerrada.');
    }
  }

  async function handleCreateLoan(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusyAction('loan');
    setError('');
    setMessage('');

    try {
      await api.createLoan({
        patron: loanForm.patron,
        item_copy: loanForm.item_copy,
        due_at: toApiDateTime(loanForm.due_at),
      });
      setMessage('Emprestimo registrado e notificacao enviada.');
      setLoanForm((current) => ({ ...current, item_copy: '' }));
      await loadWorkspace();
    } catch (caughtError) {
      setError(caughtError instanceof ApiError ? caughtError.message : 'Falha ao registrar emprestimo.');
    } finally {
      setBusyAction('');
    }
  }

  async function handleCreateReservation(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusyAction('reservation');
    setError('');
    setMessage('');

    try {
      await api.createReservation({
        patron: reservationForm.patron,
        bibliographic_record: reservationForm.bibliographic_record,
        pickup_branch: reservationForm.pickup_branch,
        expires_at: reservationForm.expires_at ? toApiDateTime(`${reservationForm.expires_at}T12:00`) : null,
      });
      setMessage('Reserva registrada com sucesso.');
      setReservationForm((current) => ({ ...current, bibliographic_record: '', expires_at: '' }));
      await loadWorkspace();
    } catch (caughtError) {
      setError(caughtError instanceof ApiError ? caughtError.message : 'Falha ao registrar reserva.');
    } finally {
      setBusyAction('');
    }
  }

  async function handleRegisterReturn(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusyAction('return');
    setError('');
    setMessage('');

    try {
      const receipt = await api.createReturnReceipt(returnForm);
      setLookupResult(await api.lookupReturnToken(receipt.return_token));
      setMessage('Devolucao confirmada com token auditavel.');
      setReturnForm({ loan: '', notes: '' });
      await loadWorkspace();
    } catch (caughtError) {
      setError(caughtError instanceof ApiError ? caughtError.message : 'Falha ao registrar devolucao.');
    } finally {
      setBusyAction('');
    }
  }

  async function handleLookupToken(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusyAction('token');
    setError('');
    setMessage('');

    try {
      const payload = await api.lookupReturnToken(tokenLookup.trim());
      setLookupResult(payload);
      setMessage('Token localizado com sucesso.');
    } catch (caughtError) {
      setLookupResult(null);
      setError(caughtError instanceof ApiError ? caughtError.message : 'Nao foi possivel localizar o token informado.');
    } finally {
      setBusyAction('');
    }
  }

  async function handleCreateCampaign(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusyAction('campaign');
    setError('');
    setMessage('');

    try {
      const created = await api.createInventoryCampaign({
        library_branch: campaignForm.library_branch,
        name: campaignForm.name,
        status: campaignForm.status as 'draft' | 'active' | 'closed',
        notes: campaignForm.notes,
      });
      setScanForm((current) => ({ ...current, campaign_id: created.id }));
      setCampaignForm((current) => ({ ...current, name: '', notes: '' }));
      setMessage('Campanha de inventario criada.');
      await loadWorkspace();
    } catch (caughtError) {
      setError(caughtError instanceof ApiError ? caughtError.message : 'Falha ao criar campanha de inventario.');
    } finally {
      setBusyAction('');
    }
  }

  async function handleRegisterScan(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusyAction('scan');
    setError('');
    setMessage('');

    try {
      await api.createInventoryScan({
        campaign_id: scanForm.campaign_id,
        scanned_code: scanForm.scanned_code,
        scan_source: scanForm.scan_source as 'patrimony' | 'barcode' | 'rfid' | 'camera' | 'manual',
        device_label: scanForm.device_label,
      });
      setScanForm((current) => ({ ...current, scanned_code: '' }));
      setMessage('Leitura patrimonial registrada.');
      await loadWorkspace();
    } catch (caughtError) {
      setError(caughtError instanceof ApiError ? caughtError.message : 'Falha ao registrar leitura de inventario.');
    } finally {
      setBusyAction('');
    }
  }

  async function handleExportCampaign(campaignId: string) {
    setBusyAction(`export-${campaignId}`);
    setError('');
    setMessage('');

    try {
      const blob = await api.downloadInventoryReadsCsv(campaignId);
      const url = window.URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = `inventario-${campaignId}.csv`;
      anchor.click();
      window.URL.revokeObjectURL(url);
      setMessage('CSV do inventario exportado.');
    } catch (caughtError) {
      setError(caughtError instanceof ApiError ? caughtError.message : 'Falha ao exportar o inventario.');
    } finally {
      setBusyAction('');
    }
  }

  const availableCopies = copies.filter((copy) => copy.status === 'available');
  const activeLoans = loans.filter((loan) => loan.status !== 'returned');
  const overdueLoans = loans.filter((loan) => loan.status === 'overdue');
  const activeBlocks = patronBlocks.filter((block) => block.is_active);
  const matchedReads = reads.filter((read) => read.match_status === 'matched');
  const dashboardOverview = summary ?? {
    generated_at: lastSyncAt,
    institutions: 0,
    branches: branches.length,
    active_branches: branches.filter((branch) => branch.is_active).length,
    bibliographic_records: records.length,
    item_copies: copies.length,
    available_copies: availableCopies.length,
    active_loans: activeLoans.length,
    overdue_loans: overdueLoans.length,
    queued_reservations: reservations.filter((reservation) => reservation.status === 'queued').length,
    active_blocks: activeBlocks.length,
    active_inventory_campaigns: campaigns.filter((campaign) => campaign.status === 'active').length,
    matched_inventory_reads: matchedReads.length,
    unmatched_inventory_reads: reads.filter((read) => read.match_status === 'unmatched').length,
    inventory_accuracy_rate: reads.length ? Number(((matchedReads.length / reads.length) * 100).toFixed(1)) : 0,
  };

  const filteredRecords = records.filter((record) => {
    const query = deferredCatalogSearch.trim().toLowerCase();
    if (!query) {
      return true;
    }
    return [record.title, record.subtitle, record.isbn, record.publisher].join(' ').toLowerCase().includes(query);
  });
  const filteredCopies = copies.filter((copy) => {
    const query = deferredCatalogSearch.trim().toLowerCase();
    if (!query) {
      return true;
    }
    return [copy.asset_code, copy.bibliographic_title, copy.barcode || '', copy.rfid_tag || '', copy.tomb_number || '']
      .join(' ')
      .toLowerCase()
      .includes(query);
  });
  const filteredReads = reads.filter((read) => {
    const query = deferredInventorySearch.trim().toLowerCase();
    if (!query) {
      return true;
    }
    return [read.scanned_code, read.item_asset_code, read.item_title, read.device_label].join(' ').toLowerCase().includes(query);
  });

  if (!token) {
    return (
      <main className="auth-shell">
        <section className="auth-panel auth-panel--hero">
          <span className="eyebrow">IFMS Biblioteca Plataforma</span>
          <h1>Backoffice bibliotecario desenhado para superar o legado.</h1>
          <p>
            Circulacao, catalogacao, inventario patrimonial, tokens de devolucao, automacoes e rastreabilidade em um fluxo unico.
          </p>
          <div className="hero-grid">
            <div>
              <strong>Scanner anual</strong>
              <p>Conferencia de patrimonio por etiqueta, barras, RFID ou entrada manual.</p>
            </div>
            <div>
              <strong>Motor operacional</strong>
              <p>Bloqueios por atraso, recibos auditaveis e notificacoes automaticas.</p>
            </div>
            <div>
              <strong>Painel vivo</strong>
              <p>Um cockpit claro para biblioteca escolar, universitaria e multicampi.</p>
            </div>
          </div>
        </section>
        <section className="auth-panel auth-panel--form">
          <span className="eyebrow">Acesso do operador</span>
          <h2>Entrar no centro de operacoes</h2>
          <p className="auth-caption">
            API atual: <code>{apiBaseUrl}</code>
          </p>
          <form className="stack-form" onSubmit={handleLogin}>
            <label>
              <span>E-mail institucional</span>
              <input
                type="email"
                value={loginForm.email}
                onChange={(event) => setLoginForm((current) => ({ ...current, email: event.target.value }))}
                placeholder="bibliotecario@ifms.edu.br"
                required
              />
            </label>
            <label>
              <span>Senha</span>
              <input
                type="password"
                value={loginForm.password}
                onChange={(event) => setLoginForm((current) => ({ ...current, password: event.target.value }))}
                placeholder="Sua senha"
                required
              />
            </label>
            {error ? <div className="banner banner--error">{error}</div> : null}
            {message ? <div className="banner banner--success">{message}</div> : null}
            <button className="primary-button" type="submit" disabled={busyAction === 'login'}>
              {busyAction === 'login' ? 'Autenticando...' : 'Entrar'}
            </button>
          </form>
        </section>
      </main>
    );
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar__brand">
          <span className="eyebrow">melhor que o mercado</span>
          <h1>Biblioteca IFMS</h1>
          <p>Plataforma operacional para acervo, atendimento e inventario patrimonial.</p>
        </div>
        <nav className="sidebar__nav">
          {sectionOrder.map((sectionKey) => (
            <button
              key={sectionKey}
              className={sectionKey === activeSection ? 'nav-pill nav-pill--active' : 'nav-pill'}
              onClick={() => setActiveSection(sectionKey)}
              type="button"
            >
              {sectionLabels[sectionKey]}
            </button>
          ))}
        </nav>
        <div className="sidebar__footer">
          <span>{displayUserName(sessionUser)}</span>
          <small>{sessionUser?.role || 'operador'}</small>
        </div>
      </aside>

      <main className="workspace">
        <header className="workspace__header">
          <div>
            <span className="eyebrow">centro de comando</span>
            <h2>{sectionLabels[activeSection]}</h2>
            <p>Ultima sincronizacao: {lastSyncAt ? formatDateTime(lastSyncAt) : 'aguardando primeira carga'}.</p>
          </div>
          <div className="workspace__actions">
            <button className="secondary-button" type="button" onClick={() => void loadWorkspace()} disabled={loading}>
              {loading ? 'Sincronizando...' : 'Atualizar dados'}
            </button>
            <button className="ghost-button" type="button" onClick={() => void handleLogout()} disabled={busyAction === 'logout'}>
              Sair
            </button>
          </div>
        </header>

        {error ? <div className="banner banner--error">{error}</div> : null}
        {message ? <div className="banner banner--success">{message}</div> : null}

        <section className="stats-grid">
          <StatCard label="Acervo bibliografico" value={String(dashboardOverview.bibliographic_records)} detail={`${dashboardOverview.available_copies} exemplares disponiveis agora`} />
          <StatCard label="Circulacao viva" value={String(dashboardOverview.active_loans)} detail={`${dashboardOverview.overdue_loans} emprestimos em atraso`} />
          <StatCard label="Leitores bloqueados" value={String(dashboardOverview.active_blocks)} detail="bloqueios automaticos e administrativos" />
          <StatCard label="Inventario anual" value={String(dashboardOverview.active_inventory_campaigns)} detail={`${dashboardOverview.matched_inventory_reads} leituras conciliadas`} />
        </section>

        {activeSection === 'overview' ? (
          <div className="content-grid content-grid--overview">
            <Panel eyebrow="saude operacional" title="Onde agir primeiro" subtitle="Priorizacao rapida para atendimento, acervo e inventario.">
              <div className="alert-stack">
                <div className="alert-row">
                  <strong>{dashboardOverview.overdue_loans}</strong>
                  <div>
                    <span>Atrasos com impacto direto</span>
                    <p>Emprestimos vencidos ja alimentam multa e bloqueio automatico.</p>
                  </div>
                </div>
                <div className="alert-row">
                  <strong>{dashboardOverview.queued_reservations}</strong>
                  <div>
                    <span>Reservas na fila</span>
                    <p>Fila ativa para atendimento, separacao de exemplares e comunicacao.</p>
                  </div>
                </div>
                <div className="alert-row">
                  <strong>{dashboardOverview.unmatched_inventory_reads}</strong>
                  <div>
                    <span>Divergencias de patrimonio</span>
                    <p>Etiquetas ainda sem conciliacao no inventario anual.</p>
                  </div>
                </div>
              </div>
            </Panel>

            <Panel eyebrow="topo de fila" title="Emprestimos que merecem intervencao" subtitle="Recorte rapido para atendimento e comunicacao ativa.">
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Leitor</th>
                      <th>Exemplar</th>
                      <th>Vencimento</th>
                      <th>Status</th>
                      <th>Multa</th>
                    </tr>
                  </thead>
                  <tbody>
                    {loans.slice(0, 6).map((loan) => (
                      <tr key={loan.id}>
                        <td>{loan.patron_name}</td>
                        <td>{loan.item_asset_code}</td>
                        <td>{formatDateTime(loan.due_at)}</td>
                        <td><span className={toneClass(loan.status)}>{loan.status}</span></td>
                        <td>{formatCurrency(loan.fine_amount)}</td>
                      </tr>
                    ))}
                    {loans.length === 0 ? (
                      <tr>
                        <td colSpan={5}>Nenhum emprestimo carregado.</td>
                      </tr>
                    ) : null}
                  </tbody>
                </table>
              </div>
            </Panel>

            <Panel eyebrow="governanca" title="Bloqueios e causas" subtitle="Leitores com restricao ativa para tomada de decisao institucional.">
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Leitor</th>
                      <th>Motivo</th>
                      <th>Ativo</th>
                      <th>Criado em</th>
                    </tr>
                  </thead>
                  <tbody>
                    {activeBlocks.slice(0, 6).map((block) => {
                      const patron = patrons.find((item) => item.id === block.patron);
                      return (
                        <tr key={block.id}>
                          <td>{patron?.full_name || block.patron}</td>
                          <td>{block.reason}</td>
                          <td><span className={toneClass(block.is_active ? 'blocked' : 'active')}>{block.is_active ? 'ativo' : 'inativo'}</span></td>
                          <td>{formatDateTime(block.created_at)}</td>
                        </tr>
                      );
                    })}
                    {activeBlocks.length === 0 ? (
                      <tr>
                        <td colSpan={4}>Nenhum bloqueio ativo neste momento.</td>
                      </tr>
                    ) : null}
                  </tbody>
                </table>
              </div>
            </Panel>
          </div>
        ) : null}

        {activeSection === 'circulation' ? (
          <div className="content-grid">
            <Panel eyebrow="balcao" title="Novo emprestimo" subtitle="Seleciona leitor e exemplar disponivel. O backend ajusta status e notificacao.">
              <form className="stack-form" onSubmit={handleCreateLoan}>
                <label>
                  <span>Leitor</span>
                  <select value={loanForm.patron} onChange={(event) => setLoanForm((current) => ({ ...current, patron: event.target.value }))} required>
                    <option value="">Selecione um leitor</option>
                    {patrons.map((patron) => (
                      <option key={patron.id} value={patron.id}>{patron.full_name} - {patron.registration_code}</option>
                    ))}
                  </select>
                </label>
                <label>
                  <span>Exemplar disponivel</span>
                  <select value={loanForm.item_copy} onChange={(event) => setLoanForm((current) => ({ ...current, item_copy: event.target.value }))} required>
                    <option value="">Selecione um exemplar</option>
                    {availableCopies.map((copy) => (
                      <option key={copy.id} value={copy.id}>{copy.asset_code} - {copy.bibliographic_title}</option>
                    ))}
                  </select>
                </label>
                <label>
                  <span>Data limite</span>
                  <input type="datetime-local" value={loanForm.due_at} onChange={(event) => setLoanForm((current) => ({ ...current, due_at: event.target.value }))} required />
                </label>
                <button className="primary-button" type="submit" disabled={busyAction === 'loan'}>
                  {busyAction === 'loan' ? 'Registrando...' : 'Registrar emprestimo'}
                </button>
              </form>
            </Panel>

            <Panel eyebrow="fila de espera" title="Registrar reserva" subtitle="Monta a fila por titulo e define a biblioteca de retirada.">
              <form className="stack-form" onSubmit={handleCreateReservation}>
                <label>
                  <span>Leitor</span>
                  <select value={reservationForm.patron} onChange={(event) => setReservationForm((current) => ({ ...current, patron: event.target.value }))} required>
                    <option value="">Selecione um leitor</option>
                    {patrons.map((patron) => (
                      <option key={patron.id} value={patron.id}>{patron.full_name} - {patron.registration_code}</option>
                    ))}
                  </select>
                </label>
                <label>
                  <span>Titulo</span>
                  <select value={reservationForm.bibliographic_record} onChange={(event) => setReservationForm((current) => ({ ...current, bibliographic_record: event.target.value }))} required>
                    <option value="">Selecione um registro</option>
                    {records.map((record) => (
                      <option key={record.id} value={record.id}>{record.title}</option>
                    ))}
                  </select>
                </label>
                <label>
                  <span>Biblioteca de retirada</span>
                  <select value={reservationForm.pickup_branch} onChange={(event) => setReservationForm((current) => ({ ...current, pickup_branch: event.target.value }))} required>
                    <option value="">Selecione uma biblioteca</option>
                    {branches.map((branch) => (
                      <option key={branch.id} value={branch.id}>{branch.institution_name} - {branch.campus_name} - {branch.name}</option>
                    ))}
                  </select>
                </label>
                <label>
                  <span>Expira em</span>
                  <input type="date" value={reservationForm.expires_at} onChange={(event) => setReservationForm((current) => ({ ...current, expires_at: event.target.value }))} />
                </label>
                <button className="primary-button" type="submit" disabled={busyAction === 'reservation'}>
                  {busyAction === 'reservation' ? 'Registrando...' : 'Registrar reserva'}
                </button>
              </form>
            </Panel>

            <Panel eyebrow="retorno auditavel" title="Registrar devolucao" subtitle="Ao devolver, o sistema gera recibo, token publico e reavalia bloqueios.">
              <form className="stack-form" onSubmit={handleRegisterReturn}>
                <label>
                  <span>Emprestimo aberto</span>
                  <select value={returnForm.loan} onChange={(event) => setReturnForm((current) => ({ ...current, loan: event.target.value }))} required>
                    <option value="">Selecione um emprestimo</option>
                    {activeLoans.map((loan) => (
                      <option key={loan.id} value={loan.id}>{loan.patron_name} - {loan.item_asset_code}</option>
                    ))}
                  </select>
                </label>
                <label>
                  <span>Observacoes</span>
                  <textarea value={returnForm.notes} onChange={(event) => setReturnForm((current) => ({ ...current, notes: event.target.value }))} rows={3} placeholder="Conservacao, avaria, observacoes do atendimento..." />
                </label>
                <button className="primary-button" type="submit" disabled={busyAction === 'return'}>
                  {busyAction === 'return' ? 'Processando...' : 'Confirmar devolucao'}
                </button>
              </form>
            </Panel>

            <Panel eyebrow="fila ativa" title="Reservas em aberto" subtitle="Acompanha posicao na fila e disponibilidade por titulo.">
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Leitor</th>
                      <th>Titulo</th>
                      <th>Status</th>
                      <th>Fila</th>
                      <th>Retirada</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reservations.slice(0, 8).map((reservation) => {
                      const branch = branches.find((item) => item.id === reservation.pickup_branch);
                      return (
                        <tr key={reservation.id}>
                          <td>{reservation.patron_name}</td>
                          <td>{reservation.record_title}</td>
                          <td><span className={toneClass(reservation.status)}>{reservation.status}</span></td>
                          <td>{reservation.queue_position}</td>
                          <td>{branch ? `${branch.campus_name} - ${branch.name}` : reservation.pickup_branch}</td>
                        </tr>
                      );
                    })}
                    {reservations.length === 0 ? (
                      <tr>
                        <td colSpan={5}>Nenhuma reserva registrada.</td>
                      </tr>
                    ) : null}
                  </tbody>
                </table>
              </div>
            </Panel>

            <Panel eyebrow="consulta publica" title="Validar token de devolucao" subtitle="O mesmo token pode ser conferido por bibliotecario, auditoria ou portal do leitor.">
              <form className="stack-form" onSubmit={handleLookupToken}>
                <label>
                  <span>Token</span>
                  <input value={tokenLookup} onChange={(event) => setTokenLookup(event.target.value)} placeholder="Cole o token emitido no recibo" required />
                </label>
                <button className="secondary-button" type="submit" disabled={busyAction === 'token'}>
                  {busyAction === 'token' ? 'Buscando...' : 'Consultar token'}
                </button>
              </form>
              {lookupResult ? (
                <div className="token-card">
                  <strong>{lookupResult.record_title}</strong>
                  <p>{lookupResult.patron_name} - exemplar {lookupResult.item_asset_code}</p>
                  <p>Recebido em {formatDateTime(lookupResult.created_at)}</p>
                  <code>{lookupResult.return_token}</code>
                </div>
              ) : null}
            </Panel>
          </div>
        ) : null}
        {activeSection === 'catalog' ? (
          <CatalogOperationsSection
            api={api}
            branches={branches}
            authors={authors}
            subjects={subjects}
            records={records}
            filteredRecords={filteredRecords}
            filteredCopies={filteredCopies}
            catalogSearch={catalogSearch}
            onCatalogSearchChange={setCatalogSearch}
            onChanged={loadWorkspace}
            onMessage={setMessage}
            onError={setError}
          />
        ) : null}

        {activeSection === 'patrons' ? (
          <PatronOperationsSection
            api={api}
            branches={branches}
            patrons={patrons}
            onChanged={loadWorkspace}
            onMessage={setMessage}
            onError={setError}
          />
        ) : null}

        {activeSection === 'operators' ? (
          <OperatorOperationsSection
            api={api}
            branches={branches}
            currentUser={sessionUser}
            onMessage={setMessage}
            onError={setError}
          />
        ) : null}

        {activeSection === 'inventory' ? (
          <div className="content-grid">
            <Panel eyebrow="preparacao" title="Abrir campanha patrimonial" subtitle="Cada campanha organiza o inventario anual por biblioteca.">
              <form className="stack-form" onSubmit={handleCreateCampaign}>
                <label>
                  <span>Biblioteca</span>
                  <select value={campaignForm.library_branch} onChange={(event) => setCampaignForm((current) => ({ ...current, library_branch: event.target.value }))} required>
                    <option value="">Selecione uma biblioteca</option>
                    {branches.map((branch) => (
                      <option key={branch.id} value={branch.id}>{branch.institution_name} - {branch.campus_name} - {branch.name}</option>
                    ))}
                  </select>
                </label>
                <label>
                  <span>Nome da campanha</span>
                  <input value={campaignForm.name} onChange={(event) => setCampaignForm((current) => ({ ...current, name: event.target.value }))} placeholder="Inventario anual 2026" required />
                </label>
                <label>
                  <span>Status inicial</span>
                  <select value={campaignForm.status} onChange={(event) => setCampaignForm((current) => ({ ...current, status: event.target.value }))}>
                    <option value="draft">draft</option>
                    <option value="active">active</option>
                    <option value="closed">closed</option>
                  </select>
                </label>
                <label>
                  <span>Notas</span>
                  <textarea value={campaignForm.notes} onChange={(event) => setCampaignForm((current) => ({ ...current, notes: event.target.value }))} rows={3} placeholder="Escopo, corredor, colecao, observacoes da equipe..." />
                </label>
                <button className="primary-button" type="submit" disabled={busyAction === 'campaign'}>
                  {busyAction === 'campaign' ? 'Criando...' : 'Criar campanha'}
                </button>
              </form>
            </Panel>

            <Panel eyebrow="coletor" title="Scanner de patrimonio" subtitle="Leitura por etiqueta patrimonial, RFID, barras ou digitacao manual.">
              <form className="stack-form" onSubmit={handleRegisterScan}>
                <label>
                  <span>Campanha alvo</span>
                  <select value={scanForm.campaign_id} onChange={(event) => setScanForm((current) => ({ ...current, campaign_id: event.target.value }))} required>
                    <option value="">Selecione uma campanha</option>
                    {campaigns.map((campaign) => (
                      <option key={campaign.id} value={campaign.id}>{campaign.name} - {campaign.status}</option>
                    ))}
                  </select>
                </label>
                <label>
                  <span>Codigo lido</span>
                  <input value={scanForm.scanned_code} onChange={(event) => setScanForm((current) => ({ ...current, scanned_code: event.target.value }))} placeholder="Etiqueta patrimonial, RFID ou barras" required />
                </label>
                <label>
                  <span>Origem da leitura</span>
                  <select value={scanForm.scan_source} onChange={(event) => setScanForm((current) => ({ ...current, scan_source: event.target.value }))}>
                    {Object.entries(scanSourceLabels).map(([value, label]) => (
                      <option key={value} value={value}>{label}</option>
                    ))}
                  </select>
                </label>
                <label>
                  <span>Dispositivo</span>
                  <input value={scanForm.device_label} onChange={(event) => setScanForm((current) => ({ ...current, device_label: event.target.value }))} placeholder="coletor-01" />
                </label>
                <button className="primary-button" type="submit" disabled={busyAction === 'scan'}>
                  {busyAction === 'scan' ? 'Gravando...' : 'Registrar leitura'}
                </button>
              </form>
            </Panel>

            <Panel eyebrow="conciliacao" title="Campanhas e exportacoes" subtitle="Acompanha a operacao e gera CSV para auditoria anual.">
              <div className="campaign-stack">
                {campaigns.map((campaign) => (
                  <article key={campaign.id} className="campaign-card">
                    <div>
                      <strong>{campaign.name}</strong>
                      <p>
                        {formatDateTime(campaign.created_at)} - <span className={toneClass(campaign.status)}>{campaign.status}</span>
                      </p>
                    </div>
                    <button className="ghost-button" type="button" onClick={() => void handleExportCampaign(campaign.id)} disabled={busyAction === `export-${campaign.id}`}>
                      {busyAction === `export-${campaign.id}` ? 'Exportando...' : 'Exportar CSV'}
                    </button>
                  </article>
                ))}
                {campaigns.length === 0 ? <p>Nenhuma campanha criada ainda.</p> : null}
              </div>
            </Panel>

            <Panel eyebrow="diferencas" title="Leituras recentes" subtitle="Confere rapidamente itens conciliados e codigos sem correspondencia.">
              <label className="inline-field">
                <span>Filtrar leituras</span>
                <input value={inventorySearch} onChange={(event) => setInventorySearch(event.target.value)} placeholder="codigo, titulo ou dispositivo" />
              </label>
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Codigo lido</th>
                      <th>Titulo</th>
                      <th>Origem</th>
                      <th>Match</th>
                      <th>Momento</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredReads.slice(0, 12).map((read) => (
                      <tr key={read.id}>
                        <td>{read.scanned_code}</td>
                        <td>{read.item_title || 'Sem correspondencia'}</td>
                        <td>{scanSourceLabels[read.scan_source] || read.scan_source}</td>
                        <td><span className={toneClass(read.match_status)}>{read.match_status}</span></td>
                        <td>{formatDateTime(read.read_at)}</td>
                      </tr>
                    ))}
                    {filteredReads.length === 0 ? (
                      <tr>
                        <td colSpan={5}>Nenhuma leitura encontrada para o filtro atual.</td>
                      </tr>
                    ) : null}
                  </tbody>
                </table>
              </div>
            </Panel>
          </div>
        ) : null}
      </main>
    </div>
  );
}


