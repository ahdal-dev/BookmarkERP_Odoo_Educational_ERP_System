import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import StatusPill from '../../components/StatusPill/StatusPill';
import { advisorNav } from '../../config/navConfigs';
import { advisingAPI } from '../../api/apiGateway';
import useAsync from '../../hooks/useAsync';
import w from '../_shared/workflow.module.css';

/* Academic advisor — searchable advisee list (live). */

const FILTERS = ['All', 'Active Petitions', 'At-Risk GPA'];
const CLASS_LABELS = { freshman: 'Freshman', sophomore: 'Sophomore', junior: 'Junior', senior: 'Senior' };

function initials(name = '') { return name.split(' ').map((p) => p[0]).slice(0, 2).join(''); }
function gpaVariant(g) { return g >= 3.0 ? 'green' : g >= 2.0 ? 'yellow' : 'coral'; }

export default function AdviseeListPage() {
  const navigate = useNavigate();
  const { data, loading, error, reload } = useAsync(() => advisingAPI.getAdvisees(), []);
  const advisees = data?.advisees || [];
  const [q, setQ] = useState('');
  const [filter, setFilter] = useState('All');

  const rows = advisees.filter((s) => {
    if (q && !(s.name || '').toLowerCase().includes(q.toLowerCase()) && !(s.email || '').toLowerCase().includes(q.toLowerCase())) return false;
    if (filter === 'Active Petitions') return s.active_petitions > 0;
    if (filter === 'At-Risk GPA') return s.gpa < 2.5;
    return true;
  });

  return (
    <AppShell navItems={advisorNav} logoVariant="stacked" sidebarLabel="ACADEMIC ADVISOR">
      <PageHeader title="My Advisees" subtitle={`${advisees.length} students assigned`} useBrandFont />

      <div className={w.toolbar}>
        <input className={w.search} placeholder="Search advisee by name or email..." value={q} onChange={(e) => setQ(e.target.value)} />
      </div>
      <div className={w.filterTabs} style={{ marginBottom: 18 }}>
        {FILTERS.map((f) => (
          <button key={f} className={`${w.filterTab} ${filter === f ? w.filterTabActive : ''}`} onClick={() => setFilter(f)}>{f}</button>
        ))}
      </div>

      {loading ? (
        <div className={w.card}><div className={w.empty}>Loading advisees…</div></div>
      ) : error ? (
        <div className={w.card}><div className={w.empty}>
          <div className={w.emptyTitle}>Couldn't load advisees</div>
          <p>{error}</p>
          <button className={`${w.btn} ${w.btnOutline} ${w.btnSm}`} onClick={reload}>Retry</button>
        </div></div>
      ) : rows.length === 0 ? (
        <div className={w.card}><div className={w.empty}><div className={w.emptyTitle}>No advisees</div><p>No students match this view.</p></div></div>
      ) : (
        <div className={w.cardGrid2}>
          {rows.map((s) => (
            <div key={s.id} className={w.card} style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
              <div style={{ width: 46, height: 46, borderRadius: '50%', background: 'var(--color-primary-black)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700 }}>{initials(s.name)}</div>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 700 }}>{s.name} {s.active_petitions > 0 && <span style={{ color: 'var(--color-coral)' }}>●</span>}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>{s.email}</div>
                <div style={{ marginTop: 6, display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
                  <StatusPill status={CLASS_LABELS[s.class_year] || s.class_year} variant="green" />
                  <StatusPill status={`GPA ${(s.gpa ?? 0).toFixed(2)}`} variant={gpaVariant(s.gpa)} />
                  {s.on_hold && <StatusPill status="On Hold" variant="coral" />}
                </div>
              </div>
              <span className={w.cardLink} onClick={() => navigate(`/faculty/advisees/${s.id}`)}>View Profile →</span>
            </div>
          ))}
        </div>
      )}
    </AppShell>
  );
}
