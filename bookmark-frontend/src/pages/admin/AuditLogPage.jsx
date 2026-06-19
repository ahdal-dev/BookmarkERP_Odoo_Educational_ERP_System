import { useState } from 'react';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import DataTable from '../../components/DataTable/DataTable';
import StatusPill from '../../components/StatusPill/StatusPill';
import { adminNav } from '../../config/navConfigs';
import w from '../_shared/workflow.module.css';

/* System Administrator — read-only authentication & system-event log. */

const EVENTS = [
  { ts: '2026-10-16 14:32', user: 'admin@test.com', role: 'Admin', type: 'Config Change', desc: 'Updated registration ruleset', ip: '10.0.0.4', outcome: 'Success' },
  { ts: '2026-10-16 14:10', user: 'officer@test.com', role: 'Registrar', type: 'Login', desc: 'Successful login', ip: '10.0.0.9', outcome: 'Success' },
  { ts: '2026-10-16 13:58', user: 'unknown', role: '—', type: 'Failed Auth', desc: '3 failed attempts for student@test.com', ip: '102.44.9.1', outcome: 'Failed' },
  { ts: '2026-10-16 13:40', user: 'admin@test.com', role: 'Admin', type: 'Role Change', desc: 'Granted Instructor role to f.said@zc.edu', ip: '10.0.0.4', outcome: 'Success' },
  { ts: '2026-10-16 12:05', user: 'officer@test.com', role: 'Registrar', type: 'Data Export', desc: 'Exported enrollment report', ip: '10.0.0.9', outcome: 'Warning' },
];

const TYPE_VARIANT = { Login: 'green', 'Config Change': 'yellow', 'Failed Auth': 'coral', 'Role Change': 'coral', 'Data Export': 'yellow' };
const OUTCOME_VARIANT = { Success: 'green', Failed: 'coral', Warning: 'yellow' };
const TYPES = ['All', 'Login', 'Role Change', 'Config Change', 'Data Export', 'Failed Auth'];

export default function AuditLogPage() {
  const [type, setType] = useState('All');
  const rows = EVENTS.filter((e) => type === 'All' || e.type === type);

  const columns = [
    { key: 'ts', header: 'Timestamp', sortable: true },
    { key: 'user', header: 'User' },
    { key: 'role', header: 'Role' },
    { key: 'type', header: 'Event Type', render: (v) => <StatusPill status={v} variant={TYPE_VARIANT[v]} /> },
    { key: 'desc', header: 'Description' },
    { key: 'ip', header: 'IP Address' },
    { key: 'outcome', header: 'Outcome', render: (v) => <StatusPill status={v} variant={OUTCOME_VARIANT[v]} /> },
  ];

  return (
    <AppShell navItems={adminNav} logoVariant="stacked" sidebarLabel="ADMINISTRATION">
      <PageHeader
        title="System Audit Log" subtitle="Read-only · All authentication and system events" useBrandFont
        actions={<button className={`${w.btn} ${w.btnOutline} ${w.btnSm}`}>Export Log CSV</button>}
      />
      <div className={w.filterTabs} style={{ marginBottom: 16 }}>
        {TYPES.map((t) => <button key={t} className={`${w.filterTab} ${type === t ? w.filterTabActive : ''}`} onClick={() => setType(t)}>{t}</button>)}
      </div>
      <div className={w.card} style={{ padding: 0 }}>
        <DataTable columns={columns} data={rows} />
      </div>
    </AppShell>
  );
}
