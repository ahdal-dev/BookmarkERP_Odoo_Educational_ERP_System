import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import DataTable from '../../components/DataTable/DataTable';
import StatusPill from '../../components/StatusPill/StatusPill';
import { chairNav } from '../../config/navConfigs';
import { deptStudents } from '../../mocks/facultyMocks';
import w from '../_shared/workflow.module.css';

/* Department Chair — read-only access to all department student records. */

const STANDING_VARIANT = { 'Good Standing': 'green', Probation: 'yellow', 'Suspension Risk': 'coral' };

export default function DepartmentStudentRecordsPage() {
  const navigate = useNavigate();
  const [q, setQ] = useState('');

  const rows = deptStudents.filter((s) => s.name.toLowerCase().includes(q.toLowerCase()) || s.sid.toLowerCase().includes(q.toLowerCase()));

  const columns = [
    { key: 'sid', header: 'Student ID', sortable: true },
    { key: 'name', header: 'Name', sortable: true, render: (v) => <strong>{v}</strong> },
    { key: 'year', header: 'Year', sortable: true },
    { key: 'gpa', header: 'GPA', sortable: true },
    { key: 'credits', header: 'Credits', sortable: true },
    { key: 'standing', header: 'Standing', render: (v) => <StatusPill status={v} variant={STANDING_VARIANT[v]} /> },
    { key: 'petitions', header: 'Petitions', render: (v) => v > 0 ? <StatusPill status={String(v)} variant="coral" /> : <span style={{ color: 'var(--color-text-muted)' }}>0</span> },
    { key: 'action', header: 'Action', render: (_, r) => <span className={w.cardLink} onClick={() => navigate(`/faculty/advisees/${r.sid}`)}>View Profile →</span> },
  ];

  return (
    <AppShell navItems={chairNav} logoVariant="stacked" sidebarLabel="DEPARTMENT CHAIR">
      <PageHeader
        title="Department Student Records" subtitle={`Computer Science · ${deptStudents.length} enrolled students`} useBrandFont
        actions={<button className={`${w.btn} ${w.btnOutline} ${w.btnSm}`}>Export Report</button>}
      />

      <div className={w.toolbar}>
        <input className={w.search} placeholder="Search by name or ID..." value={q} onChange={(e) => setQ(e.target.value)} />
      </div>

      <div className={w.card} style={{ padding: 0 }}>
        <DataTable columns={columns} data={rows} />
      </div>

      <div className={w.readonlyBar}>🔒 Read-only departmental view. To modify a record, contact the Registrar.</div>
    </AppShell>
  );
}
