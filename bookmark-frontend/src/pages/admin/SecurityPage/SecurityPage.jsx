import { useState } from 'react';
import AppShell from '../../../components/AppShell/AppShell';
import TopBar from '../../../components/TopBar/TopBar';
import PageHeader from '../../../components/PageHeader/PageHeader';
import DataTable from '../../../components/DataTable/DataTable';
import StatusPill from '../../../components/StatusPill/StatusPill';
import { adminDashboardNav } from '../../../config/navConfigs';
import {
  mockSecurityScore,
  mockSecurityAlerts,
  mockAuditLogs,
  mockActiveSessions,
  mockAPIKeys,
  openTicketCount,
} from '../../../mocks/adminMocks';
import styles from './SecurityPage.module.css';

// Security center — audit logs, active sessions, API key vault, threat alerts

const navWithActive = adminDashboardNav.map((n) =>
  n.path === '/admin/security' ? { ...n, active: true } : n
);

function downloadCSV(rows, filename) {
  const headers = Object.keys(rows[0]);
  const csv = [
    headers.map((h) => `"${h}"`).join(','),
    ...rows.map((r) => headers.map((h) => `"${String(r[h] ?? '').replace(/"/g, '""')}"`).join(',')),
  ].join('\n');
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

const SEVERITY = { high: styles.sevHigh, medium: styles.sevMed, low: styles.sevLow };

const AUDIT_COLS = [
  { key: 'timestamp', header: 'Timestamp', sortable: true, render: (v) => <span className={styles.mono}>{v}</span> },
  { key: 'user', header: 'User / IP', sortable: true },
  {
    key: 'action', header: 'Action',
    render: (v) => {
      const isWarn = v.includes('FAIL') || v.includes('LOCK');
      return <span className={isWarn ? styles.actionWarn : styles.actionNorm}>{v}</span>;
    },
  },
  { key: 'resource', header: 'Resource' },
  { key: 'ip', header: 'IP Address', render: (v) => <span className={styles.mono}>{v}</span> },
];

export default function SecurityPage() {
  const [activeTab, setActiveTab] = useState('audit');
  const [alerts, setAlerts] = useState(mockSecurityAlerts);
  const [apiKeys, setApiKeys] = useState(mockAPIKeys);
  const [sessions, setSessions] = useState(mockActiveSessions);
  const [showNewKey, setShowNewKey] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');

  const terminateSession = (id) => setSessions((prev) => prev.filter((s) => s.id !== id));
  const terminateAllSessions = () => setSessions([]);

  const SESSION_COLS = [
    { key: 'user', header: 'User', sortable: true },
    { key: 'role', header: 'Role', render: (v) => <StatusPill status={v} /> },
    { key: 'ip', header: 'IP', render: (v) => <span className={styles.mono}>{v}</span> },
    { key: 'device', header: 'Device' },
    { key: 'location', header: 'Location' },
    { key: 'lastActive', header: 'Last Active' },
    {
      key: 'actions', header: 'Actions',
      render: (_, row) => <button className={styles.terminateBtn} onClick={() => terminateSession(row.id)}>Terminate</button>,
    },
  ];

  const scoreColor = mockSecurityScore >= 90 ? 'var(--color-lime)' : mockSecurityScore >= 70 ? 'var(--color-yellow)' : 'var(--color-coral)';
  const scoreLabel = mockSecurityScore >= 90 ? 'STRONG' : mockSecurityScore >= 70 ? 'MODERATE' : 'AT RISK';

  const dismissAlert = (id) => setAlerts((prev) => prev.filter((a) => a.id !== id));
  const revokeKey = (id) => setApiKeys((prev) => prev.map((k) => k.id === id ? { ...k, isActive: false } : k));

  return (
    <AppShell
      navItems={navWithActive}
      logoVariant="icon-text"
      sidebarLabel="ADMIN PANEL"
      topBar={<TopBar searchPlaceholder="Search security events..." notificationCount={openTicketCount} />}
    >
      <div className={styles.breadcrumb}>INSIGHTS / SECURITY CENTER</div>

      <PageHeader
        title="Security Center"
        subtitle="Audit logs, active sessions, API keys, and threat detection."
        actions={
          <button
            className={styles.exportBtn}
            onClick={() => downloadCSV(mockAuditLogs, `audit-log-${new Date().toISOString().split('T')[0]}.csv`)}
          >
            Export Audit Log
          </button>
        }
      />

      {/* Top Row: Score + Alerts */}
      <div className={styles.topRow}>
        {/* Security Score */}
        <div className={styles.scoreCard}>
          <div className={styles.scoreHeader}>
            <span className={styles.scoreTitle}>Security Score</span>
          </div>
          <div className={styles.scoreBody}>
            <div className={styles.scoreRing}>
              <svg width="120" height="120" viewBox="0 0 120 120">
                <circle cx="60" cy="60" r="50" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="10"/>
                <circle
                  cx="60" cy="60" r="50" fill="none"
                  stroke={scoreColor} strokeWidth="10"
                  strokeLinecap="round"
                  strokeDasharray={`${2 * Math.PI * 50}`}
                  strokeDashoffset={`${2 * Math.PI * 50 * (1 - mockSecurityScore / 100)}`}
                  transform="rotate(-90 60 60)"
                />
              </svg>
              <div className={styles.scoreOverlay}>
                <span className={styles.scoreNumber}>{mockSecurityScore}</span>
                <span className={styles.scoreMax}>/100</span>
              </div>
            </div>
            <span className={styles.scoreLabel} style={{ color: scoreColor }}>{scoreLabel}</span>
          </div>
        </div>

        {/* Active Alerts */}
        <div className={styles.alertsCard}>
          <div className={styles.alertsHeader}>
            <span className={styles.alertsTitle}>Active Security Alerts</span>
            <span className={styles.alertsBadge}>{alerts.filter((a) => !a.resolved).length} open</span>
          </div>
          <div className={styles.alertsList}>
            {alerts.map((alert) => (
              <div key={alert.id} className={`${styles.alertRow} ${alert.resolved ? styles.alertResolved : ''}`}>
                <span className={`${styles.sevPill} ${SEVERITY[alert.severity] || ''}`}>
                  {alert.severity.toUpperCase()}
                </span>
                <div className={styles.alertContent}>
                  <span className={styles.alertMsg}>{alert.message}</span>
                  <span className={styles.alertTime}>{alert.time}</span>
                </div>
                {!alert.resolved && (
                  <button className={styles.dismissBtn} onClick={() => dismissAlert(alert.id)}>
                    Dismiss
                  </button>
                )}
                {alert.resolved && <span className={styles.resolvedBadge}>Resolved</span>}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className={styles.tabs}>
        {[
          { key: 'audit', label: 'Audit Log' },
          { key: 'sessions', label: 'Active Sessions' },
          { key: 'apikeys', label: 'API Key Vault' },
        ].map((t) => (
          <button
            key={t.key}
            className={`${styles.tab} ${activeTab === t.key ? styles.tabActive : ''}`}
            onClick={() => setActiveTab(t.key)}
          >{t.label}</button>
        ))}
      </div>

      {/* ── Audit Log ── */}
      {activeTab === 'audit' && (
        <div className={styles.tableCard}>
          <DataTable columns={AUDIT_COLS} data={mockAuditLogs} selectable />
        </div>
      )}

      {/* ── Active Sessions ── */}
      {activeTab === 'sessions' && (
        <>
          <div className={styles.sessionsMeta}>
            <span className={styles.sessionCount}>{sessions.length} active sessions</span>
            <button className={styles.terminateAllBtn} onClick={terminateAllSessions}>Terminate All Sessions</button>
          </div>
          <div className={styles.tableCard}>
            <DataTable columns={SESSION_COLS} data={sessions} />
          </div>
        </>
      )}

      {/* ── API Key Vault ── */}
      {activeTab === 'apikeys' && (
        <>
          <div className={styles.keyHeader}>
            <span className={styles.keyCount}>{apiKeys.length} keys registered</span>
            <button className={styles.generateBtn} onClick={() => setShowNewKey(true)}>+ Generate New Key</button>
          </div>
          <div className={styles.keyList}>
            {apiKeys.map((key) => (
              <div key={key.id} className={`${styles.keyCard} ${!key.isActive ? styles.keyRevoked : ''}`}>
                <div className={styles.keyMain}>
                  <div className={styles.keyIcon}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 11-7.778 7.778 5.5 5.5 0 017.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/></svg>
                  </div>
                  <div className={styles.keyInfo}>
                    <span className={styles.keyName}>{key.name}</span>
                    <span className={styles.keyPrefix}>{key.prefix}</span>
                  </div>
                </div>
                <div className={styles.keyMeta}>
                  <span className={styles.keyMetaItem}>Scope: <strong>{key.scope}</strong></span>
                  <span className={styles.keyMetaItem}>Created: <strong>{key.created}</strong></span>
                  <span className={styles.keyMetaItem}>Last used: <strong>{key.lastUsed}</strong></span>
                </div>
                <div className={styles.keyActions}>
                  {key.isActive ? (
                    <>
                      <StatusPill status="Active" variant="green" />
                      <button className={styles.revokeBtn} onClick={() => revokeKey(key.id)}>Revoke</button>
                    </>
                  ) : (
                    <StatusPill status="Revoked" variant="coral" />
                  )}
                </div>
              </div>
            ))}
          </div>
        </>
      )}
      {showNewKey && (
        <div className={styles.modalOverlay} onClick={() => setShowNewKey(false)}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <span className={styles.modalTitle}>Generate New API Key</span>
              <button className={styles.modalClose} onClick={() => setShowNewKey(false)}>✕</button>
            </div>
            <div className={styles.modalBody}>
              <label className={styles.fieldLabel}>Key Name</label>
              <input
                className={styles.fieldInput}
                placeholder="e.g. Mobile Integration"
                value={newKeyName}
                onChange={(e) => setNewKeyName(e.target.value)}
              />
              <label className={styles.fieldLabel} style={{ marginTop: 16 }}>Scope</label>
              <select className={styles.fieldInput}>
                <option>/api/v2/*</option>
                <option>/api/ocr/*</option>
                <option>/api/export/*</option>
                <option>/api/admin/*</option>
              </select>
              <label className={styles.fieldLabel} style={{ marginTop: 16 }}>Expiry</label>
              <select className={styles.fieldInput}>
                <option>Never</option>
                <option>30 days</option>
                <option>90 days</option>
                <option>1 year</option>
              </select>
            </div>
            <div className={styles.modalFooter}>
              <button className={styles.cancelBtn} onClick={() => setShowNewKey(false)}>Cancel</button>
              <button
                className={styles.generateBtn}
                onClick={() => {
                  if (!newKeyName.trim()) return;
                  setApiKeys((prev) => [
                    ...prev,
                    { id: Date.now(), name: newKeyName, prefix: `bk_${newKeyName.substring(0, 3).toLowerCase()}_****`, scope: '/api/v2/*', created: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }), lastUsed: 'Never', isActive: true },
                  ]);
                  setNewKeyName('');
                  setShowNewKey(false);
                }}
              >
                Generate Key
              </button>
            </div>
          </div>
        </div>
      )}
    </AppShell>
  );
}
