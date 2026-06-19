import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import PublicShell from '../../components/PublicShell/PublicShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import StatusPill from '../../components/StatusPill/StatusPill';
import w from '../_shared/workflow.module.css';

/* Public admissions landing — admission tracks, application pipeline,
   program listing, and a prominent Apply Now call-to-action. */

const PROGRAMS = [
  { name: 'Computer Science & AI', level: 'B.Sc.', dept: 'Engineering', duration: '4 years', seats: 60, track: 'undergraduate' },
  { name: 'Data Science', level: 'B.Sc.', dept: 'Engineering', duration: '4 years', seats: 40, track: 'undergraduate' },
  { name: 'Nanotechnology', level: 'M.Sc.', dept: 'Science', duration: '2 years', seats: 20, track: 'graduate' },
  { name: 'Architecture', level: 'M.Sc.', dept: 'Design', duration: '2 years', seats: 25, track: 'graduate' },
  { name: 'Biomedical Sciences', level: 'Ph.D.', dept: 'Science', duration: '4 years', seats: 12, track: 'graduate' },
  { name: 'Renewable Energy', level: 'M.Sc.', dept: 'Engineering', duration: '2 years', seats: 18, track: 'graduate' },
];
const LEVELS = ['All', 'B.Sc.', 'M.Sc.', 'Ph.D.'];

// Admission tracks the applicant can choose from.
const TRACKS = [
  { key: 'undergraduate', title: 'Undergraduate', tag: 'B.Sc. / B.A.', desc: "Bachelor's programs for high-school graduates." },
  { key: 'graduate', title: 'Graduate', tag: 'M.Sc. / Ph.D.', desc: "Master's and doctoral research programs." },
  { key: 'transfer', title: 'Transfer', tag: 'Credit transfer', desc: 'Continue your studies with transferred credits.' },
  { key: 'international', title: 'International', tag: 'Visa support', desc: 'For applicants studying from abroad.' },
];

// The multi-step admission pipeline shown to guide applicants.
const PIPELINE = [
  { n: 1, title: 'Submit Application', desc: 'Create an account and complete the online form.' },
  { n: 2, title: 'Upload Documents', desc: 'Transcripts, ID & supporting files — OCR-verified.' },
  { n: 3, title: 'Entrance Assessment', desc: 'Complete any required placement test.' },
  { n: 4, title: 'Interview', desc: 'Meet with the admissions committee.' },
  { n: 5, title: 'Decision', desc: 'Receive your admission decision.' },
  { n: 6, title: 'Enroll', desc: 'Accept your offer and register for courses.' },
];

export default function AdmissionsPortalPage() {
  const navigate = useNavigate();
  const [q, setQ] = useState('');
  const [level, setLevel] = useState('All');
  const [track, setTrack] = useState(null);

  const startApplication = () => navigate('/admissions/status');

  const rows = PROGRAMS.filter((p) =>
    (level === 'All' || p.level === level) &&
    (!track || p.track === track) &&
    p.name.toLowerCase().includes(q.toLowerCase())
  );

  return (
    <PublicShell active="Programs">
      <PageHeader
        title="Begin Your Academic Journey"
        subtitle="Explore programs and apply online at Bookmark University"
        useBrandFont
        actions={
          <button className={`${w.btn} ${w.btnGreen}`} onClick={startApplication}>Apply Now →</button>
        }
      />

      {/* ===== ADMISSION TRACKS ===== */}
      <div className={w.section}>
        <div className={w.sectionTitle}>Admission Tracks</div>
        <div className={`${w.statRow} ${w.cols4}`} style={{ marginBottom: 0 }}>
          {TRACKS.map((t) => (
            <button
              key={t.key}
              className={`${w.card} ${w.cardAccent}`}
              onClick={() => setTrack(track === t.key ? null : t.key)}
              style={{
                textAlign: 'left', cursor: 'pointer', fontFamily: 'inherit',
                outline: track === t.key ? '2px solid var(--color-lime)' : 'none',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3 style={{ fontWeight: 800, fontSize: '1rem' }}>{t.title}</h3>
                <StatusPill status={t.tag} variant="yellow" />
              </div>
              <p className={w.cardSub} style={{ marginTop: 8, marginBottom: 0 }}>{t.desc}</p>
            </button>
          ))}
        </div>
        {track && (
          <p style={{ fontSize: '0.82rem', color: 'var(--color-text-muted)', marginTop: 10 }}>
            Showing <strong>{TRACKS.find((t) => t.key === track)?.title}</strong> programs ·{' '}
            <span className={w.cardLink} onClick={() => setTrack(null)}>Clear track</span>
          </p>
        )}
      </div>

      {/* ===== ADMISSION PIPELINE ===== */}
      <div className={w.section}>
        <div className={w.sectionTitle}>Admission Pipeline</div>
        <div className={w.card}>
          <div className={w.pipeline}>
            {PIPELINE.map((s, i) => (
              <div key={s.n} className={w.pipeStage}>
                {i > 0 && <span className={w.pipeConnector} />}
                <div className={w.pipeNum}>{s.n}</div>
                <div className={w.pipeTitle}>{s.title}</div>
                <div className={w.pipeDesc}>{s.desc}</div>
              </div>
            ))}
          </div>
          <button className={`${w.btn} ${w.btnPrimary}`} style={{ marginTop: 20 }} onClick={startApplication}>
            Start your application →
          </button>
        </div>
      </div>

      {/* ===== PROGRAMS ===== */}
      <div className={w.sectionTitle}>Available Programs</div>
      <div className={w.toolbar}>
        <input className={w.search} placeholder="Search programs..." value={q} onChange={(e) => setQ(e.target.value)} />
        <div className={w.filterTabs}>
          {LEVELS.map((l) => <button key={l} className={`${w.filterTab} ${level === l ? w.filterTabActive : ''}`} onClick={() => setLevel(l)}>{l}</button>)}
        </div>
      </div>

      <div className={`${w.statRow} ${w.cols3}`} style={{ marginBottom: 0 }}>
        {rows.map((p) => (
          <div key={p.name} className={`${w.card} ${w.cardAccent}`}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <h3 style={{ fontWeight: 800, fontSize: '1.05rem' }}>{p.name}</h3>
              <StatusPill status={p.level} variant="green" />
            </div>
            <div className={w.cardSub}>{p.dept}</div>
            <div className={w.metaRow}>
              <StatusPill status={`${p.duration}`} variant="black" />
              <StatusPill status={`${p.seats} seats`} variant="yellow" />
            </div>
            <button className={`${w.btn} ${w.btnPrimary} ${w.btnFull}`} onClick={() => navigate('/admissions/status')}>Apply Now →</button>
          </div>
        ))}
      </div>

      <p style={{ textAlign: 'center', marginTop: 28, fontSize: '0.88rem', color: 'var(--color-text-muted)' }}>
        Already applied? <span className={w.cardLink} onClick={() => navigate('/admissions/status')}>Track your application →</span>
      </p>
    </PublicShell>
  );
}
