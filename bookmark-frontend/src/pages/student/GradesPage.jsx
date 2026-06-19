import { useState, useEffect } from 'react';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import StatCard from '../../components/StatCard/StatCard';
import StatusPill from '../../components/StatusPill/StatusPill';
import { studentNav } from '../../config/navConfigs';
import { studentAPI } from '../../api/apiGateway';
import useAsync from '../../hooks/useAsync';
import w from '../_shared/workflow.module.css';

/* Read-only unofficial transcript with semester accordion (live data). */

const GRADE_COLOR = {
  A: 'green', 'A-': 'green', 'B+': 'yellow', B: 'yellow', 'B-': 'yellow',
  'C+': 'yellow', C: 'coral', 'C-': 'coral', 'D+': 'coral', D: 'coral', F: 'coral', W: 'black',
};

export default function GradesPage() {
  const { data, loading, error, reload } = useAsync(() => studentAPI.getGrades(), []);
  const terms = data?.terms || [];
  const [open, setOpen] = useState({});

  // Open the most recent term by default once data arrives.
  useEffect(() => {
    if (terms.length) setOpen((prev) => (Object.keys(prev).length ? prev : { [terms[0].term]: true }));
  }, [terms]);

  return (
    <AppShell navItems={studentNav} logoVariant="stacked" sidebarLabel="STUDENT PORTAL">
      <PageHeader title="Academic Transcript" subtitle="Unofficial · For an official copy contact the Registrar" useBrandFont />

      {loading && <div className={w.card}><div className={w.empty}>Loading your transcript…</div></div>}

      {error && !loading && (
        <div className={w.card}>
          <div className={w.empty}>
            <div className={w.emptyTitle}>Couldn't load your grades</div>
            <p>{error}</p>
            <button className={`${w.btn} ${w.btnOutline} ${w.btnSm}`} onClick={reload}>Retry</button>
          </div>
        </div>
      )}

      {!loading && !error && data && (
        <>
          <div className={`${w.statRow} ${w.cols3}`}>
            <StatCard value={`${(data.cumulative_gpa ?? 0).toFixed(2)} / 4.00`} label="Cumulative GPA" accentColor="var(--color-lime)" />
            <StatCard value={data.earned_credits ?? 0} label="Total Credits Earned" accentColor="var(--color-yellow)" />
            <StatCard value={data.academic_standing || '—'} label="Academic Standing" accentColor="var(--color-lime)" />
          </div>

          {terms.length === 0 ? (
            <div className={w.card}><div className={w.empty}>
              <div className={w.emptyTitle}>No graded courses yet</div>
              <p>Your grades will appear here once they are posted.</p>
            </div></div>
          ) : terms.map((s) => (
            <div key={s.term} className={w.card} style={{ marginBottom: 14, padding: 0, overflow: 'hidden' }}>
              <button
                onClick={() => setOpen((p) => ({ ...p, [s.term]: !p[s.term] }))}
                style={{
                  width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  padding: '16px 24px', background: 'none', border: 'none', cursor: 'pointer', fontFamily: 'inherit',
                }}
              >
                <span style={{ fontWeight: 800, fontSize: '1rem' }}>{s.term}</span>
                <span style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem' }}>
                  {s.credits} credits · GPA: {(s.gpa ?? 0).toFixed(2)} <span style={{ marginLeft: 10 }}>{open[s.term] ? '▾' : '▸'}</span>
                </span>
              </button>
              {open[s.term] && (
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.86rem' }}>
                  <thead>
                    <tr style={{ textTransform: 'uppercase', fontSize: '0.68rem', letterSpacing: '0.05em', color: 'var(--color-text-muted)' }}>
                      <th style={th}>Course Code</th><th style={th}>Course Name</th><th style={th}>Credits</th><th style={th}>Grade</th><th style={th}>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {s.courses.map((c) => (
                      <tr key={c.code} style={{ borderTop: '1px solid var(--color-border-light)' }}>
                        <td style={td}><strong>{c.code}</strong></td>
                        <td style={td}>{c.name}</td>
                        <td style={td}>{c.credits}</td>
                        <td style={td}><StatusPill status={c.grade} variant={GRADE_COLOR[c.grade] || 'black'} /></td>
                        <td style={td}>{c.status}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          ))}

          <button className={`${w.btn} ${w.btnOutline}`} style={{ marginTop: 12 }}>Export as PDF</button>
        </>
      )}
    </AppShell>
  );
}

const th = { textAlign: 'left', padding: '10px 24px', fontWeight: 700 };
const td = { padding: '10px 24px' };
