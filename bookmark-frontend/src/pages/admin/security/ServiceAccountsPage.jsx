import { useState } from 'react';
import AppShell from '../../../components/AppShell/AppShell';
import TopBar from '../../../components/TopBar/TopBar';
import PageHeader from '../../../components/PageHeader/PageHeader';
import useAsync from '../../../hooks/useAsync';
import { adminAPI } from '../../../api/apiGateway';
import { adminDashboardNav } from '../../../config/navConfigs';
import styles from './securityPages.module.css';

const nav = adminDashboardNav.map((n) =>
  n.path === '/admin/service-accounts' ? { ...n, active: true } : n);

export default function ServiceAccountsPage() {
  const { data, loading, error, reload } = useAsync(adminAPI.getServiceAccounts);
  const [modalOpen, setModalOpen] = useState(false);
  const [revealed, setRevealed] = useState(null); // { name, key }
  const accounts = data?.service_accounts ?? [];

  const rotate = async (a) => {
    if (!window.confirm(`Rotate the key for "${a.name}"? The old key stops working.`)) return;
    try {
      const res = await adminAPI.rotateServiceAccount(a.id);
      setRevealed({ name: a.name, key: res.api_key });
      reload();
    } catch (e) {
      window.alert(e.response?.data?.detail || 'Rotation failed');
    }
  };

  return (
    <AppShell navItems={nav} logoVariant="icon-text" sidebarLabel="ADMIN PANEL" topBar={<TopBar />}>
      <div className={styles.breadcrumb}>ADMIN / SERVICE ACCOUNTS</div>
      <PageHeader
        title="Service Accounts"
        subtitle="Machine credentials with automated rotation."
        actions={<button className={styles.createBtn} onClick={() => setModalOpen(true)}>+ New Account</button>}
      />

      {revealed && (
        <div className={styles.revealBox}>
          <div className={styles.revealLabel}>New key for {revealed.name} — copy it now, it won't be shown again</div>
          {revealed.key}
          <div style={{ marginTop: 10 }}>
            <button className={styles.iconBtn} onClick={() => setRevealed(null)}>Dismiss</button>
          </div>
        </div>
      )}

      <div className={styles.tableCard}>
        {loading ? <div className={styles.state}>Loading…</div>
          : error ? <div className={styles.state}>{error} <button className={styles.iconBtn} onClick={reload}>Retry</button></div>
          : accounts.length === 0 ? <div className={styles.state}>No service accounts yet.</div>
          : (
            <table className={styles.table}>
              <thead>
                <tr><th>Name</th><th>Description</th><th>Key</th><th>Last Rotated</th><th>Interval</th><th>Status</th><th></th></tr>
              </thead>
              <tbody>
                {accounts.map((a) => (
                  <tr key={a.id}>
                    <td>{a.name}</td>
                    <td>{a.description || '—'}</td>
                    <td className={styles.mono}>****{a.api_key_hint || '----'}</td>
                    <td className={styles.mono}>{a.last_rotated || '—'}</td>
                    <td>{a.rotation_interval_days}d</td>
                    <td>
                      <span className={`${styles.pill} ${a.status === 'due' ? styles.pillAmber : styles.pillGreen}`}>
                        {a.status === 'due' ? 'Rotation due' : 'OK'}
                      </span>
                    </td>
                    <td><button className={styles.iconBtn} onClick={() => rotate(a)}>Rotate</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
      </div>

      {modalOpen && (
        <CreateModal
          onClose={() => setModalOpen(false)}
          onCreated={(res, name) => { setModalOpen(false); setRevealed({ name, key: res.api_key }); reload(); }}
        />
      )}
    </AppShell>
  );
}

function CreateModal({ onClose, onCreated }) {
  const [form, setForm] = useState({ name: '', description: '', rotation_interval_days: 30 });
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const save = async () => {
    if (!form.name.trim()) { setError('Name is required'); return; }
    setBusy(true); setError('');
    try {
      const res = await adminAPI.createServiceAccount({
        ...form, rotation_interval_days: Number(form.rotation_interval_days),
      });
      onCreated(res, form.name);
    } catch (e) {
      setError(e.response?.data?.detail || 'Failed to create');
      setBusy(false);
    }
  };

  return (
    <div className={styles.overlay} role="dialog" aria-modal="true">
      <div className={styles.modal}>
        <h2 className={styles.modalTitle}>New Service Account</h2>
        {error && <div className={styles.errorText}>{error}</div>}
        <div className={styles.field}>
          <span className={styles.fieldLabel}>Name</span>
          <input className={styles.input} value={form.name}
                 onChange={(e) => setForm({ ...form, name: e.target.value })} />
        </div>
        <div className={styles.field}>
          <span className={styles.fieldLabel}>Description</span>
          <input className={styles.input} value={form.description}
                 onChange={(e) => setForm({ ...form, description: e.target.value })} />
        </div>
        <div className={styles.field}>
          <span className={styles.fieldLabel}>Rotation interval (days)</span>
          <input className={styles.input} type="number" min="1" value={form.rotation_interval_days}
                 onChange={(e) => setForm({ ...form, rotation_interval_days: e.target.value })} />
        </div>
        <div className={styles.modalActions}>
          <button className={styles.iconBtn} onClick={onClose}>Cancel</button>
          <button className={styles.createBtn} onClick={save} disabled={busy}>
            {busy ? 'Creating…' : 'Create'}
          </button>
        </div>
      </div>
    </div>
  );
}
