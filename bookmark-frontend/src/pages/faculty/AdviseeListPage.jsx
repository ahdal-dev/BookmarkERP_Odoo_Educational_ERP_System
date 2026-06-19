import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import StatusPill from '../../components/StatusPill/StatusPill';
import { advisorNav } from '../../config/navConfigs';
import { advisees, gpaVariant } from '../../mocks/facultyMocks';
import w from '../_shared/workflow.module.css';

/* Academic advisor — searchable advisee list. */

const FILTERS = ['All', 'Active Petitions', 'At-Risk GPA', 'Graduating'];

function initials(name) { return name.split(' ').map((p) => p[0]).slice(0, 2).join(''); }

export default function AdviseeListPage() {
  const navigate = useNavigate();
  const [q, setQ] = useState('');
  const [filter, setFilter] = useState('All');

  const rows = advisees.filter((s) => {
    if (q && !s.name.toLowerCase().includes(q.toLowerCase()) && !s.sid.toLowerCase().includes(q.toLowerCase())) return false;
    if (filter === 'Active Petitions') return s.petition;
    if (filter === 'At-Risk GPA') return s.gpa < 2.5;
    return true;
  });

  return (
    <AppShell navItems={advisorNav} logoVariant="stacked" sidebarLabel="ACADEMIC ADVISOR">
      <PageHeader title="My Advisees" subtitle={`${advisees.length} students assigned · Fall 2026`} useBrandFont />

      <div className={w.toolbar}>
        <input className={w.search} placeholder="Search advisee by name or ID..." value={q} onChange={(e) => setQ(e.target.value)} />
      </div>
      <div className={w.filterTabs} style={{ marginBottom: 18 }}>
        {FILTERS.map((f) => (
          <button key={f} className={`${w.filterTab} ${filter === f ? w.filterTabActive : ''}`} onClick={() => setFilter(f)}>{f}</button>
        ))}
      </div>

      <div className={w.cardGrid2}>
        {rows.map((s) => (
          <div key={s.sid} className={w.card} style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
            <div style={{ width: 46, height: 46, borderRadius: '50%', background: 'var(--color-primary-black)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700 }}>{initials(s.name)}</div>
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 700 }}>{s.name} {s.petition && <span style={{ color: 'var(--color-coral)' }}>●</span>}</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>{s.sid}</div>
              <div style={{ marginTop: 6, display: 'flex', gap: 8, alignItems: 'center' }}>
                <StatusPill status={s.major} variant="green" />
                <StatusPill status={`GPA ${s.gpa}`} variant={gpaVariant(s.gpa)} />
              </div>
            </div>
            <span className={w.cardLink} onClick={() => navigate(`/faculty/advisees/${s.sid}`)}>View Profile →</span>
          </div>
        ))}
      </div>
    </AppShell>
  );
}
