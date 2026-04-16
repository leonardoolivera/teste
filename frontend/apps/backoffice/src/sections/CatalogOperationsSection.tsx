import { startTransition, useEffect, useState } from 'react';
import type { ChangeEvent, FormEvent } from 'react';
import { ApiError } from '@biblioteca-ifms/shared';
import type {
  ApiClient,
  Author,
  BibliographicRecord,
  BibliographicRecordInput,
  ItemCopy,
  ItemCopyInput,
  LibraryBranch,
  Subject,
} from '@biblioteca-ifms/shared';

type RecordFormState = {
  title: string;
  subtitle: string;
  isbn: string;
  publication_year: string;
  publisher: string;
  language: string;
  edition_statement: string;
  classification_code: string;
  cutter: string;
  description: string;
  author_ids: string[];
  subject_ids: string[];
};

type CopyFormState = {
  bibliographic_record: string;
  library_branch: string;
  asset_code: string;
  tomb_number: string;
  barcode: string;
  rfid_tag: string;
  shelf_location: string;
  status: ItemCopy['status'];
  notes: string;
};

const copyStatuses: ItemCopy['status'][] = ['available', 'loaned', 'reserved', 'processing', 'lost', 'discarded'];

function createEmptyRecordForm(): RecordFormState {
  return {
    title: '',
    subtitle: '',
    isbn: '',
    publication_year: '',
    publisher: '',
    language: 'pt-BR',
    edition_statement: '1a edicao',
    classification_code: '',
    cutter: '',
    description: '',
    author_ids: [],
    subject_ids: [],
  };
}

function createEmptyCopyForm(branchId = '', recordId = ''): CopyFormState {
  return {
    bibliographic_record: recordId,
    library_branch: branchId,
    asset_code: '',
    tomb_number: '',
    barcode: '',
    rfid_tag: '',
    shelf_location: '',
    status: 'available',
    notes: '',
  };
}

function mapRecordToForm(record: BibliographicRecord): RecordFormState {
  return {
    title: record.title,
    subtitle: record.subtitle,
    isbn: record.isbn,
    publication_year: record.publication_year ? String(record.publication_year) : '',
    publisher: record.publisher,
    language: record.language || 'pt-BR',
    edition_statement: record.edition_statement,
    classification_code: record.classification_code,
    cutter: record.cutter,
    description: record.description,
    author_ids: record.author_ids,
    subject_ids: record.subject_ids,
  };
}

function mapCopyToForm(copy: ItemCopy): CopyFormState {
  return {
    bibliographic_record: copy.bibliographic_record,
    library_branch: copy.library_branch,
    asset_code: copy.asset_code,
    tomb_number: copy.tomb_number,
    barcode: copy.barcode || '',
    rfid_tag: copy.rfid_tag || '',
    shelf_location: copy.shelf_location,
    status: copy.status,
    notes: copy.notes,
  };
}

function getSelectedValues(event: ChangeEvent<HTMLSelectElement>): string[] {
  return Array.from(event.currentTarget.selectedOptions).map((option) => option.value);
}

interface CatalogOperationsSectionProps {
  api: ApiClient;
  branches: LibraryBranch[];
  authors: Author[];
  subjects: Subject[];
  records: BibliographicRecord[];
  filteredRecords: BibliographicRecord[];
  filteredCopies: ItemCopy[];
  catalogSearch: string;
  onCatalogSearchChange: (value: string) => void;
  onChanged: () => Promise<void>;
  onMessage: (value: string) => void;
  onError: (value: string) => void;
}

