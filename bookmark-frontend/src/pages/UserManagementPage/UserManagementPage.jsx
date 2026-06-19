import { useState } from 'react';
import AppShell from '../../components/AppShell/AppShell';
import TopBar from '../../components/TopBar/TopBar';
import PageHeader from '../../components/PageHeader/PageHeader';
import StatCard from '../../components/StatCard/StatCard';
import DataTable from '../../components/DataTable/DataTable';
import StatusPill from '../../components/StatusPill/StatusPill';
import Pagination from '../../components/Pagination/Pagination';
import CreateUserModal from '../../components/CreateUserModal/CreateUserModal';
import { adminUsersNav } from '../../config/navConfigs';
import { adminAPI } from '../../api/apiGateway';
import useAsync from '../../hooks/useAsync';
import styles from './UserManagementPage.module.css';

/* ============================================================
   USER MANAGEMENT PAGE — Admin user directory
   ============================================================ */

const STATUS_DOT = { Active: 'green', Inactive: 'yellow', Suspended: 'coral' };

const ROLE_LABELS = {
  super_admin: 'Super Admin',
  registrar: 'Registrar',
  department_chair: 'Department Chair',
  academic_advisor: 'Academic Advisor',
  instructor: 'Instructor',
  admission_officer: 'Admission Officer',
  support_technician: 'Support',
  student: 'Student',
  prospective_student: 'Prospective',
  staff: 'Staff',
};

const columns = [
  { key: 'name', header: 'Name', sortable: true },
  { key: 'email', header: 'Email', sortable: true },
  {
    key: 'role', header: 'Assigned Role', sortable: true,
    render: (val) => <StatusPill status={ROLE_LABELS[val] || val} />,
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

const PER_PAGE = 10;

export default function UserManagementPage() {
  const [page, setPage] = useState(1);
  const [modalOpen, setModalOpen] = useState(false);
  const { data, loading, error, reload } = useAsync(() => adminAPI.getUsers(), []);

  const users = data?.users || [];
  const totalPages = Math.max(1, Math.ceil(users.length / PER_PAGE));
  const paged = users.slice((page - 1) * PER_PAGE, page * PER_PAGE);

  const deactivate = async (u) => {
    if (!window.confirm(`Deactivate ${u.name}?`)) return;
    try { await adminAPI.deleteUser(u.id); reload(); } catch { /* ignore */ }
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

  return (
    <AppShell
      navItems={adminUsersNav}
      logoVariant="icon-text"
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
          value={data?.total_accounts ?? users.length}
        />
        <StatCard
          label="ACTIVE NOW"
          value={data?.active_now ?? 0}
        >
          {/* Avatar stack */}
          <div className={styles.avatarStack}>
            {['A', 'E', 'J'].map((l, i) => (
              <div key={i} className={styles.miniAvatar}>{l}</div>
            ))}
            <div className={styles.miniAvatarMore}>+3k</div>
          </div>
        </StatCard>
        <div className={styles.permCard}>
          <div className={styles.permTop}>
            <span className={styles.permLabel}>Directory synced</span>
            <span className={styles.permDesc}>Live from Odoo res.users</span>
          </div>
          <button className={styles.auditBtn} onClick={reload}>Refresh Directory</button>
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
        <span className={styles.showing}>
          Showing {users.length === 0 ? 0 : (page - 1) * PER_PAGE + 1}–{Math.min(page * PER_PAGE, users.length)} of {data?.total_accounts ?? users.length} users
        </span>
        <Pagination currentPage={page} totalPages={totalPages} onPageChange={setPage} />
      </div>

      {/* Create User Modal */}
      <CreateUserModal isOpen={modalOpen} onClose={() => setModalOpen(false)} />
    </AppShell>
  );
}
