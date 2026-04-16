import { startTransition, useDeferredValue, useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { ApiError, formatDateTime } from '@biblioteca-ifms/shared';
import type { ApiClient, LibraryBranch, Patron, PatronInput } from '@biblioteca-ifms/shared';

type PatronFormState = {
  registration_code: string;
  full_name: string;
  email: string;
  category: Patron['category'];
  status: Patron['status'];
  library_branch: string;
  expires_at: string;
};

function createEmptyPatronForm(branchId = ''): PatronFormState {
  return {
    registration_code: '',
    full_name: '',
    email: '',
    category: 'student',
    status: 'active',
    library_branch: branchId,
    expires_at: '',
  };
}

function mapPatronToForm(patron: Patron): PatronFormState {
  return {
    registration_code: patron.registration_code,
    full_name: patron.full_name,
    email: patron.email,
    category: patron.category,
    status: patron.status,
    library_branch: patron.library_branch || '',
    expires_at: patron.expires_at || '',
  };
}

function toneClass(value: string) {
  if (['active'].includes(value)) {
    return 'tone tone--positive';
  }
  if (['blocked'].includes(value)) {
    return 'tone tone--critical';
  }
  return 'tone tone--warning';
}

interface PatronOperationsSectionProps {
  api: ApiClient;
  branches: LibraryBranch[];
  patrons: Patron[];
  onChanged: () => Promise<void>;
  onMessage: (value: string) => void;
  onError: (value: string) => void;
}

export function PatronOperationsSection(props: PatronOperationsSectionProps) {
  const [editingPatronId, setEditingPatronId] = useState('');
  const [search, setSearch] = useState('');
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState<PatronFormState>(() => createEmptyPatronForm(props.branches[0]?.id));
  const deferredSearch = useDeferredValue(search);

  useEffect(() => {
    if (!form.library_branch && props.branches[0]) {
      setForm((current) => ({ ...current, library_branch: props.branches[0].id }));
    }
  }, [form.library_branch, props.branches]);

  const filteredPatrons = props.patrons.filter((patron) => {
    const query = deferredSearch.trim().toLowerCase();
    if (!query) {
      return true;
    }
    return [patron.full_name, patron.registration_code, patron.email].join(' ').toLowerCase().includes(query);
  });

  async function handleSavePatron(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    props.onError('');
    props.onMessage('');

    const payload: PatronInput = {
      registration_code: form.registration_code.trim(),
      full_name: form.full_name.trim(),
      email: form.email.trim(),
      category: form.category,
      status: form.status,
      library_branch: form.library_branch || null,
      expires_at: form.expires_at || null,
    };

    try {
      if (editingPatronId) {
        await props.api.updatePatron(editingPatronId, payload);
      } else {
        await props.api.createPatron(payload);
      }
      await props.onChanged();
      startTransition(() => {
        setEditingPatronId('');
        setForm(createEmptyPatronForm(props.branches[0]?.id));
      });
      props.onMessage(editingPatronId ? 'Leitor atualizado com sucesso.' : 'Leitor cadastrado com sucesso.');
    } catch (caughtError) {
      props.onError(caughtError instanceof ApiError ? caughtError.message : 'Falha ao salvar leitor.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="content-grid">
      <section className="panel-card">
        <div className="panel-card__header">
          <span className="eyebrow">cadastro de leitores</span>
          <h2>{editingPatronId ? 'Editar leitor' : 'Novo leitor'}</h2>
          <p>Controla matricula, categoria, status e expiracao do cadastro do usuario da biblioteca.</p>
        </div>
        <form className="stack-form" onSubmit={handleSavePatron}>
          <label>
            <span>Codigo de matricula</span>
            <input value={form.registration_code} onChange={(event) => setForm((current) => ({ ...current, registration_code: event.target.value }))} required />
          </label>
          <label>
            <span>Nome completo</span>
            <input value={form.full_name} onChange={(event) => setForm((current) => ({ ...current, full_name: event.target.value }))} required />
          </label>
          <label>
            <span>E-mail</span>
            <input type="email" value={form.email} onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))} />
          </label>
          <label>
            <span>Categoria</span>
            <select value={form.category} onChange={(event) => setForm((current) => ({ ...current, category: event.target.value as Patron['category'] }))}>
              <option value="student">student</option>
              <option value="teacher">teacher</option>
              <option value="staff">staff</option>
              <option value="external">external</option>
            </select>
          </label>
          <label>
            <span>Status</span>
            <select value={form.status} onChange={(event) => setForm((current) => ({ ...current, status: event.target.value as Patron['status'] }))}>
              <option value="active">active</option>
              <option value="blocked">blocked</option>
              <option value="inactive">inactive</option>
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
            <span>Expira em</span>
            <input type="date" value={form.expires_at} onChange={(event) => setForm((current) => ({ ...current, expires_at: event.target.value }))} />
          </label>
          <div className="button-row">
            <button className="primary-button" type="submit" disabled={saving}>
              {saving ? 'Salvando...' : editingPatronId ? 'Atualizar leitor' : 'Cadastrar leitor'}
            </button>
            {editingPatronId ? (
              <button className="ghost-button" type="button" onClick={() => { setEditingPatronId(''); setForm(createEmptyPatronForm(props.branches[0]?.id)); }}>
                Cancelar edicao
              </button>
            ) : null}
          </div>
        </form>
      </section>

      <section className="panel-card">
        <div className="panel-card__header">
          <span className="eyebrow">cadastros ativos</span>
          <h2>Leitores registrados</h2>
          <p>Pesquisa rapida para atendimento e manutencao do cadastro.</p>
        </div>
        <label className="inline-field">
          <span>Buscar leitor</span>
          <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="nome, matricula ou e-mail" />
        </label>
        <div className="table-wrapper section-gap">
          <table>
            <thead>
              <tr>
                <th>Leitor</th>
                <th>Matricula</th>
                <th>Categoria</th>
                <th>Status</th>
                <th>Expira em</th>
                <th>Acao</th>
              </tr>
            </thead>
            <tbody>
              {filteredPatrons.slice(0, 12).map((patron) => (
                <tr key={patron.id}>
                  <td>{patron.full_name}</td>
                  <td>{patron.registration_code}</td>
                  <td>{patron.category}</td>
                  <td><span className={toneClass(patron.status)}>{patron.status}</span></td>
                  <td>{patron.expires_at ? formatDateTime(`${patron.expires_at}T12:00:00`) : 'Sem expiracao'}</td>
                  <td>
                    <button className="ghost-button ghost-button--small" type="button" onClick={() => { setEditingPatronId(patron.id); setForm(mapPatronToForm(patron)); }}>
                      Editar
                    </button>
                  </td>
                </tr>
              ))}
              {filteredPatrons.length === 0 ? (
                <tr>
                  <td colSpan={6}>Nenhum leitor encontrado para o filtro atual.</td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}