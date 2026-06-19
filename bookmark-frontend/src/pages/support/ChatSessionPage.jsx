import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import AppShell from '../../components/AppShell/AppShell';
import StatusPill from '../../components/StatusPill/StatusPill';
import { supportNav } from '../../config/navConfigs';
import w from '../_shared/workflow.module.css';

/* Support Technician — single live-chat conversation view. */

const QUICK_REPLIES = ['Resend portal link', 'Check registration hold', 'Escalate to Registrar'];

export default function ChatSessionPage() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [messages, setMessages] = useState([
    { from: 'student', text: "Hi, I can't register — it says I have a hold on my account?" },
    { from: 'agent', text: 'Hello! Let me pull up your record and check that for you.' },
  ]);
  const [input, setInput] = useState('');

  const send = (text) => {
    const t = (text ?? input).trim();
    if (!t) return;
    setMessages((m) => [...m, { from: 'agent', text: t }]);
    setInput('');
  };

  return (
    <AppShell navItems={supportNav} logoVariant="stacked" sidebarLabel="SUPPORT">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div><strong style={{ fontSize: '1.1rem' }}>Aya Hassan</strong> · Session #{sessionId} <StatusPill status="Live" variant="green" /></div>
        <div style={{ display: 'flex', gap: 10 }}>
          <button className={`${w.btn} ${w.btnOutline} ${w.btnSm}`}>Escalate Ticket</button>
          <button className={`${w.btn} ${w.btnDanger} ${w.btnSm}`} onClick={() => navigate('/support/chat-queue')}>Close & Resolve</button>
        </div>
      </div>

      <div className={w.split} style={{ gridTemplateColumns: '300px 1fr' }}>
        {/* Mini agent info sidebar */}
        <div className={w.cardDark}>
          <div className={w.sectionTitle} style={{ color: 'rgba(255,255,255,0.6)' }}>Student</div>
          <div style={{ fontWeight: 700, fontSize: '1.05rem' }}>Aya Hassan</div>
          <div style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.7)' }}>STU-2024-011 · Sophomore · B.Sc. CS</div>
          <div style={{ margintop: 8 }}><StatusPill status="Registration Hold" variant="coral" /></div>
          <a className={w.cardLink} style={{ color: 'var(--color-lime)', display: 'block', marginTop: 12 }}>Open Full Profile →</a>

          <div className={w.sectionTitle} style={{ color: 'rgba(255,255,255,0.6)', marginTop: 20 }}>Ticket History</div>
          {[{ t: 'Login Issue', d: 'Sep 12', s: 'Resolved' }, { t: 'Portal Bug', d: 'Aug 30', s: 'Closed' }].map((t, i) => (
            <div key={i} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', padding: '6px 0', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
              <span>{t.t}</span><span style={{ color: 'rgba(255,255,255,0.5)' }}>{t.d} · {t.s}</span>
            </div>
          ))}
        </div>

        {/* Chat area */}
        <div className={w.card} style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 220px)', minHeight: 420, padding: 0 }}>
          <div className={w.chatScroll}>
            {messages.map((m, i) => (
              <div key={i} className={`${w.bubbleRow} ${m.from === 'student' ? w.bubbleLeft : w.bubbleRight}`}>
                <div className={`${w.bubble} ${m.from === 'student' ? w.bubbleStudent : w.bubbleAgent}`}>{m.text}</div>
              </div>
            ))}
          </div>
          <div style={{ borderTop: '1px solid var(--color-border-light)', padding: 14 }}>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 10 }}>
              {QUICK_REPLIES.map((r) => <button key={r} className={`${w.filterTab}`} onClick={() => send(r)}>{r}</button>)}
            </div>
            <div style={{ display: 'flex', gap: 10 }}>
              <input className={w.search} placeholder="Type a message..." value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && send()} />
              <button className={`${w.btn} ${w.btnPrimary}`} onClick={() => send()}>Send</button>
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
