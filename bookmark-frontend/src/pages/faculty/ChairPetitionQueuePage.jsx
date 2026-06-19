import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import KanbanBoard from '../../components/KanbanBoard/KanbanBoard';
import StatusPill from '../../components/StatusPill/StatusPill';
import SegmentedControl from '../../components/SegmentedControl/SegmentedControl';
import { chairNav } from '../../config/navConfigs';
import { facultyAPI } from '../../api/apiGateway';
import useAsync from '../../hooks/useAsync';
import w from '../_shared/workflow.module.css';

/* Department Chair — escalated petition board (live, Kanban / List). */

const LANES = [
  { key: 'submitted', label: 'Submitted', color: 'var(--color-coral)' },
  { key: 'under_review', label: 'Under Review', color: 'var(--color-yellow)' },
  { key: 'approved', label: 'Approved', color: 'var(--color-lime)' },
  { key: 'rejected', label: 'Rejected', color: '#7a7a72' },
];

export default function ChairPetitionQueuePage() {
  const navigate = useNavigate();
  const { data, loading, error, reload } = useAsync(
    () => facultyAPI.getPetitionQueue({ states: 'submitted,under_review,approved,rejected' }), []);
  const petitions = data?.petitions || [];
  const [view, setView] = useState('Kanban');

  const byLane = (key) => petitions.filter((p) => p.state === key);

  const card = (p) => (
    <div key={p.id} onClick={() => navigate(`/faculty/chair/petitions/${p.id}`)}
         style={{ border: '1px solid var(--color-border-light)', borderRadius: 8, padding: 12, cursor: 'pointer' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <strong>{p.name}</strong><span style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)' }}>{p.submitted_date}</span>
      </div>
      <div style={{ fontSize: '0.85rem', fontWeight: 600, margin: '4px 0' }}>{p.student_id?.name || 'Student'}</div>
      <StatusPill status={p.petition_type_id?.name || 'Petition'} variant="yellow" />
      {p.is_escalated && <div style={{ fontSize: '0.72rem', color: 'var(--color-coral)', marginTop: 6 }}>Escalated</div>}
    </div>
  );

  return (
    <AppShell navItems={chairNav} logoVariant="stacked" sidebarLabel="DEPARTMENT CHAIR">
      <PageHeader
        title="Department Petition Board" subtitle={`${petitions.length} requests`} useBrandFont
        actions={<SegmentedControl options={['List View', 'Kanban']} value={view} onChange={setView} />}
      />

      {loading ? <div className={w.card}><div className={w.empty}>Loading petitions…</div></div>
      : error ? <div className={w.card}><div className={w.empty}><div className={w.emptyTitle}>Couldn't load board</div><p>{error}</p><button className={`${w.btn} ${w.btnOutline} ${w.btnSm}`} onClick={reload}>Retry</button></div></div>
      : view === 'Kanban' ? (
        <KanbanBoard>
          {LANES.map((lane) => (
            <div key={lane.key} style={{ minWidth: 270, flex: 1 }}>
              <div style={{ background: lane.color, color: '#fff', fontWeight: 700, fontSize: '0.78rem', letterSpacing: '0.04em', textTransform: 'uppercase', padding: '8px 14px', borderRadius: '10px 10px 0 0' }}>
                {lane.label} · {byLane(lane.key).length}
              </div>
              <div style={{ background: 'var(--color-bg-white)', borderRadius: '0 0 10px 10px', padding: 10, display: 'flex', flexDirection: 'column', gap: 10, minHeight: 120, boxShadow: '0 2px 12px rgba(0,0,0,0.05)' }}>
                {byLane(lane.key).map(card)}
              </div>
            </div>
          ))}
        </KanbanBoard>
      ) : (
        <div className={w.card} style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {petitions.map((p) => (
            <div key={p.id} onClick={() => navigate(`/faculty/chair/petitions/${p.id}`)}
                 style={{ display: 'flex', alignItems: 'center', gap: 14, border: '1px solid var(--color-border-light)', borderRadius: 10, padding: 12, cursor: 'pointer' }}>
              <strong style={{ minWidth: 70 }}>{p.name}</strong>
              <span style={{ flex: 1 }}>{p.student_id?.name || 'Student'}</span>
              <StatusPill status={p.petition_type_id?.name || 'Petition'} variant="yellow" />
              <StatusPill status={p.state} variant={p.state === 'approved' ? 'green' : p.state === 'rejected' ? 'coral' : 'yellow'} />
            </div>
          ))}
        </div>
      )}
    </AppShell>
  );
}
