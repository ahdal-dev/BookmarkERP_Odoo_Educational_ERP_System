import { useState } from 'react';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import StatusPill from '../../components/StatusPill/StatusPill';
import { registrarNav } from '../../config/navConfigs';
import w from '../_shared/workflow.module.css';

/* Registrar — real-time seat counts & compliance dashboard. */

const ROWS = [
  { code: 'CSAI 301', name: 'Advanced Algorithms', enrolled: 45, capacity: 50, waitlist: 3 },
  { code: 'CSAI 220', name: 'Data Structures', enrolled: 50, capacity: 50, waitlist: 6 },
  { code: 'MATH 200', name: 'Calculus II', enrolled: 24, capacity: 25, waitlist: 2 },
  { code: 'CSAI 410', name: 'Machine Learning', enrolled: 32, capacity: 40, waitlist: 0 },
  { code: 'ENG 105', name: 'Academic Writing', enrolled: 12, capacity: 28, waitlist: 0 },
];

function statusFor(pct) {
  if (pct >= 100) return { label: 'Full', variant: 'coral' };
  if (pct >= 95) return { label: 'Near Full', variant: 'yellow' };
  return { label: 'Open', variant: 'green' };
}
function barColor(pct) { return pct >= 95 ? 'var(--color-coral)' : pct >= 80 ? 'var(--color-yellow)' : 'var(--color-lime)'; }

export default function EnrollmentMonitorPage() {
  const [q, setQ] = useState('');
  const rows = ROWS.filter((r) => r.name.toLowerCase().includes(q.toLowerCase()) || r.code.toLowerCase().includes(q.toLowerCase()));

  return (
    <AppShell navItems={registrarNav} logoVariant="stacked" sidebarLabel="REGISTRAR">
      <PageHeader title="Enrollment Monitor" subtitle="Live · Last synced 3 seconds ago" useBrandFont badge="LIVE" badgeVariant="green" />

      <div className={w.toolbar}>
        <input className={w.search} placeholder="Search course or department..." value={q} onChange={(e) => setQ(e.target.value)} />
      </div>

      <div className={w.card} style={{ padding: 0, overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
          <thead><tr style={{ textTransform: 'uppercase', fontSize: '0.66rem', color: 'var(--color-text-muted)', textAlign: 'left' }}>
            <th style={th}>Code</th><th style={th}>Course Name</th><th style={th}>Enrolled</th><th style={th}>Capacity</th><th style={th}>Waitlist</th><th style={th}>Fill %</th><th style={th}>Status</th>
          </tr></thead>
          <tbody>
            {rows.map((r) => {
              const pct = Math.round((r.enrolled / r.capacity) * 100);
              const st = statusFor(pct);
              return (
                <tr key={r.code} style={{ borderTop: '1px solid var(--color-border-light)', background: pct >= 95 ? 'rgba(232,97,58,0.06)' : undefined }}>
                  <td style={td}><strong>{r.code}</strong></td>
                  <td style={td}>{r.name}</td>
                  <td style={td}>{r.enrolled}</td>
                  <td style={td}>{r.capacity}</td>
                  <td style={td}>{r.waitlist}</td>
                  <td style={td}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <div className={w.bar} style={{ width: 80 }}><div className={w.barFill} style={{ width: `${Math.min(pct, 100)}%`, background: barColor(pct) }} /></div>
                      <span style={{ fontSize: '0.78rem' }}>{pct}%</span>
                    </div>
                  </td>
                  <td style={td}><StatusPill status={st.label} variant={st.variant} /></td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div style={{ display: 'flex', gap: 12, marginTop: 16 }}>
        <button className={`${w.btn} ${w.btnOutline}`}>Run Seat Reconciliation</button>
        <button className={`${w.btn} ${w.btnOutline}`}>Export Enrollment Report</button>
      </div>
    </AppShell>
  );
}

const th = { padding: '12px 16px', fontWeight: 700 };
const td = { padding: '12px 16px' };
