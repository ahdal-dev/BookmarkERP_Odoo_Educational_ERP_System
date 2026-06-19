import { useState } from 'react';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import DataTable from '../../components/DataTable/DataTable';
import StatusPill from '../../components/StatusPill/StatusPill';
import { adminNav } from '../../config/navConfigs';
import { auditAPI } from '../../api/apiGateway';
import useAsync from '../../hooks/useAsync';
import { exportCsv } from '../../utils/exportCsv';
import w from '../_shared/workflow.module.css';

/* System Administrator — read-only authentication & system-event log (live). */

const SEVERITY_VARIANT = { info: 'green', warning: 'yellow', critical: 'coral' };
const FILTERS = ['All', 'info', 'warning', 'critical'];
const FILTER_LABEL = { All: 'All', info: 'Info', warning: 'Warning', critical: 'Critical' };

export default function AuditLogPage() {
  const { data, loading, error, reload } = useAsync(() => auditAPI.getLog({ limit: 200 }), []);
  const events = data?.events || [];
  const [severity, setSeverity] = useState('All');
  const rows = events.filter((e) => severity === 'All' || e.severity === severity);

  const columns = [
    { key: 'date', header: 'Timestamp', sortable: true },
    { key: 'event_type', header: 'Event Type', render: (v) => <strong>{v}</strong> },
    { key: 'actor', header: 'Actor' },
    { key: 'ip', header: 'IP Address' },
    { key: 'detail', header: 'Detail' },
    { key: 'severity', header: 'Severity', render: (v) => <StatusPill status={v} variant={SEVERITY_VARIANT[v] || 'green'} /> },
  ];

  const handleExport = () => exportCsv('audit_log.csv', [
    { key: 'date', header: 'Timestamp' }, { key: 'event_type', header: 'Event' },
    { key: 'actor', header: 'Actor' }, { key: 'ip', header: 'IP' },
    { key: 'detail', header: 'Detail' }, { key: 'severity', header: 'Severity' },
  ], rows);

  return (
    <AppShell navItems={adminNav} logoVariant="stacked" sidebarLabel="ADMINISTRATION">
      <PageHeader
        title="System Audit Log" subtitle={`${data?.total ?? 0} recorded events`} useBrandFont
        actions={<button className={`${w.btn} ${w.btnOutline} ${w.btnSm}`} onClick={handleExport} disabled={!rows.length}>Export Log CSV</button>}
      />
      <div className={w.filterTabs} style={{ marginBottom: 16 }}>
        {FILTERS.map((t) => <button key={t} className={`${w.filterTab} ${severity === t ? w.filterTabActive : ''}`} onClick={() => setSeverity(t)}>{FILTER_LABEL[t]}</button>)}
      </div>
      <div className={w.card} style={{ padding: 0 }}>
        {loading ? <div className={w.empty}>Loading audit log…</div>
          : error ? <div className={w.empty}><div className={w.emptyTitle}>Couldn't load audit log</div><p>{error}</p><button className={`${w.btn} ${w.btnOutline} ${w.btnSm}`} onClick={reload}>Retry</button></div>
          : rows.length === 0 ? <div className={w.empty}><div className={w.emptyTitle}>No events</div><p>Audit events will appear here as users sign in and make changes.</p></div>
          : <DataTable columns={columns} data={rows} />}
      </div>
    </AppShell>
  );
}
