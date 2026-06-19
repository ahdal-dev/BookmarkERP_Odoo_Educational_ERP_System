import { useNavigate } from 'react-router-dom';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import StatCard from '../../components/StatCard/StatCard';
import StatusPill from '../../components/StatusPill/StatusPill';
import { facultyNav } from '../../config/navConfigs';
import { facultyAPI } from '../../api/apiGateway';
import useAsync from '../../hooks/useAsync';
import w from '../_shared/workflow.module.css';

/* Instructor landing — assigned courses + pending petition queue (live). */

const URGENCY_VARIANT = { High: 'coral', Medium: 'yellow', Low: 'green' };

function urgencyOf(daysPending) {
  if ((daysPending ?? 0) > 7) return 'High';
  if ((daysPending ?? 0) >= 3) return 'Medium';
  return 'Low';
}

export default function FacultyDashboardPage() {
  const navigate = useNavigate();

  const { data, loading, error, reload } = useAsync(async () => {
    const [dashboard, queue] = await Promise.all([
      facultyAPI.getDashboard(),
      facultyAPI.getPetitionQueue(),
    ]);
    return { dashboard, petitions: queue?.petitions || [] };
  }, []);

  const dash = data?.dashboard;
  const courses = dash?.courses || [];
  const petitions = data?.petitions || [];

  return (
    <AppShell navItems={facultyNav} logoVariant="stacked" sidebarLabel="FACULTY">
      <PageHeader title="Faculty Dashboard" subtitle="Fall 2026 · Your teaching overview" useBrandFont />

      {loading && <div className={w.card}><div className={w.empty}>Loading your dashboard…</div></div>}

      {error && !loading && (
        <div className={w.card}>
          <div className={w.empty}>
            <div className={w.emptyTitle}>Couldn't load your dashboard</div>
            <p>{error}</p>
            <button className={`${w.btn} ${w.btnOutline} ${w.btnSm}`} onClick={reload}>Retry</button>
          </div>
        </div>
      )}

      {!loading && !error && dash && (
        <>
          <div className={`${w.statRow} ${w.cols3}`}>
            <StatCard value={dash.assigned_courses ?? 0} label="Assigned Courses" accentColor="var(--color-lime)" />
            <StatCard value={dash.total_students ?? 0} label="Total Enrolled Students" accentColor="var(--color-yellow)" />
            <StatCard value={dash.pending_petitions ?? 0} label="Pending Petitions" accentColor="var(--color-coral)" />
          </div>

          <div className={w.split}>
            {/* Assigned courses */}
            <div className={`${w.card} ${w.cardAccent}`}>
              <h3 className={w.cardTitle}>Assigned Courses</h3>
              <p className={w.cardSub}>Fall 2026</p>
              {courses.length === 0 ? (
                <div style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>No courses assigned to you.</div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                  {courses.map((c) => {
                    const pct = c.capacity ? Math.round((c.enrolled / c.capacity) * 100) : 0;
                    return (
                      <div key={c.id} style={{ border: '1px solid var(--color-border-light)', borderRadius: 12, padding: 14 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <div>
                            <span style={{ color: 'var(--color-lime-dark)', fontWeight: 800 }}>{c.code}</span>
                            <span style={{ marginLeft: 8, fontWeight: 600 }}>{c.name}</span>
                          </div>
                          <span className={w.cardLink} onClick={() => navigate(`/faculty/courses/${c.id}`)}>View Roster →</span>
                        </div>
                        <div style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)', margin: '6px 0' }}>{c.schedule || 'Schedule TBA'}</div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                          <div className={w.bar}><div className={w.barFill} style={{ width: `${pct}%`, background: pct >= 95 ? 'var(--color-coral)' : 'var(--color-lime)' }} /></div>
                          <span style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)' }}>{c.enrolled}/{c.capacity}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Pending petitions */}
            <div className={`${w.card} ${w.cardAccent}`}>
              <h3 className={w.cardTitle}>Pending Petition Queue</h3>
              <p className={w.cardSub}>{petitions.length} awaiting your review</p>
              {petitions.length === 0 ? (
                <div style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>Your petition queue is clear.</div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {petitions.map((p) => {
                    const urgency = urgencyOf(p.days_pending);
                    return (
                      <div key={p.id} style={{ display: 'flex', alignItems: 'center', gap: 12, border: '1px solid var(--color-border-light)', borderRadius: 10, padding: 12 }}>
                        <div style={{ flex: 1 }}>
                          <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>{p.student_id?.name || 'Student'}</div>
                          <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginTop: 4 }}>
                            <StatusPill status={p.petition_type_id?.name || p.subject || 'Petition'} variant="yellow" />
                            <span style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)' }}>{p.submitted_date || ''}</span>
                          </div>
                        </div>
                        <StatusPill status={urgency} variant={URGENCY_VARIANT[urgency]} />
                        <button className={`${w.btn} ${w.btnPrimary} ${w.btnSm}`} onClick={() => navigate(`/faculty/petitions/${p.id}`)}>Review →</button>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </AppShell>
  );
}
