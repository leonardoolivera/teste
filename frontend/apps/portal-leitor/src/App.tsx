import { useDeferredValue, useEffect, useEffectEvent, useState } from 'react';
import type { FormEvent } from 'react';
import {
  ApiError,
  createApiClient,
  formatDateTime,
  formatCurrency,
} from '@biblioteca-ifms/shared';
import type {
  BibliographicRecord,
  ItemCopy,
  LibraryBranch,
  PatronMe,
  PatronPortalLoan,
  PatronPortalReservation,
  ReturnReceiptLookup,
} from '@biblioteca-ifms/shared';

// ─── Persistência de sessão ───────────────────────────────────────────────────

const SESSION_KEY = 'portal_token';

function loadToken(): string | null {
  try {
    return localStorage.getItem(SESSION_KEY);
  } catch {
    return null;
  }
}

function saveToken(token: string) {
  try {
    localStorage.setItem(SESSION_KEY, token);
  } catch { /* noop */ }
}

function clearToken() {
  try {
    localStorage.removeItem(SESSION_KEY);
  } catch { /* noop */ }
}

// ─── Tipos de view ────────────────────────────────────────────────────────────

type View = 'public' | 'login' | 'set-password' | 'account';

// ─── Helpers ──────────────────────────────────────────────────────────────────

function branchLabel(branches: LibraryBranch[], branchId: string) {
  const branch = branches.find((b) => b.id === branchId);
  if (!branch) return 'Unidade nao identificada';
  return `${branch.campus_name} - ${branch.name}`;
}

function loanStatusLabel(status: string) {
  if (status === 'open') return 'Em aberto';
  if (status === 'overdue') return 'Atrasado';
  if (status === 'returned') return 'Devolvido';
  return status;
}

function reservationStatusLabel(status: string) {
  if (status === 'queued') return 'Na fila';
  if (status === 'available') return 'Disponivel para retirada';
  if (status === 'fulfilled') return 'Retirado';
  if (status === 'expired') return 'Expirado';
  if (status === 'canceled') return 'Cancelado';
  return status;
}

// ─── App ──────────────────────────────────────────────────────────────────────

