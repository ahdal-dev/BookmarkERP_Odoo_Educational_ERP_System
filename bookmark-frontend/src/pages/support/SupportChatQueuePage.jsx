import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import StatCard from '../../components/StatCard/StatCard';
import StatusPill from '../../components/StatusPill/StatusPill';
import { useNavigate } from 'react-router-dom';
import { supportNav } from '../../config/navConfigs';
import { supportAPI } from '../../api/apiGateway';
import useAsync from '../../hooks/useAsync';
import w from '../_shared/workflow.module.css';

/* Support Technician — live queue from support.ticket. */

export default function SupportChatQueuePage() {
  const navigate = useNavigate();
  const { data, loading, error, reload } = useAsync(() => supportAPI.listTickets(), []);
  const tickets = data?.tickets || [];
  const waiting = tickets.filter((t) => t.state === 'open');
  const active = tickets.filter((t) => t.state === 'in_progress');

  const accept = async (t) => {
    await supportAPI.updateTicket(t.id, { state: 'in_progress' });
    navigate(`/support/chat/${t.id}`);
  };

  return (
    <AppShell navItems={supportNav} logoVariant="stacked" sidebarLabel="SUPPORT">
      <PageHeader title="Live Support Queue" subtitle="Open tickets awaiting a technician" useBrandFont />

      {loading ? <div className={w.card}><div className={w.empty}>Loading queue…</div></div>
      : error ? <div className={w.card}><div className={w.empty}><div className={w.emptyTitle}>Couldn't load the queue</div><p>{error}</p><button className={`${w.btn} ${w.btnOutline} ${w.btnSm}`} onClick={reload}>Retry</button></div></div>
      : (
        <>
          <div className={`${w.statRow} ${w.cols3}`}>
            <StatCard value={waiting.length} label="Queue Waiting" accentColor="var(--color-coral)" />
            <StatCard value={active.length} label="Active Sessions" accentColor="var(--color-lime)" />
            <StatCard value={tickets.length} label="Total Tickets" accentColor="var(--color-yellow)" />
          </div>

          <div className={`${w.card} ${w.cardAccent}`}>
            <div className={w.sectionTitle}>Waiting</div>
            {waiting.length === 0 ? <div className={w.empty}><div className={w.emptyTitle}>✓ Queue is clear</div></div> : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {waiting.map((q) => (
                  <div key={q.id} style={{ display: 'flex', alignItems: 'center', gap: 12, border: '1px solid var(--color-border-light)', borderRadius: 10, padding: 12 }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>{q.ref} · {q.requester?.name || 'User'}</div>
                      <div style={{ marginTop: 4 }}><StatusPill status={q.subject} variant="yellow" /></div>
                    </div>
                    <StatusPill status={q.priority} variant={q.priority === 'high' ? 'coral' : 'green'} />
                    <button className={`${w.btn} ${w.btnGreen} ${w.btnSm}`} onClick={() => accept(q)}>Accept Chat</button>
                  </div>
                ))}
              </div>
            )}

            {active.length > 0 && <div className={w.sectionTitle} style={{ marginTop: 18 }}>Active Sessions</div>}
            {active.map((a) => (
              <div key={a.id} onClick={() => navigate(`/support/chat/${a.id}`)} style={{ display: 'flex', alignItems: 'center', gap: 10, border: '1.5px solid var(--color-lime)', borderRadius: 10, padding: 12, cursor: 'pointer', marginTop: 8 }}>
                <span className={w.pulse} />
                <div style={{ flex: 1, fontSize: '0.85rem', fontWeight: 600 }}>{a.ref} · {a.requester?.name || 'User'}</div>
                <StatusPill status="Live" variant="green" />
              </div>
            ))}
          </div>
        </>
      )}
    </AppShell>
  );
}
