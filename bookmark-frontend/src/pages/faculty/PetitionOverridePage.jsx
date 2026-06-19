import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import StatusPill from '../../components/StatusPill/StatusPill';
import { chairNav } from '../../config/navConfigs';
import { facultyPetitions } from '../../mocks/facultyMocks';
import w from '../_shared/workflow.module.css';

/* Department Chair — override screen with full ruling history (final authority). */

const RULING_HISTORY = [
  { color: 'var(--color-lime)', text: 'Student submitted', actor: 'Oct 12, 2026' },
  { color: 'var(--color-coral)', text: 'Instructor: REJECTED — "Outside add/drop window."', actor: 'Oct 13, 2026' },
  { color: 'var(--color-coral)', text: 'Advisor: REJECTED — "Insufficient documentation."', actor: 'Oct 15, 2026' },
  { color: 'var(--color-yellow)', text: 'Escalated to Department Chair', actor: 'Oct 16, 2026' },
];

export default function PetitionOverridePage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const p = facultyPetitions.find((x) => x.id === id) || facultyPetitions[0];

  const [ruling, setRuling] = useState('Override & Approve');
  const [conditions, setConditions] = useState('');
  const [reason, setReason] = useState('');
  const [issued, setIssued] = useState(false);

  return (
    <AppShell navItems={chairNav} logoVariant="stacked" sidebarLabel="DEPARTMENT CHAIR">
      <div className={w.breadcrumb}>
        <span onClick={() => navigate('/faculty/chair/petitions')} style={{ cursor: 'pointer' }}>Chair Panel</span> › Petitions › {p.ref} — Override
      </div>
      <PageHeader title={`${p.ref} — Override`} useBrandFont />

      <div className={`${w.alert} ${w.alertCoral}`}>
        ⚠️ This petition was rejected by both Instructor and Advisor. Your override carries executive authority and is final.
      </div>

      {issued && <div className={`${w.alert} ${w.alertGreen}`}>Final ruling issued: <strong>{ruling}</strong>. This action has been logged.</div>}

      <div className={w.split}>
        {/* LEFT — details + ruling history */}
        <div>
          <div className={w.cardDark} style={{ marginBottom: 16 }}>
            <div className={w.sectionTitle} style={{ color: 'rgba(255,255,255,0.6)' }}>Full Ruling History</div>
            <div className={w.timeline}>
              {RULING_HISTORY.map((t, i) => (
                <div key={i} className={w.tlItem}>
                  <div className={w.tlDot} style={{ background: t.color }} />
                  {i < RULING_HISTORY.length - 1 && <div className={w.tlLine} style={{ background: 'rgba(255,255,255,0.2)' }} />}
                  <div><div className={w.tlText} style={{ color: '#fff' }}>{t.text}</div><div className={w.tlActor} style={{ color: 'rgba(255,255,255,0.6)' }}>{t.actor}</div></div>
                </div>
              ))}
            </div>
          </div>

          <div className={w.card}>
            <div className={w.metaRow}><strong>{p.studentName}</strong> · {p.sid}<span>{p.course}</span></div>
            <div className={w.section}>
              <div className={w.sectionTitle}>Justification</div>
              <div className={w.quote}>{p.justification}</div>
            </div>
            <div className={w.section}>
              <div className={w.sectionTitle}>Student Snapshot</div>
              <div className={w.metaRow}>
                <StatusPill status={`GPA ${p.snapshot.gpa}`} variant="green" />
                <span>Credits <strong>{p.snapshot.credits}</strong></span>
                <StatusPill status={p.snapshot.standing} variant="green" />
              </div>
            </div>
          </div>
        </div>

        {/* RIGHT — chair decision */}
        <div className={w.panel} style={{ borderLeftColor: 'var(--color-yellow)' }}>
          <div className={w.panelLabel} style={{ color: 'var(--color-yellow)' }}>Chair Decision</div>

          <div className={w.field}>
            <span className={w.fieldLabel}>Ruling Type</span>
            <select className={w.select} value={ruling} onChange={(e) => setRuling(e.target.value)}>
              <option>Override & Approve</option>
              <option>Uphold Rejection</option>
              <option>Conditional Approval</option>
            </select>
          </div>

          {ruling === 'Conditional Approval' && (
            <div className={w.field}>
              <span className={w.fieldLabel}>Conditions</span>
              <textarea className={w.textarea} placeholder="State the conditions..." value={conditions} onChange={(e) => setConditions(e.target.value)} />
            </div>
          )}

          <div className={w.field}>
            <span className={w.fieldLabel}>Override Reason (required)</span>
            <textarea className={w.textarea} placeholder="Justification for the executive override..." value={reason} onChange={(e) => setReason(e.target.value)} />
          </div>

          <button className={`${w.btn} ${w.btnPrimary} ${w.btnFull}`} disabled={!reason.trim() || issued} onClick={() => setIssued(true)}>Issue Final Ruling</button>
          <p style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)', marginTop: 8, textAlign: 'center' }}>This action is logged and cannot be undone.</p>
        </div>
      </div>
    </AppShell>
  );
}
