import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import ToggleSwitch from '../../components/ToggleSwitch/ToggleSwitch';
import StatusPill from '../../components/StatusPill/StatusPill';
import { navForRole } from '../../config/navConfigs';
import { ROLES } from '../../config/roles';
import { useAuth } from '../../context/AuthContext';
import w from '../_shared/workflow.module.css';

/* Global Settings — available to every authenticated role. Common sections
   render for everyone; a role-specific section renders below where relevant. */

const ROLE_LABELS = {
  [ROLES.STUDENT]: 'Student',
  [ROLES.INSTRUCTOR]: 'Instructor',
  [ROLES.ACADEMIC_ADVISOR]: 'Academic Advisor',
  [ROLES.DEPARTMENT_CHAIR]: 'Department Chair',
  [ROLES.REGISTRAR]: 'Registrar',
  [ROLES.SUPPORT_TECHNICIAN]: 'Support Technician',
  [ROLES.ADMISSION_OFFICER]: 'Admission Officer',
  [ROLES.SUPER_ADMIN]: 'Super Administrator',
};

export default function SettingsPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const role = user?.role;
  const navItems = useMemo(() => navForRole(role), [role]);

  const baseSections = ['Profile', 'Account & Security', 'Notifications', 'Appearance'];
  const roleSection = roleSectionFor(role);
  const sections = roleSection ? [...baseSections, roleSection.label] : baseSections;

  const [section, setSection] = useState('Profile');
  const [prefs, setPrefs] = useState({
    email: true, inApp: true, sms: false, petitionUpdates: true, registrationAlerts: true,
  });
  const [compact, setCompact] = useState(() => localStorage.getItem('bookmark_sidebar_collapsed') === 'true');
  const setPref = (k) => (v) => setPrefs((p) => ({ ...p, [k]: v }));

  const onCompactChange = (v) => {
    setCompact(v);
    localStorage.setItem('bookmark_sidebar_collapsed', String(v));
  };

  return (
    <AppShell navItems={navItems} logoVariant="stacked" sidebarLabel="SETTINGS">
      <PageHeader
        title="Settings"
        subtitle="Manage your account, preferences, and role-specific options"
        useBrandFont
        badge={ROLE_LABELS[role] || 'User'}
        badgeVariant="green"
      />

      <div className={w.split} style={{ gridTemplateColumns: '210px 1fr' }}>
        {/* Sub-nav */}
        <div className={w.card} style={{ padding: 10, alignSelf: 'start' }}>
          {sections.map((s) => (
            <button
              key={s}
              onClick={() => setSection(s)}
              style={{
                display: 'block', width: '100%', textAlign: 'left', padding: '10px 14px', borderRadius: 8,
                border: 'none', cursor: 'pointer', fontFamily: 'inherit', fontWeight: 600, fontSize: '0.86rem', marginBottom: 2,
                background: section === s ? 'var(--color-bg-warm)' : 'transparent',
                color: section === s ? 'var(--color-lime-dark)' : 'var(--color-text-secondary)',
              }}
            >
              {s}
            </button>
          ))}
        </div>

        {/* Section content */}
        <div className={w.card}>
          {section === 'Profile' && (
            <>
              <h3 className={w.cardTitle}>Profile</h3>
              <p className={w.cardSub}>Your personal information.</p>
              <div className={w.cardGrid2}>
                <div className={w.field}><span className={w.fieldLabel}>Full Name</span><input className={w.input} defaultValue={user?.name || ''} /></div>
                <div className={w.field}><span className={w.fieldLabel}>Email</span><input className={w.input} defaultValue={user?.email || ''} type="email" /></div>
                <div className={w.field}><span className={w.fieldLabel}>Role</span><input className={w.input} value={ROLE_LABELS[role] || role || ''} readOnly /></div>
                <div className={w.field}><span className={w.fieldLabel}>Preferred Language</span>
                  <select className={w.select}><option>English</option><option>Arabic</option></select>
                </div>
              </div>
            </>
          )}

          {section === 'Account & Security' && (
            <>
              <h3 className={w.cardTitle}>Account &amp; Security</h3>
              <p className={w.cardSub}>Update your password and protect your account.</p>
              <div className={w.cardGrid2}>
                <div className={w.field}><span className={w.fieldLabel}>Current Password</span><input className={w.input} type="password" placeholder="••••••••" /></div>
                <div />
                <div className={w.field}><span className={w.fieldLabel}>New Password</span><input className={w.input} type="password" placeholder="••••••••" /></div>
                <div className={w.field}><span className={w.fieldLabel}>Confirm New Password</span><input className={w.input} type="password" placeholder="••••••••" /></div>
              </div>
              <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
                <button className={`${w.btn} ${w.btnPrimary} ${w.btnSm}`} onClick={() => navigate('/change-password')}>Change Password</button>
                <button className={`${w.btn} ${w.btnOutline} ${w.btnSm}`} onClick={() => navigate('/settings/security/mfa')}>Manage Two-Factor Auth</button>
              </div>
            </>
          )}

          {section === 'Notifications' && (
            <>
              <h3 className={w.cardTitle}>Notification Preferences</h3>
              <p className={w.cardSub}>Choose how you want to be notified.</p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                <ToggleSwitch checked={prefs.email} onChange={setPref('email')} label="Email Notifications" />
                <ToggleSwitch checked={prefs.inApp} onChange={setPref('inApp')} label="In-Portal Notifications" />
                <ToggleSwitch checked={prefs.sms} onChange={setPref('sms')} label="SMS Notifications" />
                <ToggleSwitch checked={prefs.petitionUpdates} onChange={setPref('petitionUpdates')} label="Petition Updates" />
                <ToggleSwitch checked={prefs.registrationAlerts} onChange={setPref('registrationAlerts')} label="Registration Alerts" />
              </div>
              <button className={`${w.btn} ${w.btnOutline} ${w.btnSm}`} style={{ marginTop: 12 }} onClick={() => navigate('/notifications')}>
                Open Notifications Hub →
              </button>
            </>
          )}

          {section === 'Appearance' && (
            <>
              <h3 className={w.cardTitle}>Appearance</h3>
              <p className={w.cardSub}>Tune how the interface looks for you.</p>
              <ToggleSwitch
                checked={compact}
                onChange={onCompactChange}
                label="Compact Sidebar"
                description="Collapse the sidebar to icons by default"
              />
            </>
          )}

          {roleSection && section === roleSection.label && (
            <>
              <h3 className={w.cardTitle}>{roleSection.label}</h3>
              <p className={w.cardSub}>{roleSection.subtitle}</p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginTop: 4 }}>
                {roleSection.items.map((it) => (
                  <div key={it.label} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', border: '1px solid var(--color-border-light)', borderRadius: 10, padding: 14 }}>
                    <span>
                      <strong style={{ fontSize: '0.9rem' }}>{it.label}</strong>
                      <span style={{ display: 'block', fontSize: '0.78rem', color: 'var(--color-text-muted)' }}>{it.hint}</span>
                    </span>
                    {it.to
                      ? <button className={`${w.btn} ${w.btnOutline} ${w.btnSm}`} onClick={() => navigate(it.to)}>Open</button>
                      : <StatusPill status={it.badge || 'Configured'} variant="green" />}
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12, marginTop: 20 }}>
        <button className={`${w.btn} ${w.btnOutline}`}>Discard</button>
        <button className={`${w.btn} ${w.btnPrimary}`}>Save Changes</button>
      </div>
    </AppShell>
  );
}

