import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import StatusPill from '../../components/StatusPill/StatusPill';
import { facultyNav } from '../../config/navConfigs';
import { useAuth } from '../../context/AuthContext';
import { facultyAPI, petitionsAPI } from '../../api/apiGateway';
import useAsync from '../../hooks/useAsync';
import w from '../_shared/workflow.module.css';

/* Single petition detail + decision (Instructor / Advisor / Chair), live + persisted. */

export default function PetitionReviewPage() {
  const { id } = useParams();
  const pid = Number(id);
  const navigate = useNavigate();
  const { user } = useAuth();
  const isChair = user?.role === 'department_chair';

  const { data, loading, error } = useAsync(() => facultyAPI.getPetitionQueue({ states: 'submitted,under_review' }), []);
  const p = (data?.petitions || []).find((x) => x.id === pid);

  const [comments, setComments] = useState('');
  const [decision, setDecision] = useState(null);
  const [busy, setBusy] = useState(false);

  const act = async (action) => {
    setBusy(true);
    try {
      await petitionsAPI.facultyAction(pid, action, comments);
      setDecision(action);
    } finally {
      setBusy(false);
    }
  };

  return (
    <AppShell navItems={facultyNav} logoVariant="stacked" sidebarLabel="FACULTY">
      <div className={w.breadcrumb}>
        <span onClick={() => navigate('/faculty/petitions')} style={{ cursor: 'pointer' }}>Petitions</span> › #{id}
      </div>

      {loading ? <div className={w.card}><div className={w.empty}>Loading petition…</div></div>
      : error ? <div className={w.card}><div className={w.empty}><div className={w.emptyTitle}>Couldn't load petition</div><p>{error}</p></div></div>
      : !p ? <div className={w.card}><div className={w.empty}><div className={w.emptyTitle}>Petition not in your queue</div><p>It may have already been decided or escalated.</p><button className={`${w.btn} ${w.btnOutline} ${w.btnSm}`} onClick={() => navigate('/faculty/petitions')}>Back to queue</button></div></div>
      : (
        <>
          <PageHeader title={`${p.name} — ${p.petition_type_id?.name || 'Petition'}`} useBrandFont />

          {decision && (
            <div className={`${w.alert} ${decision === 'approve' ? w.alertGreen : w.alertCoral}`}>
              Decision recorded: petition {p.name} was {decision === 'approve' ? 'approved' : decision === 'reject' ? 'rejected' : 'escalated'} at your tier.{' '}
              <span className={w.cardLink} onClick={() => navigate('/faculty/petitions')}>Back to queue →</span>
            </div>
          )}

          <div className={w.split}>
            <div className={`${w.card}`}>
              <div className={w.metaRow}>
                <StatusPill status={p.petition_type_id?.name || 'Petition'} variant="yellow" />
                <span>Tier: <strong>{p.current_tier}</strong></span>
                <span>{p.submitted_date}</span>
              </div>
              <div className={w.metaRow}>
                <span><strong>{p.student_id?.name || 'Student'}</strong></span>
                {p.department_id && <span>{p.department_id.name}</span>}
                {p.course_id && <span>{p.course_id.name}</span>}
              </div>
              <div className={w.section}>
                <div className={w.sectionTitle}>Subject</div>
                <div className={w.quote}>{p.subject || '—'}</div>
              </div>
            </div>

            <div className={w.panel}>
              <div className={w.panelLabel}>Your Decision</div>
              <textarea className={w.textarea} placeholder="Add comments or reason..." value={comments} onChange={(e) => setComments(e.target.value)} style={{ marginBottom: 12 }} />
              <div className={w.btnRow}>
                <button className={`${w.btn} ${w.btnPrimary} ${w.btnFull}`} disabled={busy || !!decision} onClick={() => act('approve')}>Approve</button>
                <button className={`${w.btn} ${w.btnDanger} ${w.btnFull}`} disabled={busy || !!decision} onClick={() => act('reject')}>Reject</button>
                {isChair
                  ? <button className={`${w.btn} ${w.btnOutline} ${w.btnFull}`} onClick={() => navigate(`/faculty/chair/petitions/${p.id}`)}>Override Previous Decision</button>
                  : <button className={`${w.btn} ${w.btnOutline} ${w.btnFull}`} disabled={busy || !!decision} onClick={() => act('escalate')}>Escalate to Chair</button>}
              </div>
            </div>
          </div>
        </>
      )}
    </AppShell>
  );
}
