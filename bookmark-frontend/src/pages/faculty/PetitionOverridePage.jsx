import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import StatusPill from '../../components/StatusPill/StatusPill';
import { chairNav } from '../../config/navConfigs';
import { facultyAPI, petitionsAPI } from '../../api/apiGateway';
import useAsync from '../../hooks/useAsync';
import w from '../_shared/workflow.module.css';

/* Department Chair — override screen (final authority), live + persisted. */

export default function PetitionOverridePage() {
  const { id } = useParams();
  const pid = Number(id);
  const navigate = useNavigate();

  const { data, loading } = useAsync(
    () => facultyAPI.getPetitionQueue({ states: 'submitted,under_review,approved,rejected' }), []);
  const p = (data?.petitions || []).find((x) => x.id === pid);

  const [ruling, setRuling] = useState('Override & Approve');
  const [reason, setReason] = useState('');
  const [issued, setIssued] = useState(false);
  const [busy, setBusy] = useState(false);

  const issue = async () => {
    setBusy(true);
    try {
      const decision = ruling === 'Uphold Rejection' ? 'reject' : 'approve';
      await petitionsAPI.override(pid, decision, reason);
      setIssued(true);
    } finally {
      setBusy(false);
    }
  };

  return (
    <AppShell navItems={chairNav} logoVariant="stacked" sidebarLabel="DEPARTMENT CHAIR">
      <div className={w.breadcrumb}>
        <span onClick={() => navigate('/faculty/chair/petitions')} style={{ cursor: 'pointer' }}>Chair Panel</span> › Override › #{id}
      </div>
      <PageHeader title={`${p?.name || 'Petition'} — Override`} useBrandFont />

      <div className={`${w.alert} ${w.alertCoral}`}>
        ⚠️ Your override carries executive authority and is final.
      </div>

      {issued && <div className={`${w.alert} ${w.alertGreen}`}>Final ruling issued: <strong>{ruling}</strong>. This action has been logged. <span className={w.cardLink} onClick={() => navigate('/faculty/chair/petitions')}>Back to board →</span></div>}

      {loading ? <div className={w.card}><div className={w.empty}>Loading…</div></div> : (
        <div className={w.split}>
          <div className={w.card}>
            <div className={w.metaRow}><strong>{p?.student_id?.name || 'Student'}</strong>{p?.course_id && <span>{p.course_id.name}</span>}</div>
            <div className={w.section}>
              <div className={w.sectionTitle}>Subject</div>
              <div className={w.quote}>{p?.subject || '—'}</div>
            </div>
            <div className={w.metaRow}>
              <StatusPill status={p?.petition_type_id?.name || 'Petition'} variant="yellow" />
              <StatusPill status={p?.state || '—'} variant="coral" />
            </div>
          </div>

          <div className={w.panel} style={{ borderLeftColor: 'var(--color-yellow)' }}>
            <div className={w.panelLabel} style={{ color: 'var(--color-yellow)' }}>Chair Decision</div>
            <div className={w.field}>
              <span className={w.fieldLabel}>Ruling Type</span>
              <select className={w.select} value={ruling} onChange={(e) => setRuling(e.target.value)}>
                <option>Override &amp; Approve</option>
                <option>Uphold Rejection</option>
              </select>
            </div>
            <div className={w.field}>
              <span className={w.fieldLabel}>Override Reason (required)</span>
              <textarea className={w.textarea} placeholder="Justification for the executive override..." value={reason} onChange={(e) => setReason(e.target.value)} />
            </div>
            <button className={`${w.btn} ${w.btnPrimary} ${w.btnFull}`} disabled={!reason.trim() || issued || busy} onClick={issue}>Issue Final Ruling</button>
            <p style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)', marginTop: 8, textAlign: 'center' }}>This action is logged and cannot be undone.</p>
          </div>
        </div>
      )}
    </AppShell>
  );
}