export default function App() {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1';

  // Sessão
  const [token, setToken] = useState<string | null>(loadToken);
  const [patron, setPatron] = useState<PatronMe | null>(null);
  const [view, setView] = useState<View>(token ? 'account' : 'public');

  // Dados públicos
  const [records, setRecords] = useState<BibliographicRecord[]>([]);
  const [copies, setCopies] = useState<ItemCopy[]>([]);
  const [branches, setBranches] = useState<LibraryBranch[]>([]);
  const [search, setSearch] = useState('');
  const [selectedBranch, setSelectedBranch] = useState('');
  const [tokenLookup, setTokenLookup] = useState('');
  const [lookupResult, setLookupResult] = useState<ReturnReceiptLookup | null>(null);
  const [publicLoading, setPublicLoading] = useState(true);

  // Minha conta
  const [myLoans, setMyLoans] = useState<PatronPortalLoan[]>([]);
  const [myReservations, setMyReservations] = useState<PatronPortalReservation[]>([]);
  const [accountLoading, setAccountLoading] = useState(false);
  const [renewingId, setRenewingId] = useState<string | null>(null);

  // Forms de auth
  const [regCode, setRegCode] = useState('');
  const [password, setPassword] = useState('');
  const [authBusy, setAuthBusy] = useState(false);

  // Feedback
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);

  const deferredSearch = useDeferredValue(search);

  // ── Cria client com token ──
  const api = createApiClient({ baseUrl: apiBaseUrl, token: token ?? undefined });

  // ── Carrega dados públicos ──
  const loadPublicData = useEffectEvent(async () => {
    setPublicLoading(true);
    setError('');
    try {
      const [recordData, copyData, branchData] = await Promise.all([
        api.listRecords(),
        api.listCopies(),
        api.listBranches(),
      ]);
      setRecords(recordData);
      setCopies(copyData);
      setBranches(branchData);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Nao foi possivel carregar o portal.');
    } finally {
      setPublicLoading(false);
    }
  });

  useEffect(() => {
    void loadPublicData();
  }, []);

  // ── Carrega dados da conta ──
  const loadAccountData = useEffectEvent(async (authToken: string) => {
    const authedApi = createApiClient({ baseUrl: apiBaseUrl, token: authToken });
    setAccountLoading(true);
    setError('');
    try {
      const [loans, reservations, me] = await Promise.all([
        authedApi.patronMyLoans(),
        authedApi.patronMyReservations(),
        authedApi.patronMe(),
      ]);
      setMyLoans(loans);
      setMyReservations(reservations);
      setPatron(me);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Nao foi possivel carregar sua conta.');
      if (e instanceof ApiError && e.status === 401) {
        handleLogout();
      }
    } finally {
      setAccountLoading(false);
    }
  });

  useEffect(() => {
    if (view === 'account' && token) {
      void loadAccountData(token);
    }
  }, [view, token]);

  // ── Auth handlers ──

  function handleLogout() {
    clearToken();
    setToken(null);
    setPatron(null);
    setMyLoans([]);
    setMyReservations([]);
    setView('public');
    setError('');
    setMessage('');
  }

  async function handleLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setAuthBusy(true);
    setError('');
    try {
      const res = await api.patronLogin(regCode.trim(), password);
      saveToken(res.token);
      setToken(res.token);
      setPatron(res.patron);
      setView('account');
      setRegCode('');
      setPassword('');
    } catch (e) {
      if (e instanceof ApiError) {
        if (e.status === 403 && (e.payload as Record<string, unknown>)?.must_set_password) {
          setView('set-password');
          setError('Voce ainda nao definiu uma senha. Crie uma senha para acessar sua conta.');
        } else {
          setError(e.message);
        }
      } else {
        setError('Nao foi possivel autenticar.');
      }
    } finally {
      setAuthBusy(false);
    }
  }

  async function handleSetPassword(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setAuthBusy(true);
    setError('');
    try {
      const res = await api.patronSetPassword(regCode.trim(), password);
      saveToken(res.token);
      setToken(res.token);
      setPatron(res.patron);
      setView('account');
      setRegCode('');
      setPassword('');
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Nao foi possivel definir a senha.');
    } finally {
      setAuthBusy(false);
    }
  }

  // ── Renovação ──

  async function handleRenew(loanId: string) {
    if (!token) return;
    setRenewingId(loanId);
    setError('');
    setMessage('');
    try {
      const authedApi = createApiClient({ baseUrl: apiBaseUrl, token });
      const updated = await authedApi.patronRenewLoan(loanId);
      setMyLoans((prev) => prev.map((l) => (l.id === loanId ? updated : l)));
      setMessage('Renovacao realizada. Novo vencimento: ' + formatDateTime(updated.due_at));
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Nao foi possivel renovar.');
    } finally {
      setRenewingId(null);
    }
  }

  // ── Lookup token público ──

  async function handleLookupToken(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError('');
    setMessage('');
    try {
      const payload = await api.lookupReturnToken(tokenLookup.trim());
      setLookupResult(payload);
      setMessage('Recibo localizado com sucesso.');
    } catch (e) {
      setLookupResult(null);
      setError(e instanceof ApiError ? e.message : 'Token nao encontrado.');
    } finally {
      setBusy(false);
    }
  }

  // ── Filtros do catálogo ──

  const filteredRecords = records.filter((record) => {
    const q = deferredSearch.trim().toLowerCase();
    if (!q) return true;
    return [record.title, record.subtitle, record.isbn, record.publisher].join(' ').toLowerCase().includes(q);
  });
  const visibleRecords = filteredRecords.filter((record) => {
    if (!selectedBranch) return true;
    return copies.some((c) => c.bibliographic_record === record.id && c.library_branch === selectedBranch);
  });
  const availableCopies = copies.filter((c) => c.status === 'available').length;
  const featuredRecords = visibleRecords.slice(0, 9);

  // ─── Render ────────────────────────────────────────────────────────────────

  return (
    <div className="portal-shell">
      {/* ── Cabeçalho global ── */}
      <header className="hero">
        <div className="hero__copy">
          <span className="eyebrow">portal do leitor</span>
          <h1>Acervo vivo, devolucao auditavel e experiencia melhor que o legado.</h1>
          <p>
            {patron
              ? `Bem-vindo(a), ${patron.full_name}. Aqui voce acessa seus emprestimos, reservas e o catalogo completo.`
              : 'Esta interface conecta o leitor ao catalogo, reforca transparencia nas devolucoes e permite autoatendimento.'}
          </p>
          <div className="hero__stats">
            <article>
              <strong>{records.length}</strong>
              <span>registros bibliograficos</span>
            </article>
            <article>
              <strong>{availableCopies}</strong>
              <span>exemplares disponiveis</span>
            </article>
            <article>
              <strong>{branches.length}</strong>
              <span>bibliotecas conectadas</span>
            </article>
          </div>
        </div>
        <div className="hero__card">
          {patron ? (
            <>
              <span className="eyebrow">sua conta</span>
              <p><strong>{patron.full_name}</strong></p>
              <p>Matricula: {patron.registration_code}</p>
              {patron.library_branch_name && <p>{patron.library_branch_name}</p>}
              <div style={{ marginTop: '1rem', display: 'grid', gap: '0.5rem' }}>
                <button
                  className="primary-button"
                  onClick={() => setView('account')}
                  type="button"
                  style={view === 'account' ? { opacity: 0.6 } : {}}
                >
                  Minha conta
                </button>
                <button
                  className="primary-button"
                  onClick={() => setView('public')}
                  type="button"
                  style={{ background: 'linear-gradient(120deg,#2a7b69,#1f5c46)', ...(view === 'public' ? { opacity: 0.6 } : {}) }}
                >
                  Catalogo publico
                </button>
                <button
                  type="button"
                  onClick={handleLogout}
                  style={{ background: 'none', border: '1px solid rgba(163,80,69,0.35)', borderRadius: '999px', padding: '0.7rem 1rem', color: '#8a3028' }}
                >
                  Sair
                </button>
              </div>
            </>
          ) : (
            <>
              <span className="eyebrow">diferenciais</span>
              <ul>
                <li>Catalogo pesquisavel com base no mesmo dado operacional do backoffice.</li>
                <li>Validacao publica de token de devolucao para auditoria e confianca.</li>
                <li>Arquitetura preparada para RFID, scanner patrimonial e automacoes.</li>
              </ul>
              <div style={{ marginTop: '1rem' }}>
                <button
                  className="primary-button"
                  type="button"
                  onClick={() => { setView('login'); setError(''); }}
                >
                  Entrar na minha conta
                </button>
              </div>
            </>
          )}
        </div>
      </header>

      <main className="portal-content">
        {error ? <div className="banner banner--error">{error}</div> : null}
        {message ? <div className="banner banner--success">{message}</div> : null}

        {/* ── View: Login ── */}
        {view === 'login' && (
          <section className="panel" style={{ maxWidth: 440 }}>
            <span className="eyebrow">acesso do leitor</span>
            <h2>Entrar na minha conta</h2>
            <p>Use sua matricula e senha cadastrada na biblioteca.</p>
            <form className="stack-form" onSubmit={handleLogin}>
              <label>
                <span>Matricula</span>
                <input
                  value={regCode}
                  onChange={(e) => setRegCode(e.target.value)}
                  placeholder="Ex.: 2026001"
                  required
                  autoFocus
                />
              </label>
              <label>
                <span>Senha</span>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Sua senha"
                  required
                />
              </label>
              <button className="primary-button" type="submit" disabled={authBusy}>
                {authBusy ? 'Entrando...' : 'Entrar'}
              </button>
            </form>
            <p style={{ marginTop: '1rem', fontSize: '0.9rem' }}>
              Primeiro acesso?{' '}
              <button
                type="button"
                onClick={() => { setView('set-password'); setError(''); }}
                style={{ background: 'none', border: 'none', padding: 0, color: '#2a7b69', cursor: 'pointer', textDecoration: 'underline' }}
              >
                Defina sua senha aqui.
              </button>
            </p>
            <p style={{ marginTop: '0.5rem', fontSize: '0.9rem' }}>
              <button
                type="button"
                onClick={() => { setView('public'); setError(''); }}
                style={{ background: 'none', border: 'none', padding: 0, color: '#546e61', cursor: 'pointer', textDecoration: 'underline' }}
              >
                Voltar ao catalogo publico
              </button>
            </p>
          </section>
        )}

        {/* ── View: Definir senha (primeiro acesso) ── */}
        {view === 'set-password' && (
          <section className="panel" style={{ maxWidth: 440 }}>
            <span className="eyebrow">primeiro acesso</span>
            <h2>Criar senha de acesso</h2>
            <p>Informe sua matricula e escolha uma senha para acessar o portal.</p>
            <form className="stack-form" onSubmit={handleSetPassword}>
              <label>
                <span>Matricula</span>
                <input
                  value={regCode}
                  onChange={(e) => setRegCode(e.target.value)}
                  placeholder="Ex.: 2026001"
                  required
                  autoFocus
                />
              </label>
              <label>
                <span>Nova senha (minimo 6 caracteres)</span>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Escolha uma senha"
                  required
                  minLength={6}
                />
              </label>
              <button className="primary-button" type="submit" disabled={authBusy}>
                {authBusy ? 'Salvando...' : 'Criar senha e entrar'}
              </button>
            </form>
            <p style={{ marginTop: '1rem', fontSize: '0.9rem' }}>
              Ja tem senha?{' '}
              <button
                type="button"
                onClick={() => { setView('login'); setError(''); }}
                style={{ background: 'none', border: 'none', padding: 0, color: '#2a7b69', cursor: 'pointer', textDecoration: 'underline' }}
              >
                Entrar aqui.
              </button>
            </p>
          </section>
        )}

        {/* ── View: Minha conta ── */}
        {view === 'account' && (
          <>
            {accountLoading ? (
              <p>Carregando sua conta...</p>
            ) : (
              <>
                <section className="panel">
                  <span className="eyebrow">meus emprestimos</span>
                  <h2>Historico de emprestimos</h2>
                  {myLoans.length === 0 ? (
                    <p>Nenhum emprestimo registrado.</p>
                  ) : (
                    <div style={{ display: 'grid', gap: '0.75rem', marginTop: '1rem' }}>
                      {myLoans.map((loan) => (
                        <div key={loan.id} className="receipt-card" style={{ display: 'grid', gap: '0.3rem' }}>
                          <strong>{loan.record_title}</strong>
                          {loan.record_subtitle ? <span style={{ color: '#546e61', fontSize: '0.9rem' }}>{loan.record_subtitle}</span> : null}
                          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', fontSize: '0.88rem', color: '#546e61' }}>
                            <span>Exemplar: {loan.asset_code}</span>
                            {loan.branch_name && <span>{loan.branch_name}</span>}
                            <span>Emprestado em: {formatDateTime(loan.loaned_at)}</span>
                            <span>Vencimento: {formatDateTime(loan.due_at)}</span>
                            <span style={{ fontWeight: 600, color: loan.status === 'overdue' ? '#8a3028' : loan.status === 'returned' ? '#2a7b69' : '#163028' }}>
                              {loanStatusLabel(loan.status)}
                            </span>
                            {Number(loan.fine_amount) > 0 && (
                              <span style={{ color: '#8a3028' }}>Multa: {formatCurrency(loan.fine_amount)}</span>
                            )}
                          </div>
                          {loan.status === 'open' && (
                            <div style={{ marginTop: '0.4rem' }}>
                              <button
                                className="primary-button"
                                type="button"
                                style={{ fontSize: '0.85rem', padding: '0.5rem 1rem' }}
                                disabled={renewingId === loan.id}
                                onClick={() => handleRenew(loan.id)}
                              >
                                {renewingId === loan.id ? 'Renovando...' : 'Renovar (+7 dias)'}
                              </button>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </section>

                <section className="panel">
                  <span className="eyebrow">minhas reservas</span>
                  <h2>Fila de reservas</h2>
                  {myReservations.length === 0 ? (
                    <p>Nenhuma reserva ativa.</p>
                  ) : (
                    <div style={{ display: 'grid', gap: '0.75rem', marginTop: '1rem' }}>
                      {myReservations.map((res) => (
                        <div key={res.id} className="receipt-card" style={{ display: 'grid', gap: '0.3rem' }}>
                          <strong>{res.record_title}</strong>
                          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', fontSize: '0.88rem', color: '#546e61' }}>
                            <span>{res.pickup_branch_name}</span>
                            <span>Posicao na fila: {res.queue_position}</span>
                            {res.expires_at && <span>Expira em: {formatDateTime(res.expires_at)}</span>}
                            <span style={{ fontWeight: 600, color: res.status === 'available' ? '#2a7b69' : res.status === 'expired' ? '#8a3028' : '#163028' }}>
                              {reservationStatusLabel(res.status)}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </section>
              </>
            )}
          </>
        )}

        {/* ── View: Catálogo público ── */}
        {(view === 'public' || view === 'login' || view === 'set-password') && (
          <>
            <section className="panel panel--filters">
              <div>
                <span className="eyebrow">descoberta do acervo</span>
                <h2>Buscar por titulo, ISBN ou editora</h2>
              </div>
              <div className="filter-grid">
                <label>
                  <span>Busca livre</span>
                  <input
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    placeholder="Ex.: algebra linear, Machado de Assis, 978..."
                  />
                </label>
                <label>
                  <span>Filtrar por biblioteca</span>
                  <select value={selectedBranch} onChange={(e) => setSelectedBranch(e.target.value)}>
                    <option value="">Todas as bibliotecas</option>
                    {branches.map((b) => (
                      <option key={b.id} value={b.id}>{branchLabel(branches, b.id)}</option>
                    ))}
                  </select>
                </label>
              </div>
            </section>

            <section className="catalog-grid">
              {publicLoading ? <p>Carregando catalogo publico...</p> : null}
              {!publicLoading && featuredRecords.length === 0 ? <p>Nenhum titulo encontrado para o filtro atual.</p> : null}
              {featuredRecords.map((record) => {
                const recordCopies = copies.filter((c) => c.bibliographic_record === record.id);
                const freeCopies = recordCopies.filter((c) => c.status === 'available');
                const firstBranch = recordCopies[0]?.library_branch;
                return (
                  <article key={record.id} className="catalog-card">
                    <div>
                      <span className="catalog-card__meta">{record.publication_year || 'Ano nao informado'} - {record.language || 'pt-BR'}</span>
                      <h3>{record.title}</h3>
                      <p>{record.subtitle || record.description || 'Registro pronto para enriquecer com resumo, sumario e recomendacoes.'}</p>
                    </div>
                    <div className="catalog-card__footer">
                      <span>{freeCopies.length} disponivel(is)</span>
                      <small>{firstBranch ? branchLabel(branches, firstBranch) : 'Sem unidade vinculada'}</small>
                    </div>
                  </article>
                );
              })}
            </section>

            <section className="portal-grid">
              <article className="panel">
                <span className="eyebrow">recibo digital</span>
                <h2>Conferir token de devolucao</h2>
                <p>Digite o token recebido no atendimento para validar a devolucao registrada pela biblioteca.</p>
                <form className="stack-form" onSubmit={handleLookupToken}>
                  <label>
                    <span>Token</span>
                    <input
                      value={tokenLookup}
                      onChange={(e) => setTokenLookup(e.target.value)}
                      placeholder="Cole aqui o token do recibo"
                      required
                    />
                  </label>
                  <button className="primary-button" type="submit" disabled={busy}>
                    {busy ? 'Consultando...' : 'Validar token'}
                  </button>
                </form>
                {lookupResult ? (
                  <div className="receipt-card">
                    <strong>{lookupResult.record_title}</strong>
                    <p>{lookupResult.patron_name} - exemplar {lookupResult.item_asset_code}</p>
                    <p>Recebido em {formatDateTime(lookupResult.created_at)}</p>
                    <code>{lookupResult.return_token}</code>
                  </div>
                ) : null}
              </article>

              <article className="panel panel--accent">
                <span className="eyebrow">o que vem a seguir</span>
                <h2>Leitor no centro</h2>
                <p>
                  Esta interface nasce conectada ao motor transacional. Acesse sua conta para ver emprestimos, reservas e renovar online.
                </p>
                <div className="roadmap-list">
                  <div>
                    <strong>Reserva inteligente</strong>
                    <p>Fila unica com previsao de disponibilidade e notificacao automatica.</p>
                  </div>
                  <div>
                    <strong>Minha conta</strong>
                    <p>Emprestimos, multas, recibos e alertas em um painel pessoal seguro.</p>
                  </div>
                  <div>
                    <strong>Autoatendimento</strong>
                    <p>Base pronta para kiosks, RFID e fluxos hibridos com atendente.</p>
                  </div>
                </div>
                {!patron && (
                  <div style={{ marginTop: '1rem' }}>
                    <button
                      className="primary-button"
                      type="button"
                      onClick={() => { setView('login'); setError(''); }}
                      style={{ background: 'linear-gradient(120deg,#df7a34,#d9593e)' }}
                    >
                      Entrar na minha conta
                    </button>
                  </div>
                )}
              </article>
            </section>
          </>
        )}
      </main>
    </div>
  );
}
