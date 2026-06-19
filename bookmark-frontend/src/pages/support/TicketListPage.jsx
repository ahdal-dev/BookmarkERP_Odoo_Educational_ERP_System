import { useState } from 'react';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import DataTable from '../../components/DataTable/DataTable';
import StatusPill from '../../components/StatusPill/StatusPill';
import { supportNav } from '../../config/navConfigs';
import w from '../_shared/workflow.module.css';

/* Support Technician — ticket queue. */

const TICKETS = [
  { num: 'T-5012', student: 'Aya Hassan', issue: 'Registration Error', date: 'Oct 16', priority: 'Critical', status: 'Open', agent: 'Unassigned' },
  { num: 'T-5009', student: 'Omar Khaled', issue: 'Login Issue', date: 'Oct 16', priority: 'High', status: 'Open', agent: 'You' },
  { num: 'T-4998', student: 'Lina Saad', issue: 'Portal Bug', date: 'Oct 15', priority: 'Normal', status: 'Escalated', agent: 'You' },
  { num: 'T-4980', student: 'Marcus Thorne', issue: 'Hold Inquiry', date: 'Oct 14', priority: 'Low', status: 'Resolved', agent: 'M. Said' },
  { num: 'T-4971', student: 'Elena Lunt', issue: 'Transcript Request', date: 'Oct 13', priority: 'Normal', status: 'Closed', agent: 'M. Said' },
];

const PRIORITY_VARIANT = { Critical: 'coral', High: 'coral', Normal: 'green', Low: 'yellow' };
const STATUS_VARIANT = { Open: 'green', Escalated: 'coral', Resolved: 'green', Closed: 'black' };
const FILTERS = ['All', 'Open', 'Escalated', 'Resolved', 'Closed'];

export default function TicketListPage() {
  const [filter, setFilter] = useState('All');
  const rows = TICKETS.filter((t) => filter === 'All' || t.status === filter);

  const columns = [
    { key: 'num', header: 'Ticket #', sortable: true, render: (v) => <strong>{v}</strong> },
    { key: 'student', header: 'Student', sortable: true },
    { key: 'issue', header: 'Issue Type' },
    { key: 'date', header: 'Submitted', sortable: true },
    { key: 'priority', header: 'Priority', render: (v) => <StatusPill status={v} variant={PRIORITY_VARIANT[v]} /> },
    { key: 'status', header: 'Status', render: (v) => <StatusPill status={v} variant={STATUS_VARIANT[v]} /> },
    { key: 'agent', header: 'Assigned To' },
    { key: 'action', header: 'Action', render: () => <span className={w.cardLink}>Open →</span> },
  ];

  return (
    <AppShell navItems={supportNav} logoVariant="stacked" sidebarLabel="SUPPORT">
      <PageHeader
        title="Support Tickets" subtitle={`Showing ${rows.length} tickets`} useBrandFont
        actions={<button className={`${w.btn} ${w.btnPrimary}`}>Create Manual Ticket</button>}
      />
      <div className={w.filterTabs} style={{ marginBottom: 16 }}>
        {FILTERS.map((f) => <button key={f} className={`${w.filterTab} ${filter === f ? w.filterTabActive : ''}`} onClick={() => setFilter(f)}>{f}</button>)}
      </div>
      <div className={w.card} style={{ padding: 0 }}>
        <DataTable columns={columns} data={rows} />
      </div>
    </AppShell>
  );
}
