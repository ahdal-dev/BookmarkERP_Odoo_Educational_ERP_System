import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import DataTable from '../../components/DataTable/DataTable';
import StatusPill from '../../components/StatusPill/StatusPill';
import { chairNav } from '../../config/navConfigs';
import { advisingAPI } from '../../api/apiGateway';
import useAsync from '../../hooks/useAsync';
import { exportCsv } from '../../utils/exportCsv';
import w from '../_shared/workflow.module.css';

/* Department Chair — read-only access to all department student records (live). */

const STANDING_VARIANT = { good: 'green', deans_list: 'green', probation: 'coral', new: 'yellow' };
const STANDING_LABEL = { good: 'Good Standing', deans_list: "Dean's List", probation: 'Probation', new: 'New' };
const CLASS_LABEL = { freshman: 'Freshman', sophomore: 'Sophomore', junior: 'Junior', senior: 'Senior' };

export default function DepartmentStudentRecordsPage() {
  const navigate = useNavigate();
  const { data, loading, error, reload } = useAsync(() => advisingAPI.getDepartmentStudents(), []);
  const students = data?.students || [];
  const [q, setQ] = useState('');

  const rows = students.filter((s) => (s.name || '').toLowerCase().includes(q.toLowerCase()) || (s.email || '').toLowerCase().includes(q.toLowerCase()));

  const columns = [
    { key: 'email', header: 'Email', sortable: true },
    { key: 'name', header: 'Name', sortable: true, render: (v) => <strong>{v}</strong> },
    { key: 'class_year', header: 'Year', sortable: true, render: (v) => CLASS_LABEL[v] || v },
    { key: 'gpa', header: 'GPA', sortable: true, render: (v) => (v ?? 0).toFixed(2) },
    { key: 'earned_credits', header: 'Credits', sortable: true },
    { key: 'standing', header: 'Standing', render: (v) => <StatusPill status={STANDING_LABEL[v] || v} variant={STANDING_VARIANT[v] || 'yellow'} /> },
    { key: 'active_petitions', header: 'Petitions', render: (v) => v > 0 ? <StatusPill status={String(v)} variant="coral" /> : <span style={{ color: 'var(--color-text-muted)' }}>0</span> },
    { key: 'action', header: 'Action', render: (_, r) => <span className={w.cardLink} onClick={() => navigate(`/faculty/advisees/${r.id}`)}>View Profile →</span> },
  ];

  const handleExport = () => exportCsv('department_students.csv', [
    { key: 'name', header: 'Name' },
    { key: 'email', header: 'Email' },
    { key: 'class_year', header: 'Year', value: (r) => CLASS_LABEL[r.class_year] || r.class_year },
    { key: 'gpa', header: 'GPA', value: (r) => (r.gpa ?? 0).toFixed(2) },
    { key: 'earned_credits', header: 'Credits' },
    { key: 'standing', header: 'Standing', value: (r) => STANDING_LABEL[r.standing] || r.standing },
    { key: 'active_petitions', header: 'Active Petitions' },
  ], rows);

  return (
    <AppShell navItems={chairNav} logoVariant="stacked" sidebarLabel="DEPARTMENT CHAIR">
      <PageHeader
        title="Department Student Records" subtitle={`${(data?.departments || []).join(', ') || 'Department'} · ${students.length} enrolled students`} useBrandFont
        actions={<button className={`${w.btn} ${w.btnOutline} ${w.btnSm}`} onClick={handleExport} disabled={!rows.length}>Export Report</button>}
      />

      <div className={w.toolbar}>
        <input className={w.search} placeholder="Search by name or email..." value={q} onChange={(e) => setQ(e.target.value)} />
      </div>

      <div className={w.card} style={{ padding: 0 }}>
        {loading ? <div className={w.empty}>Loading students…</div>
          : error ? <div className={w.empty}><div className={w.emptyTitle}>Couldn't load records</div><p>{error}</p><button className={`${w.btn} ${w.btnOutline} ${w.btnSm}`} onClick={reload}>Retry</button></div>
          : <DataTable columns={columns} data={rows} />}
      </div>

      <div className={w.readonlyBar}>🔒 Read-only departmental view. To modify a record, contact the Registrar.</div>
    </AppShell>
  );
}
