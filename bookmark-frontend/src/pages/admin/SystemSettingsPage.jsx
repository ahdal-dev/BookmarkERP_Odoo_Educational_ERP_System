import { useState } from 'react';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import StatusPill from '../../components/StatusPill/StatusPill';
import ToggleSwitch from '../../components/ToggleSwitch/ToggleSwitch';
import { adminNav } from '../../config/navConfigs';
import w from '../_shared/workflow.module.css';

/* System Administrator — global ERP configuration. */

const SECTIONS = ['General', 'Security', 'Notifications', 'Integrations', 'Maintenance'];

export default function SystemSettingsPage() {
  const [section, setSection] = useState('General');
  const [toggles, setToggles] = useState({
    mfa: true, email: true, sms: false, portal: true, deadlines: true, maintenance: false,
  });
  const set = (k) => (v) => setToggles((p) => ({ ...p, [k]: v }));

  return (
    <AppShell navItems={adminNav} logoVariant="stacked" sidebarLabel="ADMINISTRATION">
      <PageHeader title="System Settings" subtitle="Global ERP Configuration · Bookmark Academic Suite" useBrandFont />

      <div className={w.split} style={{ gridTemplateColumns: '200px 1fr' }}>
        {/* Sub-nav */}
        <div className={w.card} style={{ padding: 10, alignSelf: 'start' }}>
          {SECTIONS.map((s) => (
            <button key={s} onClick={() => setSection(s)}
              style={{ display: 'block', width: '100%', textAlign: 'left', padding: '10px 14px', borderRadius: 8, border: 'none',
                       cursor: 'pointer', fontFamily: 'inherit', fontWeight: 600, fontSize: '0.86rem', marginBottom: 2,
                       background: section === s ? 'var(--color-bg-warm)' : 'transparent',
                       color: section === s ? 'var(--color-lime-dark)' : 'var(--color-text-secondary)' }}>
              {s}
            </button>
          ))}
        </div>

        {/* Section content */}
        <div className={w.card}>
          {section === 'General' && (
            <>
              <h3 className={w.cardTitle}>General</h3>
              <div className={w.cardGrid2} style={{ marginTop: 12 }}>
                <div className={w.field}><span className={w.fieldLabel}>Institution Name</span><input className={w.input} defaultValue="Bookmark University" /></div>
                <div className={w.field}><span className={w.fieldLabel}>Academic Year</span><input className={w.input} defaultValue="2026-2027" /></div>
                <div className={w.field}><span className={w.fieldLabel}>Active Semester</span><input className={w.input} defaultValue="Fall 2026" /></div>
                <div className={w.field}><span className={w.fieldLabel}>Support Email</span><input className={w.input} defaultValue="support@bookmark.edu" /></div>
                <div className={w.field}><span className={w.fieldLabel}>System Timezone</span><input className={w.input} defaultValue="Africa/Cairo" /></div>
              </div>
            </>
          )}

          {section === 'Security' && (
            <>
              <h3 className={w.cardTitle}>Security</h3>
              <div className={w.cardGrid2} style={{ marginTop: 12 }}>
                <div className={w.field}><span className={w.fieldLabel}>Session Timeout (min)</span><input type="number" className={w.input} defaultValue={30} /></div>
                <div className={w.field}><span className={w.fieldLabel}>Failed Login Lockout</span><input type="number" className={w.input} defaultValue={5} /></div>
                <div className={w.field}><span className={w.fieldLabel}>Password Policy</span><select className={w.select}><option>Strong (12+ chars, mixed)</option><option>Standard (8+ chars)</option></select></div>
              </div>
              <ToggleSwitch checked={toggles.mfa} onChange={set('mfa')} label="Enforce MFA" description="Require multi-factor for staff accounts" />
            </>
          )}

          {section === 'Notifications' && (
            <>
              <h3 className={w.cardTitle}>Notifications</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginTop: 12 }}>
                <ToggleSwitch checked={toggles.email} onChange={set('email')} label="Email Notifications" />
                <ToggleSwitch checked={toggles.sms} onChange={set('sms')} label="SMS Notifications" />
                <ToggleSwitch checked={toggles.portal} onChange={set('portal')} label="In-Portal Notifications" />
                <ToggleSwitch checked={toggles.deadlines} onChange={set('deadlines')} label="Petition Deadline Reminders" />
              </div>
            </>
          )}

          {section === 'Integrations' && (
            <>
              <h3 className={w.cardTitle}>Integrations</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginTop: 12 }}>
                {[['OCR Engine', 'ONLINE'], ['AI Chatbot', 'ONLINE'], ['LDAP Sync', 'ONLINE']].map(([name, st]) => (
                  <div key={name} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', border: '1px solid var(--color-border-light)', borderRadius: 10, padding: 14 }}>
                    <span style={{ fontWeight: 600 }}><span className={w.pulse} />{name}</span>
                    <span style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
                      <StatusPill status={st} variant="green" />
                      <button className={`${w.btn} ${w.btnOutline} ${w.btnSm}`}>Run Test</button>
                    </span>
                  </div>
                ))}
              </div>
            </>
          )}

          {section === 'Maintenance' && (
            <>
              <h3 className={w.cardTitle}>Maintenance</h3>
              <div style={{ display: 'flex', gap: 12, marginTop: 12, flexWrap: 'wrap' }}>
                <button className={`${w.btn} ${w.btnOutline}`}>Clear Cache</button>
                <button className={`${w.btn} ${w.btnOutline}`}>Run DB Backup Now</button>
              </div>
              <div style={{ marginTop: 16 }}>
                <ToggleSwitch checked={toggles.maintenance} onChange={set('maintenance')} label="Maintenance Mode" description="⚠️ Takes the platform offline for students" />
              </div>
            </>
          )}
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12, marginTop: 20 }}>
        <button className={`${w.btn} ${w.btnOutline}`}>Discard Changes</button>
        <button className={`${w.btn} ${w.btnPrimary}`}>Commit Changes</button>
      </div>
    </AppShell>
  );
}
