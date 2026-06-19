import { useState } from 'react';
import AppShell from '../../../components/AppShell/AppShell';
import TopBar from '../../../components/TopBar/TopBar';
import PageHeader from '../../../components/PageHeader/PageHeader';
import StatusPill from '../../../components/StatusPill/StatusPill';
import { adminDashboardNav } from '../../../config/navConfigs';
import { mockRoles, mockPermissionMatrix, openTicketCount } from '../../../mocks/adminMocks';
import styles from './RolesPage.module.css';

// Roles & permissions — manage role definitions and the module access matrix

const navWithActive = adminDashboardNav.map((n) =>
  n.path === '/admin/roles' ? { ...n, active: true } : n
);

const ROLE_PILL = {
  super_admin: 'coral', admin: 'green', registrar: 'black',
  instructor: 'green', student: 'yellow', admission_officer: 'black',
};

const ACCESS_COLOR = {
  RW: styles.cellRW, R: styles.cellR, 'RW*': styles.cellRW,
  'R*': styles.cellR, 'Sub': styles.cellSub, '—': styles.cellNone,
};

export default function RolesPage() {
  const [activeTab, setActiveTab] = useState('roles');
  const [editingRole, setEditingRole] = useState(null);
  const [roles, setRoles] = useState(mockRoles);
  const [showCreateRole, setShowCreateRole] = useState(false);
  const [newRole, setNewRole] = useState({ name: '', description: '', accessLevel: 'Limited' });

  const deleteRole = (id) => setRoles((prev) => prev.filter((r) => r.id !== id));
  const createRole = () => {
    if (!newRole.name.trim()) return;
    setRoles((prev) => [
      ...prev,
      { id: Date.now(), name: newRole.name, slug: newRole.name.toLowerCase().replace(/\s+/g, '_'), userCount: 0, accessLevel: newRole.accessLevel, description: newRole.description },
    ]);
    setNewRole({ name: '', description: '', accessLevel: 'Limited' });
    setShowCreateRole(false);
  };

  return (
    <AppShell
      navItems={navWithActive}
      logoVariant="icon-text"
      sidebarLabel="ADMIN PANEL"
      topBar={<TopBar searchPlaceholder="Search roles, permissions..." notificationCount={openTicketCount} />}
    >
      <div className={styles.breadcrumb}>ADMIN CONTROL / ROLES & PERMISSIONS</div>

      <PageHeader
        title="Roles & Permission Management"
        subtitle="Control institutional access levels and permission inheritance."
        actions={
          <button className={styles.createBtn} onClick={() => setShowCreateRole(true)}>+ Create Role</button>
        }
      />

      {/* Tabs */}
      <div className={styles.tabs}>
        <button
          className={`${styles.tab} ${activeTab === 'roles' ? styles.tabActive : ''}`}
          onClick={() => setActiveTab('roles')}
        >
          Roles
        </button>
        <button
          className={`${styles.tab} ${activeTab === 'matrix' ? styles.tabActive : ''}`}
          onClick={() => setActiveTab('matrix')}
        >
          Permission Matrix
        </button>
      </div>

      {activeTab === 'roles' && (
        <>
          {/* Role Cards */}
          <div className={styles.roleGrid}>
            {roles.map((role) => (
              <div key={role.id} className={styles.roleCard}>
                <div className={styles.roleCardTop}>
                  <StatusPill status={role.name} variant={ROLE_PILL[role.slug] || 'black'} />
                  <span className={styles.userCount}>{role.userCount.toLocaleString()} users</span>
                </div>
                <p className={styles.roleDesc}>{role.description}</p>
                <div className={styles.roleCardFooter}>
                  <span className={styles.accessLevel}>{role.accessLevel}</span>
                  <div className={styles.roleActions}>
                    <button className={styles.editBtn} onClick={() => setEditingRole(role)}>Edit</button>
                    {role.slug !== 'super_admin' && (
                      <button className={styles.deleteBtn} onClick={() => deleteRole(role.id)}>Delete</button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Edit Role Modal */}
          {editingRole && (
            <div className={styles.modalOverlay} onClick={() => setEditingRole(null)}>
              <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
                <div className={styles.modalHeader}>
                  <h2 className={styles.modalTitle}>Edit Role — {editingRole.name}</h2>
                  <button className={styles.modalClose} onClick={() => setEditingRole(null)}>✕</button>
                </div>
                <div className={styles.modalBody}>
                  <label className={styles.fieldLabel}>Role Name</label>
                  <input className={styles.fieldInput} defaultValue={editingRole.name} />
                  <label className={styles.fieldLabel}>Description</label>
                  <textarea className={styles.fieldTextarea} defaultValue={editingRole.description} rows={3} />
                  <label className={styles.fieldLabel}>Access Level</label>
                  <select className={styles.fieldSelect} defaultValue={editingRole.accessLevel}>
                    <option>Full Access</option>
                    <option>High Access</option>
                    <option>Mid Access</option>
                    <option>Scoped</option>
                    <option>Limited</option>
                  </select>
                </div>
                <div className={styles.modalFooter}>
                  <button className={styles.cancelBtn} onClick={() => setEditingRole(null)}>Discard</button>
                  <button className={styles.saveBtn} onClick={() => setEditingRole(null)}>Save Changes</button>
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {activeTab === 'matrix' && (
        <div className={styles.matrixCard}>
          <div className={styles.matrixScroll}>
            <table className={styles.matrix}>
              <thead>
                <tr>
                  <th className={styles.matrixModuleCol}>Module</th>
                  <th className={styles.matrixCell}>Super Admin</th>
                  <th className={styles.matrixCell}>Admin</th>
                  <th className={styles.matrixCell}>Registrar</th>
                  <th className={styles.matrixCell}>Instructor</th>
                  <th className={styles.matrixCell}>Student</th>
                </tr>
              </thead>
              <tbody>
                {mockPermissionMatrix.map((row, i) => (
                  <tr key={i} className={styles.matrixRow}>
                    <td className={styles.matrixModuleName}>{row.module}</td>
                    {['superAdmin', 'admin', 'registrar', 'instructor', 'student'].map((key) => (
                      <td key={key} className={`${styles.matrixCell} ${ACCESS_COLOR[row[key]] || styles.cellNone}`}>
                        {row[key]}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className={styles.matrixLegend}>
            <span className={`${styles.legendItem} ${styles.cellRW}`}>RW = Read / Write</span>
            <span className={`${styles.legendItem} ${styles.cellR}`}>R = Read Only</span>
            <span className={`${styles.legendItem} ${styles.cellSub}`}>Sub = Submit Only</span>
            <span className={`${styles.legendItem} ${styles.cellNone}`}>— = No Access</span>
            <span className={styles.legendNote}>* = Scoped to own records</span>
          </div>
        </div>
      )}
      {showCreateRole && (
        <div className={styles.modalOverlay} onClick={() => setShowCreateRole(false)}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>Create New Role</h2>
              <button className={styles.modalClose} onClick={() => setShowCreateRole(false)}>✕</button>
            </div>
            <div className={styles.modalBody}>
              <label className={styles.fieldLabel}>Role Name</label>
              <input
                className={styles.fieldInput}
                placeholder="e.g. Department Head"
                value={newRole.name}
                onChange={(e) => setNewRole((p) => ({ ...p, name: e.target.value }))}
              />
              <label className={styles.fieldLabel}>Description</label>
              <textarea
                className={styles.fieldTextarea}
                rows={2}
                placeholder="Describe the responsibilities of this role..."
                value={newRole.description}
                onChange={(e) => setNewRole((p) => ({ ...p, description: e.target.value }))}
              />
              <label className={styles.fieldLabel}>Access Level</label>
              <select
                className={styles.fieldSelect}
                value={newRole.accessLevel}
                onChange={(e) => setNewRole((p) => ({ ...p, accessLevel: e.target.value }))}
              >
                <option>Full Access</option>
                <option>High Access</option>
                <option>Mid Access</option>
                <option>Scoped</option>
                <option>Limited</option>
              </select>
            </div>
            <div className={styles.modalFooter}>
              <button className={styles.cancelBtn} onClick={() => setShowCreateRole(false)}>Discard</button>
              <button className={styles.saveBtn} onClick={createRole}>Create Role</button>
            </div>
          </div>
        </div>
      )}
    </AppShell>
  );
}
