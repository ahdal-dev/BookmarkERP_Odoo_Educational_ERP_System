import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import StatusPill from '../../components/StatusPill/StatusPill';
import SegmentedControl from '../../components/SegmentedControl/SegmentedControl';
import { advisorNav } from '../../config/navConfigs';
import { advisees, gpaVariant } from '../../mocks/facultyMocks';
import w from '../_shared/workflow.module.css';

/* Read-only advisee academic profile. */

const TERMS = [
  { term: 'Fall 2025', gpa: 3.85 }, { term: 'Spring 2025', gpa: 3.60 }, { term: 'Fall 2024', gpa: 3.40 },
];
const HISTORY = [
  { term: 'Fall 2025', course: 'CSAI 301 — Advanced Algorithms', credits: 3, grade: 'A' },
  { term: 'Fall 2025', course: 'MATH 200 — Calculus II', credits: 4, grade: 'A-' },
  { term: 'Spring 2025', course: 'CSAI 220 — Data Structures', credits: 3, grade: 'B+' },
];

function initials(name) { return name.split(' ').map((p) => p[0]).slice(0, 2).join(''); }

export default function AdviseeProfilePage() {
  const { studentId } = useParams();
  const navigate = useNavigate();
  const s = advisees.find((a) => a.sid === studentId) || advisees[0];
  const [tab, setTab] = useState('Academic Record');
  const [note, setNote] = useState('');

  return (
    <AppShell navItems={advisorNav} logoVariant="stacked" sidebarLabel="ACADEMIC ADVISOR">
      <div className={w.breadcrumb}>
        <span onClick={() => navigate('/faculty/advisees')} style={{ cursor: 'pointer' }}>My Advisees</span> › {s.name}
      </div>

      {/* Profile header (dark) */}
      <div className={w.cardDark} style={{ display: 'flex', alignItems: 'center', gap: 20, marginBottom: 20 }}>
        <div style={{ width: 64, height: 64, borderRadius: '50%', background: 'rgba(255,255,255,0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, fontSize: '1.3rem' }}>{initials(s.name)}</div>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: '1.4rem', fontWeight: 800 }}>{s.name}</div>
          <div style={{ color: 'rgba(255,255,255,0.7)', fontSize: '0.85rem' }}>{s.sid} · {s.name.toLowerCase().replace(' ', '.')}@zc.edu · Enrolled 2024</div>
          <div style={{ marginTop: 8 }}><StatusPill status={s.major} variant="green" /></div>
        </div>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--color-lime)' }}>{s.gpa}</div>
          <div style={{ fontSize: '0.72rem', color: 'rgba(255,255,255,0.6)' }}>Cumulative GPA</div>
        </div>
      </div>

      <div style={{ marginBottom: 16 }}>
        <SegmentedControl options={['Academic Record', 'Registered Courses', 'Petitions', 'Notes']} value={tab} onChange={setTab} />
      </div>

      {tab === 'Academic Record' && (
        <div className={w.card}>
          <div className={w.sectionTitle}>Semester GPA</div>
          {TERMS.map((t) => (
            <div key={t.term} style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
              <span style={{ width: 110, fontSize: '0.82rem' }}>{t.term}</span>
              <div className={w.bar} style={{ flex: 1 }}><div className={w.barFill} style={{ width: `${(t.gpa / 4) * 100}%`, background: gpaVariant(t.gpa) === 'green' ? 'var(--color-lime)' : 'var(--color-yellow)' }} /></div>
              <span style={{ fontWeight: 700, fontSize: '0.82rem' }}>{t.gpa.toFixed(2)}</span>
            </div>
          ))}
          <div className={w.sectionTitle} style={{ marginTop: 20 }}>Course History</div>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
            <thead><tr style={{ textTransform: 'uppercase', fontSize: '0.66rem', color: 'var(--color-text-muted)', textAlign: 'left' }}>
              <th style={{ padding: 8 }}>Semester</th><th style={{ padding: 8 }}>Course</th><th style={{ padding: 8 }}>Credits</th><th style={{ padding: 8 }}>Grade</th>
            </tr></thead>
            <tbody>{HISTORY.map((h, i) => (
              <tr key={i} style={{ borderTop: '1px solid var(--color-border-light)' }}>
                <td style={{ padding: 8 }}>{h.term}</td><td style={{ padding: 8 }}>{h.course}</td><td style={{ padding: 8 }}>{h.credits}</td>
                <td style={{ padding: 8 }}><StatusPill status={h.grade} variant="green" /></td>
              </tr>
            ))}</tbody>
          </table>
        </div>
      )}

      {tab === 'Notes' && (
        <div className={w.card}>
          <div className={w.field}>
            <span className={w.fieldLabel}>Add a private advising note</span>
            <textarea className={w.textarea} value={note} onChange={(e) => setNote(e.target.value)} placeholder="Visible only to advisors and the chair..." />
          </div>
          <button className={`${w.btn} ${w.btnPrimary}`} disabled={!note.trim()}>Save Note</button>
          <div className={w.sectionTitle} style={{ marginTop: 20 }}>Previous Notes</div>
          <div className={w.quote}>Discussed course-load plan for spring; student on track. — Sep 14, 2026</div>
        </div>
      )}

      {(tab === 'Registered Courses' || tab === 'Petitions') && (
        <div className={`${w.card} ${w.empty}`}><div className={w.emptyTitle}>{tab}</div><p>{tab} for {s.name} will appear here.</p></div>
      )}

      <div className={w.readonlyBar}>🔒 You are viewing this profile in read-only mode. To make changes, contact the Registrar.</div>
    </AppShell>
  );
}
