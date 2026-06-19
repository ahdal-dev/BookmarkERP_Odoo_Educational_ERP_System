import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import StatusPill from '../../components/StatusPill/StatusPill';
import Stepper from '../../components/Stepper/Stepper';
import { facultyNav } from '../../config/navConfigs';
import { useAuth } from '../../context/AuthContext';
import { facultyPetitions, URGENCY_VARIANT } from '../../mocks/facultyMocks';
import w from '../_shared/workflow.module.css';

/* Single petition detail + decision. Shared by Instructor / Advisor / Chair —
   only the decision panel differs (Chair gets the Override action). */

const STEPS = [
  { label: 'Submitted', status: 'completed' },
  { label: 'Instructor Review', status: 'active' },
  { label: 'Advisor Review', status: 'future' },
  { label: 'Decision', status: 'future' },
];

export default function PetitionReviewPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const isChair = user?.role === 'department_chair';

  const p = facultyPetitions.find((x) => x.id === id) || facultyPetitions[0];
  const [comments, setComments] = useState('');
  const [decision, setDecision] = useState(null);

  return (
    <AppShell navItems={facultyNav} logoVariant="stacked" sidebarLabel="FACULTY">
      <div className={w.breadcrumb}>
        <span onClick={() => navigate('/faculty/petitions')} style={{ cursor: 'pointer' }}>Petitions</span> › {p.ref} — {p.type}
      </div>
      <PageHeader title={`${p.ref} — ${p.type}`} useBrandFont />

      {decision && (
        <div className={`${w.alert} ${decision === 'approve' ? w.alertGreen : w.alertCoral}`}>
          Decision recorded: petition {p.ref} was {decision === 'approve' ? 'approved' : 'rejected'} at your tier.
        </div>
      )}

      <div className={w.split}>
        {/* LEFT */}
        <div>
          <div className={`${w.card}`} style={{ marginBottom: 16 }}>
            <div className={w.metaRow}>
              <StatusPill status={p.type} variant="yellow" />
              <StatusPill status={p.urgency} variant={URGENCY_VARIANT[p.urgency]} />
              <span>{p.date}</span>
            </div>
            <div className={w.metaRow}>
              <span><strong>{p.studentName}</strong> · {p.sid}</span>
              <span>{p.department}</span>
              <span>{p.course}</span>
            </div>

            <div className={w.section}>
              <div className={w.sectionTitle}>Justification</div>
              <div className={w.quote}>{p.justification}</div>
            </div>

            <div className={w.section}>
              <div className={w.sectionTitle}>Supporting Documents</div>
              {p.documents.length === 0 ? <p style={{ fontSize: '0.82rem', color: 'var(--color-text-muted)' }}>No documents attached.</p> : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {p.documents.map((d) => (
                    <div key={d.name} style={{ display: 'flex', alignItems: 'center', gap: 10, border: '1px solid var(--color-border-light)', borderRadius: 10, padding: 10 }}>
                      <span style={{ background: 'var(--color-coral)', color: '#fff', fontSize: '0.62rem', fontWeight: 700, padding: '2px 6px', borderRadius: 4 }}>PDF</span>
                      <span style={{ flex: 1, fontSize: '0.85rem' }}>{d.name}</span>
                      <span className={w.cardLink}>Download</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className={w.section}>
              <div className={w.sectionTitle}>Audit Trail</div>
              <div className={w.timeline}>
                {p.trail.map((t, i) => (
                  <div key={i} className={w.tlItem}>
                    <div className={w.tlDot} style={{ background: t.color }} />
                    {i < p.trail.length - 1 && <div className={w.tlLine} />}
                    <div><div className={w.tlText}>{t.text}</div><div className={w.tlActor}>{t.actor}</div></div>
                  </div>
                ))}
              </div>
            </div>
          </div>
          <Stepper steps={STEPS} />
        </div>

        {/* RIGHT */}
        <div>
          <div className={w.card} style={{ marginBottom: 16 }}>
            <div className={w.sectionTitle}>Student Academic Snapshot</div>
            <div className={w.metaRow}>
              <StatusPill status={`GPA ${p.snapshot.gpa}`} variant="green" />
              <span>Credits <strong>{p.snapshot.credits}</strong></span>
            </div>
            <StatusPill status={p.snapshot.standing} variant="green" />
            <div style={{ marginTop: 12 }}><span className={w.cardLink}>View Full Transcript →</span></div>
          </div>

          <div className={w.panel}>
            <div className={w.panelLabel}>Your Decision</div>
            <textarea className={w.textarea} placeholder="Add comments or reason..." value={comments} onChange={(e) => setComments(e.target.value)} style={{ marginBottom: 12 }} />
            <div className={w.btnRow}>
              <button className={`${w.btn} ${w.btnPrimary} ${w.btnFull}`} onClick={() => setDecision('approve')}>Approve</button>
              <button className={`${w.btn} ${w.btnDanger} ${w.btnFull}`} onClick={() => setDecision('reject')}>Reject</button>
              {isChair && (
                <button className={`${w.btn} ${w.btnOutline} ${w.btnFull}`} onClick={() => navigate(`/faculty/chair/petitions/${p.id}`)}>Override Previous Decision</button>
              )}
            </div>
            {!isChair && (
              <div style={{ textAlign: 'center', marginTop: 12 }}>
                <span className={w.cardLink}>Escalate to Department Chair →</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
