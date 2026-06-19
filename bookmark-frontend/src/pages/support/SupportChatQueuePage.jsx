import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import StatCard from '../../components/StatCard/StatCard';
import StatusPill from '../../components/StatusPill/StatusPill';
import { supportNav } from '../../config/navConfigs';
import w from '../_shared/workflow.module.css';

/* Support Technician — live chat queue + active session preview. */

const WAITING = [
  { id: 1042, name: 'Aya Hassan', sid: 'STU-2024-011', issue: 'Registration Error', wait: '6m 12s', urgent: true },
  { id: 1043, name: 'Omar Khaled', sid: 'STU-2024-042', issue: 'Login Issue', wait: '4m 02s', urgent: false },
  { id: 1044, name: 'Lina Saad', sid: 'STU-2023-118', issue: 'Portal Bug', wait: '2m 47s', urgent: false },
];
const ACTIVE = [
  { id: 1039, name: 'Marcus Thorne', sid: 'STU-2024-204', issue: 'Hold Inquiry' },
];

export default function SupportChatQueuePage() {
  const navigate = useNavigate();
  const [selected, setSelected] = useState(ACTIVE[0]);

  return (
    <AppShell navItems={supportNav} logoVariant="stacked" sidebarLabel="SUPPORT">
      <PageHeader title="Live Support Queue" subtitle="Registration Period · Peak Load Active 🔴" useBrandFont />

      <div className={`${w.statRow} ${w.cols3}`}>
        <StatCard value="14" label="Queue Waiting" accentColor="var(--color-coral)" />
        <StatCard value="3" label="Active Sessions" accentColor="var(--color-lime)" />
        <StatCard value="4m 12s" label="Avg. Wait Time" accentColor="var(--color-yellow)" />
      </div>

      <div className={w.split}>
        {/* Queue */}
        <div className={`${w.card} ${w.cardAccent}`}>
          <div className={w.sectionTitle}>Waiting</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {WAITING.map((q) => (
              <div key={q.id} style={{ display: 'flex', alignItems: 'center', gap: 12, border: '1px solid var(--color-border-light)', borderRadius: 10, padding: 12 }}>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>{q.name} <span style={{ color: 'var(--color-text-muted)', fontWeight: 400 }}>· {q.sid}</span></div>
                  <div style={{ marginTop: 4 }}><StatusPill status={q.issue} variant="yellow" /></div>
                </div>
                <span style={{ fontSize: '0.78rem', fontWeight: 700, color: q.urgent ? 'var(--color-coral)' : 'var(--color-text-muted)' }}>{q.wait}</span>
                <button className={`${w.btn} ${w.btnGreen} ${w.btnSm}`} onClick={() => navigate(`/support/chat/${q.id}`)}>Accept Chat</button>
              </div>
            ))}
          </div>
          <div className={w.sectionTitle} style={{ marginTop: 18 }}>Active Sessions</div>
          {ACTIVE.map((a) => (
            <div key={a.id} onClick={() => setSelected(a)} style={{ display: 'flex', alignItems: 'center', gap: 10, border: `1.5px solid ${selected?.id === a.id ? 'var(--color-lime)' : 'var(--color-border-light)'}`, borderRadius: 10, padding: 12, cursor: 'pointer' }}>
              <span className={w.pulse} />
              <div style={{ flex: 1, fontSize: '0.85rem', fontWeight: 600 }}>{a.name}</div>
              <StatusPill status="Live" variant="green" />
            </div>
          ))}
        </div>

        {/* Active chat preview */}
        <div className={`${w.card}`} style={{ display: 'flex', flexDirection: 'column', minHeight: 360 }}>
          {selected ? (
            <>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--color-border-light)', paddingBottom: 12, marginBottom: 12 }}>
                <div><strong>{selected.name}</strong> · Session #{selected.id}<div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>{selected.issue}</div></div>
                <button className={`${w.btn} ${w.btnPrimary} ${w.btnSm}`} onClick={() => navigate(`/support/chat/${selected.id}`)}>Open Full Chat →</button>
              </div>
              <div className={w.chatScroll} style={{ padding: 0 }}>
                <div className={`${w.bubbleRow} ${w.bubbleLeft}`}><div className={`${w.bubble} ${w.bubbleStudent}`}>Hi, I can't register — it says I have a hold?</div></div>
                <div className={`${w.bubbleRow} ${w.bubbleRight}`}><div className={`${w.bubble} ${w.bubbleAgent}`}>Let me check that for you. One moment…</div></div>
              </div>
            </>
          ) : <div className={w.empty}><div className={w.emptyTitle}>✓ Queue is clear</div><p>All students have been helped.</p></div>}
        </div>
      </div>
    </AppShell>
  );
}
