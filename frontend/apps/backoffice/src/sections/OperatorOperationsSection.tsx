import { startTransition, useDeferredValue, useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { ApiError } from '@biblioteca-ifms/shared';
import type { ApiClient, LibraryBranch, User, UserInput } from '@biblioteca-ifms/shared';

type OperatorFormState = {
  email: string;
  first_name: string;
  last_name: string;
  role: User['role'];
  library_branch: string;
  is_active: boolean;
  password: string;
};

const roleLabels: Record<User['role'], string> = {
  admin: 'Administrador',
  manager: 'Gerente',
  librarian: 'Bibliotecario',
  assistant: 'Auxiliar',
  integration: 'Integracao',
};

function createEmptyForm(): OperatorFormState {
  return {
    email: '',
    first_name: '',
    last_name: '',
    role: 'assistant',
    library_branch: '',
    is_active: true,
    password: '',
  };
}

function mapUserToForm(user: User): OperatorFormState {
  return {
    email: user.email,
    first_name: user.first_name || '',
    last_name: user.last_name || '',
    role: user.role,
    library_branch: user.library_branch || '',
    is_active: user.is_active,
    password: '',
  };
}

function toneClass(value: boolean) {
  return value ? 'tone tone--positive' : 'tone tone--neutral';
}

interface OperatorOperationsSectionProps {
  api: ApiClient;
  branches: LibraryBranch[];
  currentUser: User | null;
  onMessage: (value: string) => void;
  onError: (value: string) => void;
}

export function OperatorOperationsSection(props: OperatorOperationsSectionProps) {
  const [operators, setOperators] = useState<User[]>([]);
  const [editingId, setEditingId] = useState('');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [deletingId, setDeletingId] = useState('');
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [form, setForm] = useState<OperatorFormState>(() => createEmptyForm());
  const deferredSearch = useDeferredValue(search);

  async function loadOperators() {
    setLoading(true);
    try {
      const data = await props.api.listOperators();
      setOperators(data);
      setPermissionDenied(false);
    } catch (caughtError) {
      if (caughtError instanceof ApiError && caughtError.status === 403) {
        setPermissionDenied(true);
      } else {
        props.onError(caughtError instanceof ApiError ? caughtError.message : 'Falha ao carregar operadores.');
      }
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadOperators();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const filtered = operators.filter((user) => {
    const query = deferredSearch.trim().toLowerCase();
    if (!query) return true;
    return [user.email, user.first_name, user.last_name, user.role].join(' ').toLowerCase().includes(query);
  });

  async function handleSave(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    props.onError('');
    props.onMessage('');

    const payload: UserInput = {
      email: form.email.trim(),
      first_name: form.first_name.trim(),
      last_name: form.last_name.trim(),
      role: form.role,
      library_branch: form.library_branch || null,
      is_active: form.is_active,
    };
    if (form.password.trim()) {
      payload.password = form.password;
    }

    try {
      if (editingId) {
        await props.api.updateOperator(editingId, payload);
        props.onMessage('Operador atualizado com sucesso.');
      } else {
        if (!payload.password) {
          props.onError('Senha e obrigatoria ao cadastrar um novo operador.');
          setSaving(false);
          return;
        }
        await props.api.createOperator(payload);
        props.onMessage('Operador cadastrado com sucesso.');
      }
      await loadOperators();
      startTransition(() => {
        setEditingId('');
        setForm(createEmptyForm());
      });
    } catch (caughtError) {
      props.onError(caughtError instanceof ApiError ? caughtError.message : 'Falha ao salvar operador.');
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(user: User) {
    if (props.currentUser && user.id === props.currentUser.id) {
      props.onError('Nao e possivel remover o proprio usuario conectado.');
      return;
    }
    const confirmed = window.confirm(`Remover o operador ${user.email}? Essa acao nao pode ser desfeita.`);
    if (!confirmed) return;

    setDeletingId(user.id);
    props.onError('');
    props.onMessage('');

    try {
      await props.api.deleteOperator(user.id);
      props.onMessage('Operador removido.');
      await loadOperators();
    } catch (caughtError) {
      props.onError(caughtError instanceof ApiError ? caughtError.message : 'Falha ao remover operador.');
    } finally {
      setDeletingId('');
    }
  }

  if (permissionDenied) {
    return (
      <div className="content-grid">
        <section className="panel-card">
          <div className="panel-card__header">
            <span className="eyebrow">acesso restrito</span>
            <h2>Gestao de operadores</h2>
            <p>Apenas perfis <strong>Administrador</strong> ou <strong>Gerente</strong> podem cadastrar, editar e remover operadores do sistema.</p>
          </div>
          <div className="banner banner--error">
            Seu usuario atual ({props.currentUser?.role || 'sem perfil'}) nao tem permissao para acessar esta area. Solicite elevacao a um administrador.
          </div>
        </section>
      </div>
    );
  }

  return (
    <div className="content-grid">
      <section className="panel-card">
        <div className="panel-card__header">
          <span className="eyebrow">cadastro de operadores</span>
          <h2>{editingId ? 'Editar operador' : 'Novo operador'}</h2>
          <p>Controla acesso ao backoffice: perfil, biblioteca de vinculo e status. A senha so e obrigatoria no cadastro inicial.</p>
        </div>
        <form className="stack-form" onSubmit={handleSave}>
          <label>
            <span>E-mail institucional</span>
            <input type="email" value={form.email} onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))} required placeholder="nome@ifms.edu.br" />
          </label>
          <label>
            <span>Nome</span>
            <input value={form.first_name} onChange={(event) => setForm((current) => ({ ...current, first_name: event.target.value }))} />
          </label>
          <label>
            <span>Sobrenome</span>
            <input value={form.last_name} onChange={(event) => setForm((current) => ({ ...current, last_name: event.target.value }))} />
          </label>
          <label>
            <span>Perfil de acesso</span>
            <select value={form.role} onChange={(event) => setForm((current) => ({ ...current, role: event.target.value as User['role'] }))}>
              {(Object.keys(roleLabels) as User['role'][]).map((role) => (
                <option key={role} value={role}>{roleLabels[role]}</option>
              ))}
            </select>
          </label>
          <label>
            <span>Biblioteca de vinculo</span>
            <select value={form.library_branch} onChange={(event) => setForm((current) => ({ ...current, library_branch: event.target.value }))}>
              <option value="">Sem biblioteca definida</option>
              {props.branches.map((branch) => (
                <option key={branch.id} value={branch.id}>{branch.institution_name} - {branch.campus_name} - {branch.name}</option>
              ))}
            </select>
          </label>
          <label>
            <span>{editingId ? 'Nova senha (deixe em branco para manter)' : 'Senha inicial'}</span>
            <input type="password" value={form.password} onChange={(event) => setForm((current) => ({ ...current, password: event.target.value }))} placeholder={editingId ? 'Em branco = manter atual' : 'Minimo 8 caracteres recomendado'} minLength={editingId ? 0 : 6} />
          </label>
          <label className="inline-check">
            <input type="checkbox" checked={form.is_active} onChange={(event) => setForm((current) => ({ ...current, is_active: event.target.checked }))} />
            <span>Usuario ativo</span>
          </label>
          <div className="button-row">
            <button className="primary-button" type="submit" disabled={saving}>
              {saving ? 'Salvando...' : editingId ? 'Atualizar operador' : 'Cadastrar operador'}
            </button>
            {editingId ? (
              <button className="ghost-button" type="button" onClick={() => { setEditingId(''); setForm(createEmptyForm()); }}>
                Cancelar edicao
              </button>
            ) : null}
          </div>
        </form>
      </section>

      <section className="panel-card">
        <div className="panel-card__header">
          <span className="eyebrow">quadro de acesso</span>
          <h2>Operadores cadastrados</h2>
          <p>Equipe com acesso ao backoffice. Ativar/desativar nao apaga o historico de operacoes.</p>
        </div>
        <label className="inline-field">
          <span>Buscar operador</span>
          <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="nome, e-mail ou perfil" />
        </label>
        <div className="table-wrapper section-gap">
          <table>
            <thead>
              <tr>
                <th>Operador</th>
                <th>E-mail</th>
                <th>Perfil</th>
                <th>Status</th>
                <th>Acao</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={5}>Carregando operadores...</td>
                </tr>
              ) : null}
              {!loading && filtered.slice(0, 20).map((user) => {
                const displayName = `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.email;
                const isSelf = props.currentUser?.id === user.id;
                return (
                  <tr key={user.id}>
                    <td>{displayName}{isSelf ? ' (voce)' : ''}</td>
                    <td>{user.email}</td>
                    <td>{roleLabels[user.role] || user.role}</td>
                    <td><span className={toneClass(user.is_active)}>{user.is_active ? 'ativo' : 'inativo'}</span></td>
                    <td>
                      <div className="button-row">
                        <button className="ghost-button ghost-button--small" type="button" onClick={() => { setEditingId(user.id); setForm(mapUserToForm(user)); }}>
                          Editar
                        </button>
                        <button
                          className="ghost-button ghost-button--small"
                          type="button"
                          style={{ color: isSelf ? '#8a8a8a' : '#8a3028' }}
                          disabled={deletingId === user.id || isSelf}
                          onClick={() => void handleDelete(user)}
                        >
                          {deletingId === user.id ? 'Removendo...' : 'Remover'}
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
              {!loading && filtered.length === 0 ? (
                <tr>
                  <td colSpan={5}>Nenhum operador encontrado para o filtro atual.</td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
