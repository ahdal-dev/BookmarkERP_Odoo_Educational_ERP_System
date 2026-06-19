import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import DataTable from '../../components/DataTable/DataTable';
import StatusPill from '../../components/StatusPill/StatusPill';
import { supportNav } from '../../config/navConfigs';
import { supportAPI } from '../../api/apiGateway';
import useAsync from '../../hooks/useAsync';
import w from '../_shared/workflow.module.css';

/* Support Technician — ticket queue (live). */

const PRIORITY_VARIANT = { high: 'coral', medium: 'green', low: 'yellow' };
const STATUS_VARIANT = { open: 'green', in_progress: 'yellow', closed: 'black' };
const STATUS_LABEL = { open: 'Open', in_progress: 'In Progress', closed: 'Closed' };
const FILTERS = ['All', 'open', 'in_progress', 'closed'];
const FILTER_LABEL = { All: 'All', open: 'Open', in_progress: 'In Progress', closed: 'Closed' };

export default function TicketListPage() {
  const navigate = useNavigate();
  const { data, loading, error, reload } = useAsync(() => supportAPI.listTickets(), []);
  const tickets = data?.tickets || [];
  const [filter, setFilter] = useState('All');
  const [creating, setCreating] = useState(false);

  const rows = tickets.filter((t) => filter === 'All' || t.state === filter);

  const create = async () => {
    const subject = window.prompt('New ticket subject:');
    if (!subject) return;
    setCreating(true);
    try {
      await supportAPI.createTicket({ subject, category: 'other', priority: 'medium', channel: 'ticket' });
      await reload();
    } finally {
      setCreating(false);
    }
  };

  const columns = [
    { key: 'ref', header: 'Ticket #', sortable: true, render: (v) => <strong>{v}</strong> },
    { key: 'requester', header: 'Requester', render: (v) => v?.name || '—' },
    { key: 'subject', header: 'Subject' },
    { key: 'priority', header: 'Priority', render: (v) => <StatusPill status={v} variant={PRIORITY_VARIANT[v]} /> },
    { key: 'state', header: 'Status', render: (v) => <StatusPill status={STATUS_LABEL[v] || v} variant={STATUS_VARIANT[v]} /> },
    { key: 'assigned_to', header: 'Assigned To', render: (v) => v?.name || 'Unassigned' },
    { key: 'action', header: 'Action', render: (_, r) => <span className={w.cardLink} onClick={() => navigate(`/support/chat/${r.id}`)}>Open →</span> },
  ];

  return (
    <AppShell navItems={supportNav} logoVariant="stacked" sidebarLabel="SUPPORT">
      <PageHeader
        title="Support Tickets" subtitle={`Showing ${rows.length} tickets`} useBrandFont
        actions={<button className={`${w.btn} ${w.btnPrimary}`} onClick={create} disabled={creating}>Create Manual Ticket</button>}
      />
      <div className={w.filterTabs} style={{ marginBottom: 16 }}>
        {FILTERS.map((f) => <button key={f} className={`${w.filterTab} ${filter === f ? w.filterTabActive : ''}`} onClick={() => setFilter(f)}>{FILTER_LABEL[f]}</button>)}
      </div>
      <div className={w.card} style={{ padding: 0 }}>
        {loading ? <div className={w.empty}>Loading tickets…</div>
          : error ? <div className={w.empty}><div className={w.emptyTitle}>Couldn't load tickets</div><p>{error}</p><button className={`${w.btn} ${w.btnOutline} ${w.btnSm}`} onClick={reload}>Retry</button></div>
          : <DataTable columns={columns} data={rows} />}
      </div>
    </AppShell>
  );
}
