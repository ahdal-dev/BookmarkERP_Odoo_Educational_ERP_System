import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import StatCard from '../../components/StatCard/StatCard';
import StatusPill from '../../components/StatusPill/StatusPill';
import CircularGauge from '../../components/CircularGauge/CircularGauge';
import { registrarNav } from '../../config/navConfigs';
import { registrarAPI } from '../../api/apiGateway';
import useAsync from '../../hooks/useAsync';
import w from '../_shared/workflow.module.css';

/* Registrar landing — live registration status + enrollment monitor.
   All figures are fetched from the gateway (education.registration /
   education.course); no mock data. */

function relativeTime(value) {
  if (!value) return '';
  const diff = Date.now() - new Date(value.replace(' ', 'T')).getTime();
  if (Number.isNaN(diff)) return '';
  const min = Math.max(0, Math.round(diff / 60000));
  if (min < 60) return `${min}m ago`;
  const hr = Math.round(min / 60);
  if (hr < 24) return `${hr}h ago`;
  return `${Math.round(hr / 24)}d ago`;
}

export default function RegistrarDashboardPage() {
  const { data, loading, error, reload } = useAsync(() => registrarAPI.getDashboard(), []);

  const stats = data?.stats;
  const windows = data?.windows || [];
  const events = data?.recent_activity || [];

  return (
    <AppShell navItems={registrarNav} logoVariant="stacked" sidebarLabel="REGISTRAR">
      <PageHeader title="Registrar Dashboard" subtitle="Live Registration · Enrollment Monitor" useBrandFont badge="LIVE" badgeVariant="green" />

      {loading && <div className={w.card}><div className={w.empty}>Loading live registration data…</div></div>}

      {error && !loading && (
        <div className={w.card}>
          <div className={w.empty}>
            <div className={w.emptyTitle}>Couldn't load dashboard data</div>
            <p>{error}</p>
            <button className={`${w.btn} ${w.btnOutline} ${w.btnSm}`} onClick={reload}>Retry</button>
          </div>
        </div>
      )}

      {!loading && !error && data && (
        <>
          <div className={`${w.statRow} ${w.cols4}`}>
            <StatCard value={(stats?.total_enrolled ?? 0).toLocaleString()} label="Total Enrolled" accentColor="var(--color-lime)" />
            <StatCard value={(stats?.open_seats ?? 0).toLocaleString()} label="Open Seats Remaining" accentColor="var(--color-yellow)" />
            <StatCard value={(stats?.open_courses ?? 0).toLocaleString()} label="Open Courses" accentColor="var(--color-lime)" />
            <StatCard value={(stats?.waitlisted ?? 0).toLocaleString()} label="Waitlisted Students" accentColor="var(--color-coral)" />
          </div>

          <div className={w.split}>
            <div>
              <CircularGauge value={data.capacity_utilization ?? 0} caption="CAPACITY UTILIZATION" label="Seats filled across all courses" />
              <div className={w.card} style={{ marginTop: 16, padding: 0 }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.84rem' }}>
                  <thead><tr style={{ textTransform: 'uppercase', fontSize: '0.66rem', color: 'var(--color-text-muted)', textAlign: 'left' }}>
                    <th style={{ padding: 12 }}>Course</th><th style={{ padding: 12 }}>Registration Window</th><th style={{ padding: 12 }}>Status</th><th style={{ padding: 12 }}>Open Seats</th>
                  </tr></thead>
                  <tbody>
                    {windows.length === 0 ? (
                      <tr><td colSpan={4} style={{ padding: 16, color: 'var(--color-text-muted)' }}>No open registration windows.</td></tr>
                    ) : windows.map((t) => (
                      <tr key={t.name} style={{ borderTop: '1px solid var(--color-border-light)' }}>
                        <td style={{ padding: 12, fontWeight: 600 }}>{t.name}</td>
                        <td style={{ padding: 12 }}>{t.window}</td>
                        <td style={{ padding: 12 }}><StatusPill status={t.status} variant={t.status === 'Open' ? 'green' : 'yellow'} /></td>
                        <td style={{ padding: 12 }}>{(t.available_seats ?? 0).toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className={`${w.card} ${w.cardAccent}`}>
              <h3 className={w.cardTitle}><span className={w.pulse} />Live Event Log</h3>
              <p className={w.cardSub}>Most recent enrollment activity</p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {events.length === 0 ? (
                  <div style={{ fontSize: '0.82rem', color: 'var(--color-text-muted)' }}>No recent activity.</div>
                ) : events.map((e, i) => (
                  <div key={i} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', padding: '8px 12px', background: 'var(--color-bg-warm)', borderRadius: 8 }}>
                    <span>{e.text}</span><span style={{ color: 'var(--color-text-muted)', fontSize: '0.72rem' }}>{relativeTime(e.at)}</span>
                  </div>
                ))}
              </div>
              <button className={`${w.btn} ${w.btnOutline} ${w.btnSm}`} style={{ marginTop: 16 }} onClick={reload}>Refresh</button>
            </div>
          </div>
        </>
      )}
    </AppShell>
  );
}
