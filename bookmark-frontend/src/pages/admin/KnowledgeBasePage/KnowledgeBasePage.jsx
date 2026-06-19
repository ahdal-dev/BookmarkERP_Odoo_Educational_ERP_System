import { useState } from 'react';
import AppShell from '../../../components/AppShell/AppShell';
import TopBar from '../../../components/TopBar/TopBar';
import PageHeader from '../../../components/PageHeader/PageHeader';
import DataTable from '../../../components/DataTable/DataTable';
import StatusPill from '../../../components/StatusPill/StatusPill';
import Pagination from '../../../components/Pagination/Pagination';
import { adminDashboardNav } from '../../../config/navConfigs';
import { mockKBStats, mockKBCollections, mockKBDocuments, openTicketCount } from '../../../mocks/adminMocks';
import styles from './KnowledgeBasePage.module.css';

// Knowledge base — manage RAG document collections and indexing

const navWithActive = adminDashboardNav.map((n) =>
  n.path === '/admin/knowledge-base' ? { ...n, active: true } : n
);

const DOC_STATUS_VARIANT = { Indexed: 'green', Pending: 'yellow', Failed: 'coral' };

export default function KnowledgeBasePage() {
  const [page, setPage] = useState(1);
  const [activeCollection, setActiveCollection] = useState(1);
  const [showUpload, setShowUpload] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [docs, setDocs] = useState(mockKBDocuments);
  const [editingDoc, setEditingDoc] = useState(null);
  const [reindexingAll, setReindexingAll] = useState(false);
  const fileInputRef = useState(null);

  const deleteDoc = (id) => setDocs((prev) => prev.filter((d) => d.id !== id));

  const reindexDoc = (id) => {
    setDocs((prev) => prev.map((d) => d.id === id ? { ...d, status: 'Pending' } : d));
    setTimeout(() => setDocs((prev) => prev.map((d) => d.id === id ? { ...d, status: 'Indexed', chunks: d.chunks || 42, indexedAt: 'Just now' } : d)), 1500);
  };

  const reindexAll = () => {
    setReindexingAll(true);
    setDocs((prev) => prev.map((d) => ({ ...d, status: 'Pending' })));
    setTimeout(() => {
      setDocs((prev) => prev.map((d) => ({ ...d, status: 'Indexed', chunks: d.chunks || 42, indexedAt: 'Just now' })));
      setReindexingAll(false);
    }, 2000);
  };

  const columns = [
    { key: 'name', header: 'Document Name', sortable: true },
    { key: 'collection', header: 'Collection', sortable: true },
    {
      key: 'status', header: 'Status',
      render: (val) => <StatusPill status={val} variant={DOC_STATUS_VARIANT[val] || 'black'} />,
    },
    { key: 'chunks', header: 'Chunks', sortable: true,
      render: (val) => <span style={{ color: 'var(--color-text-muted)', fontSize: '0.82rem' }}>{val || '—'}</span>,
    },
    { key: 'size', header: 'Size' },
    { key: 'indexedAt', header: 'Indexed' },
    {
      key: 'actions', header: 'Actions',
      render: (_, row) => (
        <div className={styles.actionIcons}>
          <button className={styles.iconBtn} title="Edit" onClick={() => setEditingDoc(row)}><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.12 2.12 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg></button>
          <button className={styles.iconBtn} title="Re-index" onClick={() => reindexDoc(row.id)}><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M23 4v6h-6"/><path d="M20.49 15a9 9 0 11-2.12-9.36L23 10"/></svg></button>
          <button className={styles.iconBtn} title="Delete" onClick={() => deleteDoc(row.id)} style={{ color: 'var(--color-coral)' }}><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M3 6h18m-2 0v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg></button>
        </div>
      ),
    },
  ];

  return (
    <AppShell
      navItems={navWithActive}
      logoVariant="icon-text"
      sidebarLabel="ADMIN PANEL"
      topBar={<TopBar searchPlaceholder="Search documents, collections..." notificationCount={openTicketCount} />}
    >
      <div className={styles.breadcrumb}>INTELLIGENCE / KNOWLEDGE BASE</div>

      <PageHeader
        title="RAG Knowledge Base"
        subtitle="Manage the documents and collections powering the Bookmark AI Chatbot."
        actions={
          <div className={styles.headerBtns}>
            <button className={styles.secondaryBtn} onClick={reindexAll} disabled={reindexingAll}>{reindexingAll ? 'Re-indexing...' : 'Re-index All'}</button>
            <button className={styles.primaryBtn} onClick={() => setShowUpload(true)}>+ Upload Document</button>
          </div>
        }
      />

      {/* Stats Strip */}
      <div className={styles.statsStrip}>
        {[
          { label: 'TOTAL DOCS', value: mockKBStats.totalDocs.toLocaleString(), sub: '+12 this week' },
          { label: 'INDEXED', value: `${mockKBStats.indexed.toLocaleString()} (${mockKBStats.indexedPct}%)`, sub: `${mockKBStats.pending} pending` },
          { label: 'AVG TOP-K', value: mockKBStats.avgTopK, sub: `Relevance: ${mockKBStats.retrievalRelevance}%` },
          { label: 'KB COVERAGE', value: `${mockKBStats.coverage}%`, sub: 'of FAQ topics answered' },
        ].map((s) => (
          <div key={s.label} className={styles.statItem}>
            <span className={styles.statLabel}>{s.label}</span>
            <span className={styles.statValue}>{s.value}</span>
            <span className={styles.statSub}>{s.sub}</span>
          </div>
        ))}
      </div>

      <div className={styles.layout}>
        {/* Collections Sidebar */}
        <div className={styles.collections}>
          <span className={styles.collectionTitle}>Collections</span>
          {mockKBCollections.map((col) => (
            <button
              key={col.id}
              className={`${styles.collectionItem} ${activeCollection === col.id ? styles.collectionActive : ''}`}
              onClick={() => setActiveCollection(col.id)}
            >
              <span className={styles.collectionName}>{col.name}</span>
              <span className={styles.collectionCount}>{col.count.toLocaleString()}</span>
            </button>
          ))}
        </div>

        {/* Documents Table */}
        <div className={styles.tableArea}>
          <div className={styles.tableToolbar}>
            <input className={styles.searchBox} placeholder="Filter documents..." />
            <select className={styles.filterSelect}>
              <option>All Statuses</option>
              <option>Indexed</option>
              <option>Pending</option>
              <option>Failed</option>
            </select>
            <button className={styles.bulkBtn} onClick={() => { if (window.confirm(`Delete ${docs.length} documents from this collection?`)) setDocs([]); }}>Bulk Delete</button>
          </div>

          <div className={styles.tableCard}>
            <DataTable columns={columns} data={docs} selectable />
          </div>

          <div className={styles.tableFooter}>
            <span className={styles.showing}>Showing 1–{mockKBDocuments.length} of {mockKBStats.totalDocs.toLocaleString()} documents</span>
            <Pagination currentPage={page} totalPages={60} onPageChange={setPage} />
          </div>
        </div>
      </div>

      {/* Upload Modal */}
      {showUpload && (
        <div className={styles.modalOverlay} onClick={() => setShowUpload(false)}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>Upload Document to Knowledge Base</h2>
              <button className={styles.modalClose} onClick={() => setShowUpload(false)}>✕</button>
            </div>
            <div className={styles.modalBody}>
              {/* Drop Zone */}
              <div
                className={`${styles.dropZone} ${dragOver ? styles.dropZoneActive : ''}`}
                onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                onDragLeave={() => setDragOver(false)}
                onDrop={(e) => { e.preventDefault(); setDragOver(false); }}
              >
                <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="var(--color-lime)" strokeWidth="1.5" strokeLinecap="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
                <p className={styles.dropText}>Drag and drop files here</p>
                <p className={styles.dropSub}>PDF, DOCX, TXT — Max 20MB</p>
                <input
                  type="file"
                  accept=".pdf,.docx,.txt"
                  style={{ display: 'none' }}
                  id="kb-file-input"
                  onChange={(e) => {
                    if (e.target.files[0]) {
                      const f = e.target.files[0];
                      setDocs((prev) => [...prev, { id: Date.now(), name: f.name, collection: 'General', status: 'Pending', chunks: null, size: `${(f.size / 1024).toFixed(0)} KB`, indexedAt: '—' }]);
                      setShowUpload(false);
                    }
                  }}
                />
                <button className={styles.browseBtn} onClick={() => document.getElementById('kb-file-input').click()}>Browse Files</button>
              </div>

              {/* Metadata */}
              <div className={styles.formField}>
                <label className={styles.formLabel}>Collection</label>
                <select className={styles.formInput}>
                  {mockKBCollections.slice(1).map((c) => (
                    <option key={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>
              <div className={styles.formField}>
                <label className={styles.formLabel}>Tags</label>
                <input className={styles.formInput} placeholder="e.g. admission, 2025, policy" />
              </div>
              <div className={styles.formField}>
                <label className={styles.formLabel}>Chunk Size</label>
                <select className={styles.formInput}>
                  <option>512 tokens (recommended)</option>
                  <option>256 tokens</option>
                  <option>1024 tokens</option>
                </select>
              </div>
            </div>
            <div className={styles.modalFooter}>
              <button className={styles.cancelBtn} onClick={() => setShowUpload(false)}>Cancel</button>
              <button className={styles.saveBtn} onClick={() => setShowUpload(false)}>Upload & Index</button>
            </div>
          </div>
        </div>
      )}

      {editingDoc && (
        <div className={styles.modalOverlay} onClick={() => setEditingDoc(null)}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>Edit Document</h2>
              <button className={styles.modalClose} onClick={() => setEditingDoc(null)}>✕</button>
            </div>
            <div className={styles.modalBody}>
              <div className={styles.formField}>
                <label className={styles.formLabel}>Document Name</label>
                <input className={styles.formInput} defaultValue={editingDoc.name} />
              </div>
              <div className={styles.formField}>
                <label className={styles.formLabel}>Collection</label>
                <select className={styles.formInput} defaultValue={editingDoc.collection}>
                  {mockKBCollections.slice(1).map((c) => (
                    <option key={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>
              <div className={styles.formField}>
                <label className={styles.formLabel}>Tags</label>
                <input className={styles.formInput} placeholder="e.g. admission, 2025, policy" />
              </div>
            </div>
            <div className={styles.modalFooter}>
              <button className={styles.cancelBtn} onClick={() => setEditingDoc(null)}>Cancel</button>
              <button className={styles.saveBtn} onClick={() => setEditingDoc(null)}>Save Changes</button>
            </div>
          </div>
        </div>
      )}
    </AppShell>
  );
}
