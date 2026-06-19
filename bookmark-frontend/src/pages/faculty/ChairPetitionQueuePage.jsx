import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import KanbanBoard from '../../components/KanbanBoard/KanbanBoard';
import StatusPill from '../../components/StatusPill/StatusPill';
import SegmentedControl from '../../components/SegmentedControl/SegmentedControl';
import { chairNav } from '../../config/navConfigs';
import { chairPetitions } from '../../mocks/facultyMocks';
import w from '../_shared/workflow.module.css';

/* Department Chair — escalated petition board (Kanban / List). */

const LANES = [
  { key: 'Escalated', color: 'var(--color-coral)' },
  { key: 'Under Review', color: 'var(--color-yellow)' },
  { key: 'Overridden', color: 'var(--color-lime)' },
  { key: 'Closed', color: '#7a7a72' },
];

export default function ChairPetitionQueuePage() {
  const navigate = useNavigate();
  const [view, setView] = useState('Kanban');
  const total = Object.values(chairPetitions).flat().length;

  return (
    <AppShell navItems={chairNav} logoVariant="stacked" sidebarLabel="DEPARTMENT CHAIR">
      <PageHeader
        title="Department Petition Board" subtitle={`Computer Science · ${total} escalated requests`} useBrandFont
        actions={<SegmentedControl options={['List View', 'Kanban']} value={view} onChange={setView} />}
      />

      {view === 'Kanban' ? (
        <KanbanBoard>
          {LANES.map((lane) => (
            <div key={lane.key} style={{ minWidth: 270, flex: 1 }}>
              <div style={{ background: lane.color, color: '#fff', fontWeight: 700, fontSize: '0.78rem', letterSpacing: '0.04em', textTransform: 'uppercase', padding: '8px 14px', borderRadius: '10px 10px 0 0' }}>
                {lane.key} · {(chairPetitions[lane.key] || []).length}
              </div>
              <div style={{ background: 'var(--color-bg-white)', borderRadius: '0 0 10px 10px', padding: 10, display: 'flex', flexDirection: 'column', gap: 10, minHeight: 120, boxShadow: '0 2px 12px rgba(0,0,0,0.05)' }}>
                {(chairPetitions[lane.key] || []).map((p) => (
                  <div key={p.id} onClick={() => navigate(`/faculty/chair/petitions/${p.id}`)}
                       style={{ border: '1px solid var(--color-border-light)', borderRadius: 8, padding: 12, cursor: 'pointer' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <strong>{p.ref}</strong><span style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)' }}>{p.date}</span>
                    </div>
                    <div style={{ fontSize: '0.85rem', fontWeight: 600, margin: '4px 0' }}>{p.studentName}</div>
                    <StatusPill status={p.type} variant="yellow" />
                    <div style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)', marginTop: 6 }}>{p.prior}</div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </KanbanBoard>
      ) : (
        <div className={w.card} style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {Object.entries(chairPetitions).flatMap(([lane, items]) => items.map((p) => (
            <div key={p.id} onClick={() => navigate(`/faculty/chair/petitions/${p.id}`)}
                 style={{ display: 'flex', alignItems: 'center', gap: 14, border: '1px solid var(--color-border-light)', borderRadius: 10, padding: 12, cursor: 'pointer' }}>
              <strong style={{ minWidth: 60 }}>{p.ref}</strong>
              <span style={{ flex: 1 }}>{p.studentName}</span>
              <StatusPill status={p.type} variant="yellow" />
              <StatusPill status={lane} variant={LANES.find((l) => l.key === lane)?.key === 'Escalated' ? 'coral' : 'green'} />
            </div>
          )))}
        </div>
      )}
    </AppShell>
  );
}
