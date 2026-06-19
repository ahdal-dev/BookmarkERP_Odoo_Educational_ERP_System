import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import AppShell from '../../components/AppShell/AppShell';
import StatusPill from '../../components/StatusPill/StatusPill';
import { supportNav } from '../../config/navConfigs';
import { supportAPI } from '../../api/apiGateway';
import useAsync from '../../hooks/useAsync';
import w from '../_shared/workflow.module.css';

/* Support Technician — single ticket / live-chat conversation view (live). */

const QUICK_REPLIES = ['Resend portal link', 'Check registration hold', 'Escalate to Registrar'];

export default function ChatSessionPage() {
  const { sessionId } = useParams();
  const tid = Number(sessionId);
  const navigate = useNavigate();
  const { data, loading, error, reload } = useAsync(() => supportAPI.getTicket(tid), [tid]);
  const ticket = data?.ticket;
  const messages = data?.messages || [];
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);

  const send = async (text) => {
    const t = (text ?? input).trim();
    if (!t) return;
    setBusy(true);
    try {
      await supportAPI.postMessage(tid, t);
      setInput('');
      await reload();
    } finally {
      setBusy(false);
    }
  };

  const escalate = async () => { await supportAPI.updateTicket(tid, { priority: 'high' }); reload(); };
  const close = async () => { await supportAPI.updateTicket(tid, { state: 'closed' }); navigate('/support/chat-queue'); };

  return (
    <AppShell navItems={supportNav} logoVariant="stacked" sidebarLabel="SUPPORT">
      {loading ? <div className={w.card}><div className={w.empty}>Loading conversation…</div></div>
      : error || !ticket ? <div className={w.card}><div className={w.empty}><div className={w.emptyTitle}>Couldn't load ticket</div><p>{error || 'Not found.'}</p><button className={`${w.btn} ${w.btnOutline} ${w.btnSm}`} onClick={() => navigate('/support/chat-queue')}>Back to queue</button></div></div>
      : (
        <>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <div><strong style={{ fontSize: '1.1rem' }}>{ticket.requester?.name || 'User'}</strong> · {ticket.ref} <StatusPill status={ticket.state} variant={ticket.state === 'closed' ? 'black' : 'green'} /></div>
            <div style={{ display: 'flex', gap: 10 }}>
              <button className={`${w.btn} ${w.btnOutline} ${w.btnSm}`} onClick={escalate} disabled={busy}>Escalate</button>
              <button className={`${w.btn} ${w.btnDanger} ${w.btnSm}`} onClick={close} disabled={busy}>Close &amp; Resolve</button>
            </div>
          </div>

          <div className={w.split} style={{ gridTemplateColumns: '300px 1fr' }}>
            <div className={w.cardDark}>
              <div className={w.sectionTitle} style={{ color: 'rgba(255,255,255,0.6)' }}>Ticket</div>
              <div style={{ fontWeight: 700, fontSize: '1.05rem' }}>{ticket.subject}</div>
              <div style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.7)', marginTop: 4 }}>{ticket.category} · {ticket.priority} priority</div>
              <div style={{ marginTop: 10 }}><StatusPill status={ticket.priority} variant={ticket.priority === 'high' ? 'coral' : 'green'} /></div>
              {ticket.description && <><div className={w.sectionTitle} style={{ color: 'rgba(255,255,255,0.6)', marginTop: 20 }}>Description</div><p style={{ fontSize: '0.82rem', color: 'rgba(255,255,255,0.8)' }}>{ticket.description}</p></>}
            </div>

            <div className={w.card} style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 220px)', minHeight: 420, padding: 0 }}>
              <div className={w.chatScroll}>
                {messages.length === 0 ? <div style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem', margin: 'auto' }}>No messages yet — say hello.</div>
                  : messages.map((m, i) => (
                    <div key={i} className={`${w.bubbleRow} ${w.bubbleRight}`}>
                      <div className={`${w.bubble} ${w.bubbleAgent}`}><div style={{ fontSize: '0.66rem', opacity: 0.7, marginBottom: 2 }}>{m.author}</div>{m.body}</div>
                    </div>
                  ))}
              </div>
              <div style={{ borderTop: '1px solid var(--color-border-light)', padding: 14 }}>
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 10 }}>
                  {QUICK_REPLIES.map((r) => <button key={r} className={w.filterTab} onClick={() => send(r)} disabled={busy}>{r}</button>)}
                </div>
                <div style={{ display: 'flex', gap: 10 }}>
                  <input className={w.search} placeholder="Type a message..." value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && send()} disabled={ticket.state === 'closed'} />
                  <button className={`${w.btn} ${w.btnPrimary}`} onClick={() => send()} disabled={busy || ticket.state === 'closed'}>Send</button>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </AppShell>
  );
}
