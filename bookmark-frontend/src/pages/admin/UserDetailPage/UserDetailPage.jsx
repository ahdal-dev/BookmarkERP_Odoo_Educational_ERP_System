import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import AppShell from '../../../components/AppShell/AppShell';
import TopBar from '../../../components/TopBar/TopBar';
import StatusPill from '../../../components/StatusPill/StatusPill';
import ToggleSwitch from '../../../components/ToggleSwitch/ToggleSwitch';
import { adminDashboardNav } from '../../../config/navConfigs';
import { mockUsers } from '../../../mocks/usersMocks';
import { openTicketCount } from '../../../mocks/adminMocks';
import styles from './UserDetailPage.module.css';

const ROLES_AVAILABLE = ['Student', 'Instructor', 'Registrar', 'Admin', 'Admission Officer', 'Academic Advisor', 'Department Chair', 'Support Technician'];
const STATUS_VARIANT = { Active: 'green', Inactive: 'yellow', Suspended: 'coral' };

const MOCK_ACTIVITY = [
  { action: 'Logged in', time: '2025-03-10 09:14', ip: '102.131.4.22' },
  { action: 'Viewed course catalog', time: '2025-03-10 09:16', ip: '102.131.4.22' },
  { action: 'Submitted petition form', time: '2025-03-09 14:32', ip: '102.131.4.22' },
  { action: 'Password changed', time: '2025-03-08 11:00', ip: '102.131.4.22' },
  { action: 'Logged in', time: '2025-03-08 10:58', ip: '102.131.4.22' },
  { action: 'Downloaded grade report', time: '2025-03-07 15:20', ip: '102.131.4.22' },
];

const navWithActive = adminDashboardNav.map((n) =>
  n.path === '/admin/users' ? { ...n, active: true } : n
);