export function CatalogOperationsSection(props: CatalogOperationsSectionProps) {
  const [authorName, setAuthorName] = useState('');
  const [subjectName, setSubjectName] = useState('');
  const [editingRecordId, setEditingRecordId] = useState('');
  const [editingCopyId, setEditingCopyId] = useState('');
  const [recordForm, setRecordForm] = useState<RecordFormState>(createEmptyRecordForm);
  const [copyForm, setCopyForm] = useState<CopyFormState>(() => createEmptyCopyForm(props.branches[0]?.id, props.records[0]?.id));
  const [savingKey, setSavingKey] = useState('');

  useEffect(() => {
    if (!copyForm.library_branch && props.branches[0]) {
      setCopyForm((current) => ({ ...current, library_branch: props.branches[0].id }));
    }
  }, [copyForm.library_branch, props.branches]);

  useEffect(() => {
    if (!copyForm.bibliographic_record && props.records[0]) {
      setCopyForm((current) => ({ ...current, bibliographic_record: props.records[0].id }));
    }
  }, [copyForm.bibliographic_record, props.records]);

  async function handleCreateAuthor(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSavingKey('author');
    props.onError('');
    props.onMessage('');

    try {
      await props.api.createAuthor({ name: authorName.trim() });
      await props.onChanged();
      startTransition(() => setAuthorName(''));
      props.onMessage('Autor cadastrado com sucesso.');
    } catch (caughtError) {
      props.onError(caughtError instanceof ApiError ? caughtError.message : 'Falha ao cadastrar autor.');
    } finally {
      setSavingKey('');
    }
  }

  async function handleCreateSubject(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSavingKey('subject');
    props.onError('');
    props.onMessage('');

    try {
      await props.api.createSubject({ name: subjectName.trim() });
      await props.onChanged();
      startTransition(() => setSubjectName(''));
      props.onMessage('Assunto cadastrado com sucesso.');
    } catch (caughtError) {
      props.onError(caughtError instanceof ApiError ? caughtError.message : 'Falha ao cadastrar assunto.');
    } finally {
      setSavingKey('');
    }
  }

  async function handleSaveRecord(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSavingKey('record');
    props.onError('');
    props.onMessage('');

    const payload: BibliographicRecordInput = {
      title: recordForm.title.trim(),
      subtitle: recordForm.subtitle.trim(),
      isbn: recordForm.isbn.trim(),
      publication_year: recordForm.publication_year ? Number(recordForm.publication_year) : null,
      publisher: recordForm.publisher.trim(),
      language: recordForm.language.trim() || 'pt-BR',
      edition_statement: recordForm.edition_statement.trim(),
      classification_code: recordForm.classification_code.trim(),
      cutter: recordForm.cutter.trim(),
      description: recordForm.description.trim(),
      author_ids: recordForm.author_ids,
      subject_ids: recordForm.subject_ids,
    };

    try {
      if (editingRecordId) {
        await props.api.updateRecord(editingRecordId, payload);
      } else {
        await props.api.createRecord(payload);
      }
      await props.onChanged();
      startTransition(() => {
        setEditingRecordId('');
        setRecordForm(createEmptyRecordForm());
      });
      props.onMessage(editingRecordId ? 'Registro bibliografico atualizado.' : 'Registro bibliografico criado.');
    } catch (caughtError) {
      props.onError(caughtError instanceof ApiError ? caughtError.message : 'Falha ao salvar registro bibliografico.');
    } finally {
      setSavingKey('');
    }
  }

  async function handleSaveCopy(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSavingKey('copy');
    props.onError('');
    props.onMessage('');

    const payload: ItemCopyInput = {
      bibliographic_record: copyForm.bibliographic_record,
      library_branch: copyForm.library_branch,
      asset_code: copyForm.asset_code.trim(),
      tomb_number: copyForm.tomb_number.trim(),
      barcode: copyForm.barcode.trim() || null,
      rfid_tag: copyForm.rfid_tag.trim() || null,
      shelf_location: copyForm.shelf_location.trim(),
      status: copyForm.status,
      notes: copyForm.notes.trim(),
    };

    try {
      if (editingCopyId) {
        await props.api.updateCopy(editingCopyId, payload);
      } else {
        await props.api.createCopy(payload);
      }
      await props.onChanged();
      startTransition(() => {
        setEditingCopyId('');
        setCopyForm(createEmptyCopyForm(props.branches[0]?.id, props.records[0]?.id));
      });
      props.onMessage(editingCopyId ? 'Exemplar atualizado.' : 'Exemplar cadastrado.');
    } catch (caughtError) {
      props.onError(caughtError instanceof ApiError ? caughtError.message : 'Falha ao salvar exemplar.');
    } finally {
      setSavingKey('');
    }
  }

  return (
    <div className="content-grid">
      <section className="panel-card">
        <div className="panel-card__header">
          <span className="eyebrow">autoridades</span>
          <h2>Autores e assuntos</h2>
          <p>Cria rapidamente as listas de apoio para a catalogacao formal.</p>
        </div>
        <form className="stack-form" onSubmit={handleCreateAuthor}>
          <label>
            <span>Novo autor</span>
            <input value={authorName} onChange={(event) => setAuthorName(event.target.value)} placeholder="Nome do autor" required />
          </label>
          <button className="secondary-button" type="submit" disabled={savingKey === 'author'}>
            {savingKey === 'author' ? 'Salvando...' : 'Cadastrar autor'}
          </button>
        </form>
        <form className="stack-form section-gap" onSubmit={handleCreateSubject}>
          <label>
            <span>Novo assunto</span>
            <input value={subjectName} onChange={(event) => setSubjectName(event.target.value)} placeholder="Assunto ou descritor" required />
          </label>
          <button className="secondary-button" type="submit" disabled={savingKey === 'subject'}>
            {savingKey === 'subject' ? 'Salvando...' : 'Cadastrar assunto'}
          </button>
        </form>
        <p className="muted-text">Autores cadastrados: {props.authors.length}. Assuntos cadastrados: {props.subjects.length}.</p>
      </section>

      <section className="panel-card">
        <div className="panel-card__header">
          <span className="eyebrow">registro</span>
          <h2>{editingRecordId ? 'Editar registro bibliografico' : 'Novo registro bibliografico'}</h2>
          <p>Centraliza titulo, classificacao, autores e assuntos do acervo.</p>
        </div>
        <form className="stack-form" onSubmit={handleSaveRecord}>
          <label>
            <span>Titulo</span>
            <input value={recordForm.title} onChange={(event) => setRecordForm((current) => ({ ...current, title: event.target.value }))} required />
          </label>
          <label>
            <span>Subtitulo</span>
            <input value={recordForm.subtitle} onChange={(event) => setRecordForm((current) => ({ ...current, subtitle: event.target.value }))} />
          </label>
          <label>
            <span>ISBN</span>
            <input value={recordForm.isbn} onChange={(event) => setRecordForm((current) => ({ ...current, isbn: event.target.value }))} />
          </label>
          <label>
            <span>Ano de publicacao</span>
            <input type="number" value={recordForm.publication_year} onChange={(event) => setRecordForm((current) => ({ ...current, publication_year: event.target.value }))} />
          </label>
          <label>
            <span>Editora</span>
            <input value={recordForm.publisher} onChange={(event) => setRecordForm((current) => ({ ...current, publisher: event.target.value }))} />
          </label>
          <label>
            <span>Codigo de classificacao</span>
            <input value={recordForm.classification_code} onChange={(event) => setRecordForm((current) => ({ ...current, classification_code: event.target.value }))} />
          </label>
          <label>
            <span>Cutter</span>
            <input value={recordForm.cutter} onChange={(event) => setRecordForm((current) => ({ ...current, cutter: event.target.value }))} />
          </label>
          <label>
            <span>Idioma</span>
            <input value={recordForm.language} onChange={(event) => setRecordForm((current) => ({ ...current, language: event.target.value }))} />
          </label>
          <label>
            <span>Edicao</span>
            <input value={recordForm.edition_statement} onChange={(event) => setRecordForm((current) => ({ ...current, edition_statement: event.target.value }))} />
          </label>
          <label>
            <span>Autores</span>
            <select multiple size={Math.max(3, Math.min(6, props.authors.length || 3))} value={recordForm.author_ids} onChange={(event) => setRecordForm((current) => ({ ...current, author_ids: getSelectedValues(event) }))}>
              {props.authors.map((author) => (
                <option key={author.id} value={author.id}>{author.name}</option>
              ))}
            </select>
          </label>
          <label>
            <span>Assuntos</span>
            <select multiple size={Math.max(3, Math.min(6, props.subjects.length || 3))} value={recordForm.subject_ids} onChange={(event) => setRecordForm((current) => ({ ...current, subject_ids: getSelectedValues(event) }))}>
              {props.subjects.map((subject) => (
                <option key={subject.id} value={subject.id}>{subject.name}</option>
              ))}
            </select>
          </label>
          <label>
            <span>Descricao</span>
            <textarea value={recordForm.description} onChange={(event) => setRecordForm((current) => ({ ...current, description: event.target.value }))} rows={3} />
          </label>
          <div className="button-row">
            <button className="primary-button" type="submit" disabled={savingKey === 'record'}>
              {savingKey === 'record' ? 'Salvando...' : editingRecordId ? 'Atualizar registro' : 'Criar registro'}
            </button>
            {editingRecordId ? (
              <button className="ghost-button" type="button" onClick={() => { setEditingRecordId(''); setRecordForm(createEmptyRecordForm()); }}>
                Cancelar edicao
              </button>
            ) : null}
          </div>
        </form>
        <label className="inline-field section-gap">
          <span>Buscar no catalogo</span>
          <input value={props.catalogSearch} onChange={(event) => props.onCatalogSearchChange(event.target.value)} placeholder="titulo, ISBN, tombo, RFID..." />
        </label>
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Titulo</th>
                <th>ISBN</th>
                <th>Ano</th>
                <th>Editora</th>
                <th>Acao</th>
              </tr>
            </thead>
            <tbody>
              {props.filteredRecords.slice(0, 10).map((record) => (
                <tr key={record.id}>
                  <td>{record.title}</td>
                  <td>{record.isbn || 'Sem ISBN'}</td>
                  <td>{record.publication_year || '-'}</td>
                  <td>{record.publisher || 'Sem editora'}</td>
                  <td>
                    <button className="ghost-button ghost-button--small" type="button" onClick={() => { setEditingRecordId(record.id); setRecordForm(mapRecordToForm(record)); }}>
                      Editar
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="panel-card">
        <div className="panel-card__header">
          <span className="eyebrow">exemplar</span>
          <h2>{editingCopyId ? 'Editar exemplar fisico' : 'Novo exemplar fisico'}</h2>
          <p>Controla patrimonio, barras, RFID, localizacao e status do item.</p>
        </div>
        <form className="stack-form" onSubmit={handleSaveCopy}>
          <label>
            <span>Registro bibliografico</span>
            <select value={copyForm.bibliographic_record} onChange={(event) => setCopyForm((current) => ({ ...current, bibliographic_record: event.target.value }))} required>
              <option value="">Selecione um registro</option>
              {props.records.map((record) => (
                <option key={record.id} value={record.id}>{record.title}</option>
              ))}
            </select>
          </label>
          <label>
            <span>Biblioteca</span>
            <select value={copyForm.library_branch} onChange={(event) => setCopyForm((current) => ({ ...current, library_branch: event.target.value }))} required>
              <option value="">Selecione uma biblioteca</option>
              {props.branches.map((branch) => (
                <option key={branch.id} value={branch.id}>{branch.institution_name} - {branch.campus_name} - {branch.name}</option>
              ))}
            </select>
          </label>
          <label>
            <span>Codigo patrimonial</span>
            <input value={copyForm.asset_code} onChange={(event) => setCopyForm((current) => ({ ...current, asset_code: event.target.value }))} required />
          </label>
          <label>
            <span>Tombo</span>
            <input value={copyForm.tomb_number} onChange={(event) => setCopyForm((current) => ({ ...current, tomb_number: event.target.value }))} />
          </label>
          <label>
            <span>Codigo de barras</span>
            <input value={copyForm.barcode} onChange={(event) => setCopyForm((current) => ({ ...current, barcode: event.target.value }))} />
          </label>
          <label>
            <span>RFID</span>
            <input value={copyForm.rfid_tag} onChange={(event) => setCopyForm((current) => ({ ...current, rfid_tag: event.target.value }))} />
          </label>
          <label>
            <span>Localizacao</span>
            <input value={copyForm.shelf_location} onChange={(event) => setCopyForm((current) => ({ ...current, shelf_location: event.target.value }))} />
          </label>
          <label>
            <span>Status</span>
            <select value={copyForm.status} onChange={(event) => setCopyForm((current) => ({ ...current, status: event.target.value as ItemCopy['status'] }))}>
              {copyStatuses.map((status) => (
                <option key={status} value={status}>{status}</option>
              ))}
            </select>
          </label>
          <label>
            <span>Notas</span>
            <textarea value={copyForm.notes} onChange={(event) => setCopyForm((current) => ({ ...current, notes: event.target.value }))} rows={3} />
          </label>
          <div className="button-row">
            <button className="primary-button" type="submit" disabled={savingKey === 'copy'}>
              {savingKey === 'copy' ? 'Salvando...' : editingCopyId ? 'Atualizar exemplar' : 'Criar exemplar'}
            </button>
            {editingCopyId ? (
              <button className="ghost-button" type="button" onClick={() => { setEditingCopyId(''); setCopyForm(createEmptyCopyForm(props.branches[0]?.id, props.records[0]?.id)); }}>
                Cancelar edicao
              </button>
            ) : null}
          </div>
        </form>
        <div className="table-wrapper section-gap">
          <table>
            <thead>
              <tr>
                <th>Patrimonio</th>
                <th>Titulo</th>
                <th>Barras</th>
                <th>RFID</th>
                <th>Status</th>
                <th>Acao</th>
              </tr>
            </thead>
            <tbody>
              {props.filteredCopies.slice(0, 12).map((copy) => (
                <tr key={copy.id}>
                  <td>{copy.asset_code}</td>
                  <td>{copy.bibliographic_title}</td>
                  <td>{copy.barcode || '-'}</td>
                  <td>{copy.rfid_tag || '-'}</td>
                  <td>{copy.status}</td>
                  <td>
                    <button className="ghost-button ghost-button--small" type="button" onClick={() => { setEditingCopyId(copy.id); setCopyForm(mapCopyToForm(copy)); }}>
                      Editar
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}