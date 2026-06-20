import { useState } from 'react';
import AppShell from '../../../components/AppShell/AppShell';
import TopBar from '../../../components/TopBar/TopBar';
import PageHeader from '../../../components/PageHeader/PageHeader';
import useAsync from '../../../hooks/useAsync';
import { adminAPI } from '../../../api/apiGateway';
import { adminDashboardNav } from '../../../config/navConfigs';
import styles from './securityPages.module.css';

const nav = adminDashboardNav.map((n) =>
  n.path === '/admin/backups' ? { ...n, active: true } : n);

function fmtSize(bytes) {
  if (!bytes) return '0 B';
  const u = ['B', 'KB', 'MB', 'GB'];
  let i = 0; let n = bytes;
  while (n >= 1024 && i < u.length - 1) { n /= 1024; i += 1; }
  return `${n.toFixed(1)} ${u[i]}`;
}

export default function BackupsPage() {
  const { data, loading, error, reload } = useAsync(adminAPI.getBackups);
  const [busy, setBusy] = useState(false);
  const backups = data?.backups ?? [];
  const restoreEnabled = data?.restore_enabled;

  const create = async () => {
    setBusy(true);
    try {
      const meta = await adminAPI.createBackup();
      window.alert(`Backup created: ${meta.filename} (${fmtSize(meta.size)})`);
      reload();
    } catch (e) {
      window.alert(e.response?.data?.detail || 'Backup failed');
    } finally {
      setBusy(false);
    }
  };

  const restore = async (b) => {
    if (!window.confirm(`Restore ${b.filename}? This OVERWRITES the live database.`)) return;
    try {
      await adminAPI.restoreBackup(b.filename, `RESTORE-${b.filename}`);
      window.alert('Restore complete.');
    } catch (e) {
      window.alert(e.response?.data?.detail || 'Restore failed');
    }
  };

  return (
    <AppShell navItems={nav} logoVariant="icon-text" sidebarLabel="ADMIN PANEL" topBar={<TopBar />}>
      <div className={styles.breadcrumb}>ADMIN / BACKUPS</div>
      <PageHeader
        title="Encrypted Backups"
        subtitle="AES-256-GCM encrypted database snapshots."
        actions={<button className={styles.createBtn} onClick={create} disabled={busy}>
          {busy ? 'Creating…' : '+ Create Backup'}
        </button>}
      />

      {!restoreEnabled && (
        <div className={`${styles.pill} ${styles.pillAmber}`} style={{ marginTop: 8 }}>
          Restore is disabled (set ALLOW_DB_RESTORE=true to enable)
        </div>
      )}

      <div className={styles.tableCard}>
        {loading ? <div className={styles.state}>Loading…</div>
          : error ? <div className={styles.state}>{error} <button className={styles.iconBtn} onClick={reload}>Retry</button></div>
          : backups.length === 0 ? <div className={styles.state}>No backups yet.</div>
          : (
            <table className={styles.table}>
              <thead>
                <tr><th>Filename</th><th>Size</th><th>Checksum (SHA-256)</th><th>Created</th><th></th></tr>
              </thead>
              <tbody>
                {backups.map((b) => (
                  <tr key={b.filename}>
                    <td className={styles.mono}>{b.filename}</td>
                    <td>{fmtSize(b.size)}</td>
                    <td className={styles.mono}>{(b.sha256 || '').slice(0, 16)}…</td>
                    <td className={styles.mono}>{b.timestamp}</td>
                    <td>
                      {restoreEnabled
                        ? <button className={`${styles.iconBtn} ${styles.iconBtnDanger}`} onClick={() => restore(b)}>Restore</button>
                        : <span className={styles.pill + ' ' + styles.pillGray}>locked</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
      </div>
    </AppShell>
  );
}
