import { useState } from 'react';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import StatusPill from '../../components/StatusPill/StatusPill';
import { registrarNav } from '../../config/navConfigs';
import { registrarAPI } from '../../api/apiGateway';
import useAsync from '../../hooks/useAsync';
import { exportCsv } from '../../utils/exportCsv';
import w from '../_shared/workflow.module.css';

/* Registrar — live per-course seat counts. */

function statusFor(pct) {
  if (pct >= 100) return { label: 'Full', variant: 'coral' };
  if (pct >= 95) return { label: 'Near Full', variant: 'yellow' };
  return { label: 'Open', variant: 'green' };
}
function barColor(pct) { return pct >= 95 ? 'var(--color-coral)' : pct >= 80 ? 'var(--color-yellow)' : 'var(--color-lime)'; }

export default function EnrollmentMonitorPage() {
  const { data, loading, error, reload } = useAsync(() => registrarAPI.getEnrollment(), []);
  const courses = data?.courses || [];
  const [q, setQ] = useState('');
  const rows = courses.filter((r) => (r.name || '').toLowerCase().includes(q.toLowerCase()) || (r.code || '').toLowerCase().includes(q.toLowerCase()));

  const handleExport = () => exportCsv('enrollment_report.csv', [
    { key: 'code', header: 'Code' }, { key: 'name', header: 'Course' },
    { key: 'enrolled', header: 'Enrolled' }, { key: 'capacity', header: 'Capacity' },
    { key: 'waitlisted', header: 'Waitlist' }, { key: 'fill_pct', header: 'Fill %' },
  ], rows);

  return (
    <AppShell navItems={registrarNav} logoVariant="stacked" sidebarLabel="REGISTRAR">
      <PageHeader title="Enrollment Monitor" subtitle="Live per-course seat counts" useBrandFont badge="LIVE" badgeVariant="green" />

      <div className={w.toolbar}>
        <input className={w.search} placeholder="Search course..." value={q} onChange={(e) => setQ(e.target.value)} />
      </div>

      <div className={w.card} style={{ padding: 0, overflow: 'hidden' }}>
        {loading ? <div className={w.empty}>Loading enrollment…</div>
        : error ? <div className={w.empty}><div className={w.emptyTitle}>Couldn't load</div><p>{error}</p><button className={`${w.btn} ${w.btnOutline} ${w.btnSm}`} onClick={reload}>Retry</button></div>
        : (
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
            <thead><tr style={{ textTransform: 'uppercase', fontSize: '0.66rem', color: 'var(--color-text-muted)', textAlign: 'left' }}>
              <th style={th}>Code</th><th style={th}>Course Name</th><th style={th}>Enrolled</th><th style={th}>Capacity</th><th style={th}>Waitlist</th><th style={th}>Fill %</th><th style={th}>Status</th>
            </tr></thead>
            <tbody>
              {rows.map((r) => {
                const pct = r.fill_pct ?? 0;
                const st = statusFor(pct);
                return (
                  <tr key={r.id} style={{ borderTop: '1px solid var(--color-border-light)', background: pct >= 95 ? 'rgba(232,97,58,0.06)' : undefined }}>
                    <td style={td}><strong>{r.code}</strong></td>
                    <td style={td}>{r.name}</td>
                    <td style={td}>{r.enrolled}</td>
                    <td style={td}>{r.capacity}</td>
                    <td style={td}>{r.waitlisted}</td>
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
        )}
      </div>

      <div style={{ display: 'flex', gap: 12, marginTop: 16 }}>
        <button className={`${w.btn} ${w.btnOutline}`} onClick={reload}>Run Seat Reconciliation</button>
        <button className={`${w.btn} ${w.btnOutline}`} onClick={handleExport} disabled={!rows.length}>Export Enrollment Report</button>
      </div>
    </AppShell>
  );
}

const th = { padding: '12px 16px', fontWeight: 700 };
const td = { padding: '12px 16px' };