export default function UserDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const found = mockUsers.find((u) => String(u.id) === id);
  const [user, setUser] = useState(
    found || {
      id: Number(id),
      name: 'Demo User',
      email: `user${id}@bookmark.edu`,
      role: 'Student',
      status: 'Active',
      department: 'General',
      lastLogin: '2025-03-10 09:00',
      createdAt: '2024-01-01',
      phone: 'N/A',
    }
  );

  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState({ name: user.name, email: user.email, role: user.role, phone: user.phone, department: user.department });
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setUser((prev) => ({ ...prev, ...draft }));
    setEditing(false);
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  return (
    <AppShell
      navItems={navWithActive}
      logoVariant="icon-text"
      sidebarLabel="ADMIN PANEL"
      topBar={<TopBar searchPlaceholder="Search users..." notificationCount={openTicketCount} />}
    >
      {/* Breadcrumb */}
      <div className={styles.breadcrumb}>
        <button className={styles.backLink} onClick={() => navigate('/admin/users')}>
          ← User Management
        </button>
        <span className={styles.breadSep}>/</span>
        <span>{user.name}</span>
      </div>

      {saved && (
        <div className={styles.savedBanner}>
          Changes saved successfully.
        </div>
      )}

      <div className={styles.layout}>
        {/* ── Left: Profile Card ── */}
        <div className={styles.sidebar}>
          <div className={styles.profileCard}>
            <div className={styles.avatarLg}>{user.name.charAt(0).toUpperCase()}</div>
            <div className={styles.profileName}>{user.name}</div>
            <div className={styles.profileEmail}>{user.email}</div>
            <StatusPill status={user.status} variant={STATUS_VARIANT[user.status] || 'black'} />
          </div>

          <div className={styles.metaCard}>
            <div className={styles.metaRow}>
              <span className={styles.metaLabel}>Role</span>
              <span className={styles.metaValue}>{user.role}</span>
            </div>
            <div className={styles.metaRow}>
              <span className={styles.metaLabel}>Department</span>
              <span className={styles.metaValue}>{user.department}</span>
            </div>
            <div className={styles.metaRow}>
              <span className={styles.metaLabel}>Phone</span>
              <span className={styles.metaValue}>{user.phone || '—'}</span>
            </div>
            <div className={styles.metaRow}>
              <span className={styles.metaLabel}>Last Login</span>
              <span className={styles.metaValue}>{user.lastLogin}</span>
            </div>
            <div className={styles.metaRow}>
              <span className={styles.metaLabel}>Member Since</span>
              <span className={styles.metaValue}>{user.createdAt}</span>
            </div>
          </div>

          {/* Status toggle */}
          <div className={styles.statusToggleCard}>
            <span className={styles.metaLabel}>Account Status</span>
            <div className={styles.statusToggleRow}>
              {['Active', 'Inactive', 'Suspended'].map((s) => (
                <button
                  key={s}
                  className={`${styles.statusChip} ${user.status === s ? styles.statusChipActive : ''}`}
                  style={user.status === s ? { background: s === 'Active' ? '#4caf27' : s === 'Suspended' ? '#e8613a' : '#f5c842', color: '#fff' } : {}}
                  onClick={() => setUser((prev) => ({ ...prev, status: s }))}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* ── Right: Edit Form + Activity ── */}
        <div className={styles.main}>
          {/* Edit form card */}
          <div className={styles.card}>
            <div className={styles.cardHeader}>
              <span className={styles.cardTitle}>Profile Information</span>
              {!editing && (
                <button className={styles.editBtn} onClick={() => setEditing(true)}>Edit</button>
              )}
            </div>

            {editing ? (
              <>
                <div className={styles.formGrid}>
                  <div className={styles.field}>
                    <label className={styles.fieldLabel}>Full Name</label>
                    <input
                      className={styles.fieldInput}
                      value={draft.name}
                      onChange={(e) => setDraft((d) => ({ ...d, name: e.target.value }))}
                    />
                  </div>
                  <div className={styles.field}>
                    <label className={styles.fieldLabel}>Email</label>
                    <input
                      className={styles.fieldInput}
                      value={draft.email}
                      onChange={(e) => setDraft((d) => ({ ...d, email: e.target.value }))}
                    />
                  </div>
                  <div className={styles.field}>
                    <label className={styles.fieldLabel}>Role</label>
                    <select
                      className={styles.fieldInput}
                      value={draft.role}
                      onChange={(e) => setDraft((d) => ({ ...d, role: e.target.value }))}
                    >
                      {ROLES_AVAILABLE.map((r) => <option key={r}>{r}</option>)}
                    </select>
                  </div>
                  <div className={styles.field}>
                    <label className={styles.fieldLabel}>Department</label>
                    <input
                      className={styles.fieldInput}
                      value={draft.department}
                      onChange={(e) => setDraft((d) => ({ ...d, department: e.target.value }))}
                    />
                  </div>
                  <div className={styles.field}>
                    <label className={styles.fieldLabel}>Phone</label>
                    <input
                      className={styles.fieldInput}
                      value={draft.phone}
                      onChange={(e) => setDraft((d) => ({ ...d, phone: e.target.value }))}
                    />
                  </div>
                </div>
                <div className={styles.saveRow}>
                  <button className={styles.cancelBtn} onClick={() => { setEditing(false); setDraft({ name: user.name, email: user.email, role: user.role, phone: user.phone, department: user.department }); }}>
                    Discard
                  </button>
                  <button className={styles.saveBtn} onClick={handleSave}>Save Changes</button>
                </div>
              </>
            ) : (
              <div className={styles.formGrid}>
                <div className={styles.readField}>
                  <span className={styles.fieldLabel}>Full Name</span>
                  <span className={styles.readValue}>{user.name}</span>
                </div>
                <div className={styles.readField}>
                  <span className={styles.fieldLabel}>Email</span>
                  <span className={styles.readValue}>{user.email}</span>
                </div>
                <div className={styles.readField}>
                  <span className={styles.fieldLabel}>Role</span>
                  <span className={styles.readValue}>{user.role}</span>
                </div>
                <div className={styles.readField}>
                  <span className={styles.fieldLabel}>Department</span>
                  <span className={styles.readValue}>{user.department}</span>
                </div>
                <div className={styles.readField}>
                  <span className={styles.fieldLabel}>Phone</span>
                  <span className={styles.readValue}>{user.phone || '—'}</span>
                </div>
              </div>
            )}
          </div>

          {/* Activity log */}
          <div className={styles.card}>
            <div className={styles.cardHeader}>
              <span className={styles.cardTitle}>Recent Activity</span>
              <span className={styles.cardSub}>Last 7 days</span>
            </div>
            <div className={styles.activityList}>
              {MOCK_ACTIVITY.map((ev, i) => (
                <div key={i} className={styles.activityRow}>
                  <div className={styles.activityDot} />
                  <div className={styles.activityInfo}>
                    <span className={styles.activityAction}>{ev.action}</span>
                    <span className={styles.activityMeta}>{ev.time} · IP {ev.ip}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Danger zone */}
          <div className={styles.dangerCard}>
            <span className={styles.dangerTitle}>Danger Zone</span>
            <div className={styles.dangerActions}>
              <button className={styles.dangerBtn} onClick={() => setUser((p) => ({ ...p, status: 'Suspended' }))}>
                Suspend Account
              </button>
              <button className={styles.dangerBtnRed}>
                Delete Account
              </button>
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
