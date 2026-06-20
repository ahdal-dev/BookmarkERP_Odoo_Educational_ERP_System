import { useState } from 'react';
import AppShell from '../../../components/AppShell/AppShell';
import TopBar from '../../../components/TopBar/TopBar';
import PageHeader from '../../../components/PageHeader/PageHeader';
import useAsync from '../../../hooks/useAsync';
import { adminAPI } from '../../../api/apiGateway';
import { adminDashboardNav } from '../../../config/navConfigs';
import styles from './securityPages.module.css';

const RECORD_TYPES = [
  ['student_record', 'Student Records'],
  ['admission', 'Admissions'],
  ['petition', 'Petitions'],
  ['support_ticket', 'Support Tickets'],
  ['audit_log', 'Audit Logs'],
];
const ACTIONS = [['archive', 'Archive'], ['anonymize', 'Anonymize'], ['delete', 'Delete']];

const nav = adminDashboardNav.map((n) =>
  n.path === '/admin/data-retention' ? { ...n, active: true } : n);

export default function DataRetentionPage() {
  const { data, loading, error, reload } = useAsync(adminAPI.getDataRetention);
  const [modalOpen, setModalOpen] = useState(false);
  const [running, setRunning] = useState(false);
  const policies = data?.policies ?? [];

  const toggleActive = async (p) => {
    await adminAPI.updateDataRetention(p.id, { active: !p.active });
    reload();
  };
  const remove = async (p) => {
    if (!window.confirm(`Delete policy "${p.name}"?`)) return;
    await adminAPI.deleteDataRetention(p.id);
    reload();
  };
  const runNow = async () => {
    setRunning(true);
    try {
      const res = await adminAPI.runDataRetention();
      window.alert(`Retention run complete — ${res.purged} record(s) processed.`);
      reload();
    } catch (e) {
      window.alert(e.response?.data?.detail || 'Run failed');
    } finally {
      setRunning(false);
    }
  };

  return (
    <AppShell navItems={nav} logoVariant="icon-text" sidebarLabel="ADMIN PANEL" topBar={<TopBar />}>
      <div className={styles.breadcrumb}>ADMIN / DATA RETENTION</div>
      <PageHeader
        title="Data Retention Policies"
        subtitle="Automatically archive, anonymize, or delete obsolete records."
        actions={
          <div className={styles.toolbar}>
            <button className={styles.secondaryBtn} onClick={runNow} disabled={running}>
              {running ? 'Running…' : 'Run now'}
            </button>
            <button className={styles.createBtn} onClick={() => setModalOpen(true)}>+ New Policy</button>
          </div>
        }
      />

      <div className={styles.tableCard}>
        {loading ? <div className={styles.state}>Loading…</div>
          : error ? <div className={styles.state}>{error} <button className={styles.iconBtn} onClick={reload}>Retry</button></div>
          : policies.length === 0 ? <div className={styles.state}>No policies defined yet.</div>
          : (
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Policy</th><th>Record Type</th><th>Retention</th><th>Action</th>
                  <th>Status</th><th>Last Run</th><th>Purged</th><th></th>
                </tr>
              </thead>
              <tbody>
                {policies.map((p) => (
                  <tr key={p.id}>
                    <td>{p.name}</td>
                    <td>{(RECORD_TYPES.find((r) => r[0] === p.record_type) || [, p.record_type])[1]}</td>
                    <td>{p.retention_days} days</td>
                    <td><span className={`${styles.pill} ${styles.pillGray}`}>{p.action}</span></td>
                    <td>
                      <span className={`${styles.pill} ${p.active ? styles.pillGreen : styles.pillGray}`}>
                        {p.active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className={styles.mono}>{p.last_run || '—'}</td>
                    <td>{p.last_purged_count ?? 0}</td>
                    <td style={{ whiteSpace: 'nowrap' }}>
                      <button className={styles.iconBtn} onClick={() => toggleActive(p)}>
                        {p.active ? 'Disable' : 'Enable'}
                      </button>{' '}
                      <button className={`${styles.iconBtn} ${styles.iconBtnDanger}`} onClick={() => remove(p)}>Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
      </div>

      {modalOpen && (
        <PolicyModal onClose={() => setModalOpen(false)} onSaved={() => { setModalOpen(false); reload(); }} />
      )}
    </AppShell>
  );
}

function PolicyModal({ onClose, onSaved }) {
  const [form, setForm] = useState({
    name: '', record_type: 'student_record', retention_days: 365, action: 'archive', active: true,
  });
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const save = async () => {
    if (!form.name.trim()) { setError('Name is required'); return; }
    setBusy(true); setError('');
    try {
      await adminAPI.createDataRetention({ ...form, retention_days: Number(form.retention_days) });
      onSaved();
    } catch (e) {
      setError(e.response?.data?.detail || 'Failed to create policy');
      setBusy(false);
    }
  };

  return (
    <div className={styles.overlay} role="dialog" aria-modal="true">
      <div className={styles.modal}>
        <h2 className={styles.modalTitle}>New Retention Policy</h2>
        {error && <div className={styles.errorText}>{error}</div>}
        <div className={styles.field}>
          <span className={styles.fieldLabel}>Policy name</span>
          <input className={styles.input} value={form.name}
                 onChange={(e) => setForm({ ...form, name: e.target.value })} />
        </div>
        <div className={styles.field}>
          <span className={styles.fieldLabel}>Record type</span>
          <select className={styles.select} value={form.record_type}
                  onChange={(e) => setForm({ ...form, record_type: e.target.value })}>
            {RECORD_TYPES.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
          </select>
        </div>
        <div className={styles.field}>
          <span className={styles.fieldLabel}>Retention (days)</span>
          <input className={styles.input} type="number" min="1" value={form.retention_days}
                 onChange={(e) => setForm({ ...form, retention_days: e.target.value })} />
        </div>
        <div className={styles.field}>
          <span className={styles.fieldLabel}>Action</span>
          <select className={styles.select} value={form.action}
                  onChange={(e) => setForm({ ...form, action: e.target.value })}>
            {ACTIONS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
          </select>
        </div>
        <label className={styles.field} style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
          <input type="checkbox" checked={form.active}
                 onChange={(e) => setForm({ ...form, active: e.target.checked })} />
          <span className={styles.fieldLabel} style={{ margin: 0 }}>Active</span>
        </label>
        <div className={styles.modalActions}>
          <button className={styles.iconBtn} onClick={onClose}>Cancel</button>
          <button className={styles.createBtn} onClick={save} disabled={busy}>
            {busy ? 'Saving…' : 'Create'}
          </button>
        </div>
      </div>
    </div>
  );
}
