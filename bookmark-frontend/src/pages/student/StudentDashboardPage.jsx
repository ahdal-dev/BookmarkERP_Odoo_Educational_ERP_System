import { useNavigate } from 'react-router-dom';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import StatCard from '../../components/StatCard/StatCard';
import StatusPill from '../../components/StatusPill/StatusPill';
import { studentNav } from '../../config/navConfigs';
import { useAuth } from '../../context/AuthContext';
import { studentAPI } from '../../api/apiGateway';
import useAsync from '../../hooks/useAsync';
import w from '../_shared/workflow.module.css';

/* Student landing view — live GPA/credits/petition summary + enrolled courses. */

export default function StudentDashboardPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const name = user?.name || 'Student';

  const { data, loading, error, reload } = useAsync(() => studentAPI.getDashboard(), []);
  const schedule = data?.schedule || [];

  const sidebarFooter = <a href="/help" className={w.cardLink}>Help Center</a>;

  return (
    <AppShell navItems={studentNav} logoVariant="stacked" sidebarLabel="STUDENT PORTAL" sidebarFooter={sidebarFooter}>
      <PageHeader title={`Good morning, ${name} 👋`} subtitle="Fall 2026 · Your academic snapshot" useBrandFont />

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

      {!loading && !error && data && (
        <>
          <div className={`${w.statRow} ${w.cols3}`}>
            <StatCard value={data.gpa != null ? data.gpa : '—'} label="Current GPA" accentColor="var(--color-lime)" />
            <StatCard value={data.registered_credits ?? 0} label="Registered Credits" accentColor="var(--color-yellow)" />
            <StatCard value={data.active_petitions ?? 0} label="Active Petitions" accentColor="var(--color-coral)" />
          </div>

          <div className={w.split}>
            {/* Enrolled courses */}
            <div className={`${w.card} ${w.cardAccent}`}>
              <h3 className={w.cardTitle}>Enrolled Courses</h3>
              <p className={w.cardSub}>{data.registered_courses ?? 0} course(s) this term</p>
              {schedule.length === 0 ? (
                <div style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>You aren't enrolled in any courses yet.</div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {schedule.map((c) => (
                    <div key={c.code} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 12px', background: 'var(--color-bg-warm)', borderRadius: 8 }}>
                      <div>
                        <strong style={{ fontSize: '0.88rem' }}>{c.code}</strong>
                        <span style={{ display: 'block', fontSize: '0.78rem', color: 'var(--color-text-muted)' }}>{c.name}</span>
                      </div>
                      <div style={{ textAlign: 'right', fontSize: '0.76rem', color: 'var(--color-text-muted)' }}>
                        <div>{c.schedule || 'TBA'}</div>
                        <div>{c.instructor || 'TBA'}</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Petitions summary */}
            <div className={`${w.card} ${w.cardAccent}`}>
              <h3 className={w.cardTitle}>Petitions</h3>
              <div className={w.metaRow} style={{ marginTop: 8 }}>
                <span><strong>{data.active_petitions ?? 0}</strong> active</span>
                <StatusPill status={data.active_petitions ? 'Pending' : 'None'} variant={data.active_petitions ? 'yellow' : 'green'} />
              </div>
              <p className={w.cardSub} style={{ marginTop: 12 }}>
                Track the status of your submitted petitions or start a new request.
              </p>
              <button className={`${w.btn} ${w.btnOutline} ${w.btnFull}`} style={{ marginTop: 8 }}
                      onClick={() => navigate('/student/petitions')}>
                View all petitions →
              </button>
            </div>
          </div>

          {/* Quick actions */}
          <div style={{ display: 'flex', gap: 12, marginTop: 24, flexWrap: 'wrap' }}>
            <button className={`${w.btn} ${w.btnPrimary}`} onClick={() => navigate('/registration')}>Browse Courses</button>
            <button className={`${w.btn} ${w.btnPrimary}`} onClick={() => navigate('/petitions/new')}>Submit Petition</button>
            <button className={`${w.btn} ${w.btnPrimary}`} onClick={() => navigate('/student/grades')}>View Grades</button>
          </div>
        </>
      )}
    </AppShell>
  );
}
