import { useState } from 'react';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import StatCard from '../../components/StatCard/StatCard';
import StatusPill from '../../components/StatusPill/StatusPill';
import { studentNav } from '../../config/navConfigs';
import w from '../_shared/workflow.module.css';

/* Read-only unofficial transcript with semester accordion. */

const GRADE_COLOR = { A: 'green', 'A-': 'green', 'B+': 'yellow', B: 'yellow', 'B-': 'yellow', C: 'coral', F: 'coral', W: 'black' };

const SEMESTERS = [
  {
    term: 'Fall 2025', credits: 15, gpa: 3.85, open: true,
    courses: [
      { code: 'CS101', name: 'Introduction to Computer Science', credits: 3, grade: 'A', status: 'Completed' },
      { code: 'MATH200', name: 'Calculus II', credits: 4, grade: 'A-', status: 'Completed' },
      { code: 'PHYS210', name: 'Classical Mechanics', credits: 3, grade: 'B+', status: 'Completed' },
      { code: 'ENG105', name: 'Academic Writing', credits: 3, grade: 'A', status: 'Completed' },
      { code: 'HIST110', name: 'World History', credits: 2, grade: 'B', status: 'Completed' },
    ],
  },
  {
    term: 'Spring 2025', credits: 16, gpa: 3.60, open: false,
    courses: [
      { code: 'CS100', name: 'Computing Foundations', credits: 3, grade: 'A', status: 'Completed' },
      { code: 'MATH100', name: 'Calculus I', credits: 4, grade: 'B+', status: 'Completed' },
      { code: 'CHEM101', name: 'General Chemistry', credits: 4, grade: 'B', status: 'Completed' },
      { code: 'ENG104', name: 'Composition', credits: 3, grade: 'A-', status: 'Completed' },
      { code: 'PE101', name: 'Physical Education', credits: 2, grade: 'W', status: 'Withdrawn' },
    ],
  },
];

export default function GradesPage() {
  const [open, setOpen] = useState(() => Object.fromEntries(SEMESTERS.map((s) => [s.term, s.open])));

  return (
    <AppShell navItems={studentNav} logoVariant="stacked" sidebarLabel="STUDENT PORTAL">
      <PageHeader title="Academic Transcript" subtitle="Unofficial · For an official copy contact the Registrar" useBrandFont />

      <div className={`${w.statRow} ${w.cols3}`}>
        <StatCard value="3.72 / 4.00" label="Cumulative GPA" accentColor="var(--color-lime)" />
        <StatCard value="87" label="Total Credits Earned" accentColor="var(--color-yellow)" />
        <StatCard value="Good Standing" label="Academic Standing" accentColor="var(--color-lime)" />
      </div>

      {SEMESTERS.map((s) => (
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
              {s.credits} credits · GPA: {s.gpa.toFixed(2)} <span style={{ marginLeft: 10 }}>{open[s.term] ? '▾' : '▸'}</span>
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
    </AppShell>
  );
}

const th = { textAlign: 'left', padding: '10px 24px', fontWeight: 700 };
const td = { padding: '10px 24px' };