/* Role-specific settings section definitions. */
function roleSectionFor(role) {
  switch (role) {
    case ROLES.STUDENT:
      return {
        label: 'Academic',
        subtitle: 'Preferences tied to your studies.',
        items: [
          { label: 'Default Term View', hint: 'Term shown first on your dashboard', badge: 'Fall 2026' },
          { label: 'Advisor Sharing', hint: 'Let your advisor see draft petitions', badge: 'Enabled' },
        ],
      };
    case ROLES.INSTRUCTOR:
    case ROLES.ACADEMIC_ADVISOR:
    case ROLES.DEPARTMENT_CHAIR:
      return {
        label: 'Teaching',
        subtitle: 'Defaults for your courses and queues.',
        items: [
          { label: 'Office Hours', hint: 'Published to your advisees', badge: 'Set' },
          { label: 'Petition Queue Digest', hint: 'Daily summary email', badge: 'Daily' },
        ],
      };
    case ROLES.REGISTRAR:
      return {
        label: 'Registration',
        subtitle: 'Registration window and policy defaults.',
        items: [
          { label: 'Registration Ruleset', hint: 'Institutional registration rules', to: '/admin/settings/registration-rules' },
          { label: 'Default Term', hint: 'Active registration term', badge: 'Fall 2026' },
        ],
      };
    case ROLES.ADMISSION_OFFICER:
      return {
        label: 'Admissions',
        subtitle: 'Defaults for the admissions pipeline.',
        items: [
          { label: 'Pipeline View', hint: 'Default applicant board layout', badge: 'Kanban' },
          { label: 'Document Review', hint: 'Auto-run OCR on upload', badge: 'Enabled' },
        ],
      };
    case ROLES.SUPPORT_TECHNICIAN:
      return {
        label: 'Support',
        subtitle: 'Live queue and ticket preferences.',
        items: [
          { label: 'Auto-assign Tickets', hint: 'Pull from the shared queue', badge: 'On' },
          { label: 'Away Status', hint: 'Pause new chat assignments', badge: 'Available' },
        ],
      };
    case ROLES.SUPER_ADMIN:
      return {
        label: 'Administration',
        subtitle: 'System-wide configuration.',
        items: [
          { label: 'System Settings', hint: 'Global ERP configuration', to: '/admin/settings' },
          { label: 'User Management', hint: 'Manage accounts and roles', to: '/admin/users' },
          { label: 'Audit Log', hint: 'Review system activity', to: '/admin/audit-log' },
        ],
      };
    default:
      return null;
  }
}
