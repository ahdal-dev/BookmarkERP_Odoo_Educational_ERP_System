import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import StatusPill from '../../components/StatusPill/StatusPill';
import { studentNav } from '../../config/navConfigs';
import w from '../_shared/workflow.module.css';

/* Student petition history — filterable list of submitted requests. */

const TYPE_COLOR = { 'Course Overload': 'coral', 'Prereq Override': 'yellow', 'Late Drop': 'yellow', 'Grade Appeal': 'coral' };

const PETITIONS = [
  { ref: '#9412', type: 'Course Overload', date: 'Oct 14, 2026', course: 'CS101 — Intro to CS', desc: 'Requesting 18 credit hours for the fall term.', status: 'Pending' },
  { ref: '#9388', type: 'Prereq Override', date: 'Sep 30, 2026', course: 'CS305 — Algorithms', desc: 'Completed equivalent course at a partner institution.', status: 'Approved' },
  { ref: '#9301', type: 'Late Drop', date: 'Sep 12, 2026', course: 'BIO102 — General Biology', desc: 'Medical circumstances documented with the clinic.', status: 'Denied' },
];

const FILTERS = ['All', 'Pending', 'Approved', 'Denied'];

export default function PetitionListPage() {
  const navigate = useNavigate();
  const [filter, setFilter] = useState('All');

  const rows = PETITIONS.filter((p) => filter === 'All' || p.status === filter);

  return (
    <AppShell navItems={studentNav} logoVariant="stacked" sidebarLabel="STUDENT PORTAL">
      <PageHeader
        title="My Petitions" subtitle="Track all submitted academic requests" useBrandFont
        actions={<button className={`${w.btn} ${w.btnPrimary}`} onClick={() => navigate('/petitions/new')}>+ New Petition</button>}
      />

      <div className={w.filterTabs} style={{ marginBottom: 18 }}>
        {FILTERS.map((f) => (
          <button key={f} className={`${w.filterTab} ${filter === f ? w.filterTabActive : ''}`} onClick={() => setFilter(f)}>{f}</button>
        ))}
      </div>

      {rows.length === 0 ? (
        <div className={`${w.card} ${w.empty}`}>
          <div className={w.emptyTitle}>No petitions yet</div>
          <p>Submit one if you hit a registration block or need an academic exception.</p>
          <button className={`${w.btn} ${w.btnPrimary}`} style={{ marginTop: 16 }} onClick={() => navigate('/petitions/new')}>+ New Petition</button>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {rows.map((p) => (
            <div key={p.ref} className={w.card} style={{ display: 'flex', alignItems: 'center', gap: 20, padding: 18 }}>
              <div style={{ minWidth: 150 }}>
                <div style={{ fontWeight: 800 }}>{p.ref}</div>
                <StatusPill status={p.type} variant={TYPE_COLOR[p.type] || 'yellow'} />
                <div style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)', marginTop: 6 }}>{p.date}</div>
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600, fontSize: '0.88rem' }}>{p.course}</div>
                <div style={{ fontSize: '0.82rem', color: 'var(--color-text-secondary)' }}>{p.desc}</div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <StatusPill status={p.status} />
                <div style={{ marginTop: 8 }}>
                  <span className={w.cardLink} onClick={() => navigate('/petitions/new')}>View Details →</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </AppShell>
  );
}
