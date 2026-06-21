import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AppShell from '../../components/AppShell/AppShell';
import TopBar from '../../components/TopBar/TopBar';
import PageHeader from '../../components/PageHeader/PageHeader';
import StatCard from '../../components/StatCard/StatCard';
import DataTable from '../../components/DataTable/DataTable';
import StatusPill from '../../components/StatusPill/StatusPill';
import Pagination from '../../components/Pagination/Pagination';
import CreateUserModal from '../../components/CreateUserModal/CreateUserModal';
import useAsync from '../../hooks/useAsync';
import { adminAPI } from '../../api/apiGateway';
import { adminDashboardNav } from '../../config/navConfigs';
import styles from './UserManagementPage.module.css';

/* ============================================================
   USER MANAGEMENT PAGE — Admin user directory
   ============================================================ */

const STATUS_DOT = { Active: 'green', Inactive: 'yellow', Suspended: 'coral' };
const mockUsers = [];
const mockUserStats = { totalAccounts: 0, activeNow: 0, delta: '+0%', permissionConsistency: 100 };

const columns = [
  { key: 'name', header: 'Name', sortable: true },
  { key: 'email', header: 'Email', sortable: true },
  {
    key: 'role', header: 'Assigned Role', sortable: true,
    render: (val) => <StatusPill status={val} />,
  },
  {
    key: 'status', header: 'Status',
    render: (val, row) => (
      <span className={styles.statusCell}>
        <span className={styles.dot} style={{ background: `var(--color-${STATUS_DOT[val] || 'lime'})` }} />
        {val}
      </span>
    ),
  },
];

const navWithActive = adminDashboardNav.map((n) =>
  n.path === '/admin/users' ? { ...n, active: true } : n
);

export default function UserManagementPage() {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [modalOpen, setModalOpen] = useState(false);

  const { data: usersData, loading, error } = useAsync(adminAPI.getUsers);

  const liveUsers = usersData?.users?.map((u) => ({
    id: u.id,
    name: u.name,
    email: u.email,
    role: u.role,
    status: u.status,
  }));

  const users = liveUsers ?? mockUsers;
  const totalAccounts = usersData?.total_accounts ?? mockUserStats.totalAccounts;
  const activeNow = usersData?.active_now ?? mockUserStats.activeNow;

  const reload = () => window.location.reload();

  const deactivate = async (u) => {
    if (!window.confirm(`Deactivate ${u.name}?`)) return;
    try {
      await adminAPI.deleteUser(u.id);
      reload();
    } catch (e) {
      console.error('Failed to deactivate user:', e);
    }
  };

  const tableColumns = [
    ...columns,
    {
      key: 'actions', header: 'Actions',
      render: (_, r) => (
        <span className={styles.actionIcons}>
          <button className={styles.iconBtn} aria-label="Deactivate" title="Deactivate" onClick={() => deactivate(r)}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M3 6h18m-2 0v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>
          </button>
        </span>
      ),
    },
  ];

  const paged = users.slice((page - 1) * 8, page * 8);

  return (
    <AppShell
      navItems={navWithActive}
      logoVariant="icon-text"
      sidebarLabel="ADMIN PANEL"
      topBar={<TopBar searchPlaceholder="Search users, roles, or departments..." />}
    >
      {/* Tab Row */}
      <div className={styles.tabs}>
        <span className={styles.tab}>Overview</span>
        <span className={styles.tabDivider}>|</span>
        <span className={styles.tab}>Analytics</span>
        <span className={styles.tabDivider}>|</span>
        <span className={`${styles.tab} ${styles.tabActive}`}>User Management</span>
      </div>

      {/* Breadcrumb */}
      <div className={styles.breadcrumb}>ADMIN CONTROL / USER DIRECTORY</div>

      {/* Header */}
      <PageHeader
        title="User Management"
        subtitle="Oversee institutional access, manage permission matrices..."
        actions={
          <button className={styles.createBtn} onClick={() => setModalOpen(true)}>
            + Create User
          </button>
        }
      />

      {/* Stats Row */}
      <div className={styles.statsRow}>
        <StatCard
          label="TOTAL ACCOUNTS"
          value={totalAccounts}
          delta={mockUserStats.delta}
        />
        <StatCard
          label="ACTIVE NOW"
          value={activeNow}
        >
          {/* Avatar stack */}
          <div className={styles.avatarStack}>
            {['A', 'E', 'J'].map((l, i) => (
              <div key={i} className={styles.miniAvatar}>{l}</div>
            ))}
            <div className={styles.miniAvatarMore}>+{Math.max(0, activeNow - 3).toLocaleString()}</div>
          </div>
        </StatCard>
        <div className={styles.permCard}>
          <div className={styles.permTop}>
            <span className={styles.permLabel}>Permission Consistency: {mockUserStats.permissionConsistency}%</span>
            <span className={styles.permDesc}>All registrar roles synchronized with LDAP</span>
          </div>
          <button className={styles.auditBtn}>Run Integrity Audit</button>
        </div>
      </div>

      {/* Data Table */}
      <div className={styles.tableCard}>
        {loading ? (
          <div style={{ padding: 40, textAlign: 'center', color: 'var(--color-text-muted)' }}>Loading users…</div>
        ) : error ? (
          <div style={{ padding: 40, textAlign: 'center', color: 'var(--color-text-muted)' }}>
            {error} <button className={styles.auditBtn} onClick={reload} style={{ marginLeft: 8 }}>Retry</button>
          </div>
        ) : (
          <DataTable
            columns={tableColumns}
            data={paged}
            selectable
          />
        )}
      </div>

      {/* Footer */}
      <div className={styles.tableFooter}>
        <span className={styles.showing}>Showing 1–{users.length} of {totalAccounts.toLocaleString()} users</span>
        <Pagination currentPage={page} totalPages={8} onPageChange={setPage} />
      </div>

      {/* Create User Modal */}
      <CreateUserModal isOpen={modalOpen} onClose={() => setModalOpen(false)} />
    </AppShell>
  );
}
