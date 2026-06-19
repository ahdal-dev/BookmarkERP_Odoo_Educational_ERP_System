import { useState } from 'react';
import AppShell from '../../../components/AppShell/AppShell';
import TopBar from '../../../components/TopBar/TopBar';
import PageHeader from '../../../components/PageHeader/PageHeader';
import ToggleSwitch from '../../../components/ToggleSwitch/ToggleSwitch';
import StatusPill from '../../../components/StatusPill/StatusPill';
import { adminDashboardNav } from '../../../config/navConfigs';
import { mockFeatureFlags, mockBackups, mockSystemSettings, openTicketCount } from '../../../mocks/adminMocks';
import styles from './SystemPage.module.css';

// System settings — general config, feature flags, backups, integrations

const navWithActive = adminDashboardNav.map((n) =>
  n.path === '/admin/system' ? { ...n, active: true } : n
);

const TABS = ['General', 'Feature Flags', 'Backups', 'Integrations'];

const BACKUP_STATUS = { Success: 'green', Failed: 'coral', Running: 'yellow' };

function downloadBackup(backup) {
  const content = [
    'Bookmark Academic ERP — Backup Manifest',
    '========================================',
    `Date: ${backup.date}`,
    `Type: ${backup.type}`,
    `Size: ${backup.size}`,
    `Status: ${backup.status}`,
    `Checksum: sha256-${Math.random().toString(36).substring(2, 18)}`,
    '',
    'This file represents a backup archive.',
    'Restore using: System > Backups > Restore',
  ].join('\n');
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `backup-${backup.date.replace(/[\s:]/g, '-')}.txt`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export default function SystemPage() {
  const [activeTab, setActiveTab] = useState('General');
  const [flags, setFlags] = useState(mockFeatureFlags);
  const [settings, setSettings] = useState(mockSystemSettings);
  const [showSaved, setShowSaved] = useState(false);
  const [backupRunning, setBackupRunning] = useState(false);
  const [showNewFlag, setShowNewFlag] = useState(false);
  const [newFlagName, setNewFlagName] = useState('');
  const [configIntg, setConfigIntg] = useState(null);

  const toggleFlag = (id) =>
    setFlags((prev) => prev.map((f) => f.id === id ? { ...f, status: !f.status } : f));

  const toggleSetting = (key) =>
    setSettings((prev) => ({ ...prev, [key]: !prev[key] }));

  const commitChanges = () => {
    setShowSaved(true);
    setTimeout(() => setShowSaved(false), 2500);
  };

  const runBackup = () => {
    setBackupRunning(true);
    setTimeout(() => setBackupRunning(false), 2000);
  };

  const addFlag = () => {
    if (!newFlagName.trim()) return;
    setFlags((prev) => [
      ...prev,
      { id: Date.now(), name: newFlagName, description: 'Custom feature flag', status: false, rollout: 0 },
    ]);
    setNewFlagName('');
    setShowNewFlag(false);
  };

  return (
    <AppShell
      navItems={navWithActive}
      logoVariant="icon-text"
      sidebarLabel="ADMIN PANEL"
      topBar={<TopBar searchPlaceholder="Search system settings..." notificationCount={openTicketCount} />}
    >
      {showSaved && (
        <div className={styles.savedBanner}>Settings saved successfully.</div>
      )}

      <div className={styles.breadcrumb}>OPERATIONS / SYSTEM</div>

      <PageHeader
        title="System Settings"
        subtitle="Global configuration, feature flags, backup management, and integrations."
      />

      {/* Tabs */}
      <div className={styles.tabs}>
        {TABS.map((t) => (
          <button
            key={t}
            className={`${styles.tab} ${activeTab === t ? styles.tabActive : ''}`}
            onClick={() => setActiveTab(t)}
          >{t}</button>
        ))}
      </div>

      {/* ── General ── */}
      {activeTab === 'General' && (
        <div className={styles.twoCol}>
          <div className={styles.formCard}>
            <span className={styles.sectionLabel}>INSTITUTION</span>
            <div className={styles.fieldGrid}>
              <div className={styles.field}>
                <label className={styles.fieldLabel}>Institution Name</label>
                <input className={styles.fieldInput} defaultValue={settings.institutionName} />
              </div>
              <div className={styles.field}>
                <label className={styles.fieldLabel}>Default Language</label>
                <select className={styles.fieldInput} defaultValue={settings.language}>
                  <option>English</option>
                  <option>Arabic</option>
                </select>
              </div>
              <div className={styles.field}>
                <label className={styles.fieldLabel}>Timezone</label>
                <select className={styles.fieldInput} defaultValue={settings.timezone}>
                  <option>UTC+3 — Cairo</option>
                  <option>UTC+0 — London</option>
                  <option>UTC-5 — New York</option>
                </select>
              </div>
              <div className={styles.field}>
                <label className={styles.fieldLabel}>Academic Year Format</label>
                <select className={styles.fieldInput} defaultValue={settings.academicYearFormat}>
                  <option>YYYY-YYYY</option>
                  <option>YYYY/YYYY</option>
                </select>
              </div>
            </div>

            <span className={styles.sectionLabel} style={{ marginTop: 24 }}>PORTAL STATUS</span>
            <div className={styles.toggleList}>
              <ToggleSwitch
                checked={settings.maintenanceMode}
                onChange={() => toggleSetting('maintenanceMode')}
                label="Maintenance Mode"
                description="Puts the student portal in read-only mode. Admin panel remains accessible."
              />
              <ToggleSwitch
                checked={settings.registrationOpen}
                onChange={() => toggleSetting('registrationOpen')}
                label="Registration Open"
                description="Controls whether the course registration window is active."
              />
            </div>

            <div className={styles.saveRow}>
              <button className={styles.discardBtn} onClick={() => setSettings(mockSystemSettings)}>Discard Changes</button>
              <button className={styles.saveBtn} onClick={commitChanges}>Commit Changes</button>
            </div>
          </div>

          {/* System Status Panel */}
          <div className={styles.statusPanel}>
            <span className={styles.sectionLabel}>SYSTEM STATUS</span>
            {[
              { label: 'Ruleset Engine', status: 'Online' },
              { label: 'OCR Service', status: 'Online' },
              { label: 'RAG Chatbot', status: 'Degraded' },
              { label: 'LDAP Sync', status: 'Online' },
              { label: 'Email Gateway', status: 'Online' },
              { label: 'Backup Service', status: 'Online' },
            ].map((item) => (
              <div key={item.label} className={styles.statusRow}>
                <span
                  className={styles.statusDot}
                  style={{ background: item.status === 'Online' ? 'var(--color-lime)' : item.status === 'Degraded' ? 'var(--color-yellow)' : 'var(--color-coral)' }}
                />
                <span className={styles.statusLabel}>{item.label}</span>
                <span className={styles.statusText} style={{ color: item.status === 'Online' ? 'var(--color-lime-dark)' : 'var(--color-yellow)' }}>
                  {item.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Feature Flags ── */}
      {activeTab === 'Feature Flags' && (
        <>
          <div className={styles.flagsToolbar}>
            <span className={styles.flagCount}>{flags.length} flags · {flags.filter((f) => f.status).length} enabled</span>
            <button className={styles.newFlagBtn} onClick={() => setShowNewFlag(true)}>+ New Flag</button>
          </div>
          <div className={styles.flagsList}>
            {flags.map((flag) => (
              <div key={flag.id} className={styles.flagCard}>
                <div className={styles.flagLeft}>
                  <span className={styles.flagName}>{flag.name}</span>
                  <span className={styles.flagDesc}>{flag.description}</span>
                </div>
                <div className={styles.flagMeta}>
                  <div className={styles.rolloutRow}>
                    <span className={styles.rolloutLabel}>Rollout</span>
                    <div className={styles.rolloutTrack}>
                      <div className={styles.rolloutFill} style={{ width: `${flag.rollout}%`, background: flag.status ? 'var(--color-lime)' : 'var(--color-border-light)' }} />
                    </div>
                    <span className={styles.rolloutPct}>{flag.rollout}%</span>
                  </div>
                </div>
                <ToggleSwitch
                  checked={flag.status}
                  onChange={() => toggleFlag(flag.id)}
                  label={flag.status ? 'Enabled' : 'Disabled'}
                />
              </div>
            ))}
          </div>
        </>
      )}

      {/* ── Backups ── */}
      {activeTab === 'Backups' && (
        <div className={styles.twoCol}>
          <div className={styles.formCard}>
            <span className={styles.sectionLabel}>AUTO BACKUP CONFIGURATION</span>
            <div className={styles.toggleList}>
              <ToggleSwitch
                checked={settings.autoBackup}
                onChange={() => toggleSetting('autoBackup')}
                label="Automatic Backup"
                description="Runs a full database backup on the configured schedule."
              />
            </div>
            <div className={styles.fieldGrid} style={{ marginTop: 16 }}>
              <div className={styles.field}>
                <label className={styles.fieldLabel}>Frequency</label>
                <select className={styles.fieldInput} defaultValue={settings.backupFrequency}>
                  <option>Daily at 02:00 AM</option>
                  <option>Every 12 hours</option>
                  <option>Weekly</option>
                </select>
              </div>
              <div className={styles.field}>
                <label className={styles.fieldLabel}>Retention Period</label>
                <select className={styles.fieldInput} defaultValue={settings.backupRetention}>
                  <option>30 days</option>
                  <option>60 days</option>
                  <option>90 days</option>
                </select>
              </div>
            </div>
            <button className={styles.backupNowBtn} onClick={runBackup} disabled={backupRunning}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
              {backupRunning ? 'Running Backup...' : 'Run Manual Backup Now'}
            </button>
          </div>

          <div className={styles.backupHistoryCard}>
            <span className={styles.sectionLabel}>BACKUP HISTORY</span>
            <div className={styles.backupList}>
              {mockBackups.map((b) => (
                <div key={b.id} className={styles.backupRow}>
                  <div className={styles.backupInfo}>
                    <span className={styles.backupDate}>{b.date}</span>
                    <span className={styles.backupType}>{b.type} · {b.size}</span>
                  </div>
                  <StatusPill status={b.status} variant={BACKUP_STATUS[b.status] || 'black'} />
                  <div className={styles.backupActions}>
                    {b.status === 'Success' ? (
                      <>
                        <button className={styles.backupActionBtn} onClick={() => { if (window.confirm(`Restore from ${b.date}? This will replace current data.`)) runBackup(); }}>Restore</button>
                        <button className={styles.backupActionBtn} onClick={() => downloadBackup(b)}>Download</button>
                      </>
                    ) : (
                      <button className={styles.backupActionBtn} style={{ color: 'var(--color-coral)', borderColor: 'var(--color-coral)' }} onClick={runBackup}>Retry</button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ── Integrations ── */}
      {activeTab === 'Integrations' && (
        <div className={styles.integrationsList}>
          {[
            { name: 'LDAP / Active Directory', desc: 'User sync and authentication', status: 'Connected', lastSync: '5 min ago' },
            { name: 'SMTP Email Gateway', desc: 'Outbound email via SendGrid', status: 'Connected', lastSync: '1h ago' },
            { name: 'OCR Microservice', desc: 'Document extraction pipeline', status: 'Connected', lastSync: '2 min ago' },
            { name: 'Odoo ERP Backend', desc: 'Core ERP data (courses, grades)', status: 'Connected', lastSync: 'Live' },
            { name: 'Prometheus / Grafana', desc: 'Metrics and alerting', status: 'Connected', lastSync: 'Live' },
            { name: 'LMS Integration', desc: 'Moodle / Canvas sync (optional)', status: 'Not Connected', lastSync: '—' },
          ].map((intg) => (
            <div key={intg.name} className={styles.integrationCard}>
              <div className={styles.integrationInfo}>
                <span className={styles.integrationName}>{intg.name}</span>
                <span className={styles.integrationDesc}>{intg.desc}</span>
              </div>
              <span className={styles.integrationSync}>Last sync: {intg.lastSync}</span>
              <StatusPill
                status={intg.status}
                variant={intg.status === 'Connected' ? 'green' : 'coral'}
              />
              <button className={styles.configIntgBtn} onClick={() => setConfigIntg(intg)}>
                {intg.status === 'Connected' ? 'Configure' : 'Connect'}
              </button>
            </div>
          ))}
        </div>
      )}
      {showNewFlag && (
        <div className={styles.modalOverlay} onClick={() => setShowNewFlag(false)}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <span className={styles.modalTitle}>New Feature Flag</span>
              <button className={styles.modalCloseBtn} onClick={() => setShowNewFlag(false)}>✕</button>
            </div>
            <div className={styles.modalBody}>
              <label className={styles.modalFieldLabel}>Flag Key</label>
              <input
                className={styles.modalFieldInput}
                placeholder="e.g. new_registration_flow"
                value={newFlagName}
                onChange={(e) => setNewFlagName(e.target.value)}
              />
              <label className={styles.modalFieldLabel} style={{ marginTop: 14 }}>Description</label>
              <input className={styles.modalFieldInput} placeholder="What does this flag control?" />
              <label className={styles.modalFieldLabel} style={{ marginTop: 14 }}>Initial Rollout %</label>
              <input className={styles.modalFieldInput} type="number" min="0" max="100" defaultValue="0" />
            </div>
            <div className={styles.modalFooter}>
              <button className={styles.discardBtn} onClick={() => setShowNewFlag(false)}>Cancel</button>
              <button className={styles.saveBtn} onClick={addFlag}>Create Flag</button>
            </div>
          </div>
        </div>
      )}

      {configIntg && (
        <div className={styles.modalOverlay} onClick={() => setConfigIntg(null)}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <span className={styles.modalTitle}>{configIntg.status === 'Connected' ? 'Configure' : 'Connect'} — {configIntg.name}</span>
              <button className={styles.modalCloseBtn} onClick={() => setConfigIntg(null)}>✕</button>
            </div>
            <div className={styles.modalBody}>
              <p className={styles.intgDesc}>{configIntg.desc}</p>
              <label className={styles.modalFieldLabel}>Host / Endpoint</label>
              <input className={styles.modalFieldInput} placeholder="e.g. ldap://corp.domain.edu" />
              <label className={styles.modalFieldLabel} style={{ marginTop: 14 }}>Credentials / Token</label>
              <input className={styles.modalFieldInput} type="password" placeholder="API key or bind password" />
              <label className={styles.modalFieldLabel} style={{ marginTop: 14 }}>Sync Interval</label>
              <select className={styles.modalFieldInput}>
                <option>Every 5 minutes</option>
                <option>Every 15 minutes</option>
                <option>Every hour</option>
                <option>Manual only</option>
              </select>
            </div>
            <div className={styles.modalFooter}>
              <button className={styles.discardBtn} onClick={() => setConfigIntg(null)}>Cancel</button>
              <button className={styles.saveBtn} onClick={() => { setConfigIntg(null); commitChanges(); }}>Save Configuration</button>
            </div>
          </div>
        </div>
      )}
    </AppShell>
  );
}
