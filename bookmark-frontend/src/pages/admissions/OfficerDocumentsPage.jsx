import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AppShell from '../../components/AppShell/AppShell';
import TopBar from '../../components/TopBar/TopBar';
import PageHeader from '../../components/PageHeader/PageHeader';
import { admissionsOfficerNav } from '../../config/navConfigs';
import { admissionsAPI } from '../../api/apiGateway';
import useAsync from '../../hooks/useAsync';
import styles from './OfficerDocumentsPage.module.css';

const STATE_LABELS = {
  draft: { label: 'Draft', color: '#b5b3ab' },
  submitted: { label: 'Submitted', color: '#2563eb' },
  under_review: { label: 'Under Review', color: '#d97706' },
  accepted: { label: 'Accepted', color: '#16a34a' },
  rejected: { label: 'Rejected', color: '#dc2626' },
};

const FILTERS = ['All', 'Has Document', 'Missing Document'];

export default function OfficerDocumentsPage() {
  const navigate = useNavigate();
  const [filter, setFilter] = useState('All');
  const [search, setSearch] = useState('');

  const { data, loading, error } = useAsync(() => admissionsAPI.getDocuments(), []);
  const docs = data?.documents ?? [];

  const visible = docs.filter((d) => {
    const matchFilter =
      filter === 'All' ||
      (filter === 'Has Document' && d.has_document) ||
      (filter === 'Missing Document' && !d.has_document);
    const q = search.toLowerCase();
    const matchSearch =
      !q ||
      d.name?.toLowerCase().includes(q) ||
      d.email?.toLowerCase().includes(q) ||
      d.reference?.toLowerCase().includes(q);
    return matchFilter && matchSearch;
  });

  const navWithActive = admissionsOfficerNav.map((n) => ({
    ...n,
    active: n.path === '/admissions/officer/documents',
  }));

  return (
    <AppShell
      navItems={navWithActive}
      logoVariant="icon-text"
      sidebarLabel="ADMISSIONS"
      topBar={<TopBar searchPlaceholder="Search applications..." />}
    >
      <PageHeader
        title="Document Submissions"
        subtitle="Review uploaded transcripts and application documents"
      />

      <div className={styles.toolbar}>
        <input
          className={styles.search}
          placeholder="Search by name, email or reference…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <div className={styles.filters}>
          {FILTERS.map((f) => (
            <button
              key={f}
              className={`${styles.filterBtn} ${filter === f ? styles.active : ''}`}
              onClick={() => setFilter(f)}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {loading && <div className={styles.state}>Loading documents…</div>}
      {error && <div className={styles.stateError}>Failed to load documents. Is the backend running?</div>}

      {!loading && !error && (
        <div className={styles.tableWrap}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Applicant</th>
                <th>Reference</th>
                <th>Program</th>
                <th>Document</th>
                <th>Status</th>
                <th>Date</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {visible.length === 0 && (
                <tr>
                  <td colSpan={7} className={styles.emptyRow}>No applications found.</td>
                </tr>
              )}
              {visible.map((doc) => {
                const stateInfo = STATE_LABELS[doc.state] ?? { label: doc.state, color: '#b5b3ab' };
                return (
                  <tr key={doc.id} className={styles.row}>
                    <td>
                      <div className={styles.applicantName}>{doc.name}</div>
                      <div className={styles.applicantEmail}>{doc.email}</div>
                    </td>
                    <td className={styles.ref}>{doc.reference}</td>
                    <td>{doc.program}</td>
                    <td>
                      {doc.has_document ? (
                        <span className={styles.docChip}>
                          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                          {doc.transcript_filename}
                        </span>
                      ) : (
                        <span className={styles.missingChip}>Missing</span>
                      )}
                    </td>
                    <td>
                      <span className={styles.stateBadge} style={{ color: stateInfo.color, borderColor: stateInfo.color }}>
                        {stateInfo.label}
                      </span>
                    </td>
                    <td className={styles.date}>
                      {doc.application_date
                        ? new Date(doc.application_date).toLocaleDateString()
                        : '—'}
                    </td>
                    <td>
                      <button
                        className={styles.reviewBtn}
                        onClick={() => navigate(`/admissions/officer/application/${doc.id}`)}
                      >
                        Review →
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </AppShell>
  );
}
