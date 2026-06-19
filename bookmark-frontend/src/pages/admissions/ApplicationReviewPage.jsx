import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import StatusPill from '../../components/StatusPill/StatusPill';
import Stepper from '../../components/Stepper/Stepper';
import { admissionsOfficerNav } from '../../config/navConfigs';
import { admissionsAPI } from '../../api/apiGateway';
import useAsync from '../../hooks/useAsync';
import w from '../_shared/workflow.module.css';

/* Admission Officer — detailed application review with decision actions (live). */

const STAGE_ORDER = ['submitted', 'under_review', 'accepted', 'rejected'];
function stepsFor(state) {
  const idx = STAGE_ORDER.indexOf(state);
  return [
    { label: 'Submitted', status: idx > 0 ? 'completed' : 'active' },
    { label: 'Under Review', status: idx > 1 ? 'completed' : idx === 1 ? 'active' : 'future' },
    { label: 'Decision', status: (state === 'accepted' || state === 'rejected') ? 'completed' : 'future' },
  ];
}

export default function ApplicationReviewPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { data, loading, error, reload } = useAsync(() => admissionsAPI.getDetail(Number(id)), [id]);

  const [notes, setNotes] = useState('');
  const [busy, setBusy] = useState(false);
  const [decision, setDecision] = useState(null);

  const decide = async (stage, label) => {
    setBusy(true);
    try {
      await admissionsAPI.updateStage(Number(id), stage);
      setDecision(label);
      await reload();
    } finally {
      setBusy(false);
    }
  };

  const program = data?.program_id?.name || (Array.isArray(data?.program_id) ? data.program_id[1] : '');
  const fields = data ? [
    { label: 'Email', value: data.email },
    { label: 'Phone', value: data.phone },
    { label: 'National ID', value: data.national_id },
    { label: 'GPA', value: data.gpa },
    { label: 'Previous School', value: data.previous_school },
    { label: 'Reference', value: data.reference },
  ] : [];

  return (
    <AppShell navItems={admissionsOfficerNav} logoVariant="stacked" sidebarLabel="ADMISSIONS">
      <div className={w.breadcrumb}>
        <span onClick={() => navigate('/admissions/officer')} style={{ cursor: 'pointer' }}>Admissions</span> › Pipeline › #{id}
      </div>

      {loading ? <div className={w.card}><div className={w.empty}>Loading application…</div></div>
      : error || !data ? <div className={w.card}><div className={w.empty}><div className={w.emptyTitle}>Couldn't load application</div><p>{error || 'Not found.'}</p><button className={`${w.btn} ${w.btnOutline} ${w.btnSm}`} onClick={() => navigate('/admissions/officer')}>Back</button></div></div>
      : (
        <>
          <PageHeader title={data.name || 'Applicant'} useBrandFont badge={program || 'Program'} badgeVariant="green" />

          {decision && <div className={`${w.alert} ${decision === 'Accepted' ? w.alertGreen : w.alertCoral}`}>Application {decision.toLowerCase()}.</div>}

          <div className={w.split}>
            <div>
              <div className={w.card} style={{ marginBottom: 16 }}>
                <div className={w.sectionTitle}>Applicant Information</div>
                <div className={w.cardGrid2}>
                  {fields.map((f) => (
                    <div key={f.label} style={{ border: '1px solid var(--color-border-light)', borderRadius: 10, padding: '10px 12px' }}>
                      <div style={{ fontSize: '0.66rem', textTransform: 'uppercase', letterSpacing: '0.04em', color: 'var(--color-text-muted)', fontWeight: 700 }}>{f.label}</div>
                      <div style={{ fontWeight: 700 }}>{f.value || '—'}</div>
                    </div>
                  ))}
                </div>
              </div>

              <div className={w.card}>
                <div className={w.sectionTitle}>Documents</div>
                {data.transcript_filename ? (
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10, border: '1px solid var(--color-border-light)', borderRadius: 10, padding: 10 }}>
                    <span style={{ background: 'var(--color-coral)', color: '#fff', fontSize: '0.62rem', fontWeight: 700, padding: '2px 6px', borderRadius: 4 }}>DOC</span>
                    <span style={{ flex: 1, fontSize: '0.85rem' }}>{data.transcript_filename}</span>
                    <StatusPill status="Uploaded" variant="green" />
                  </div>
                ) : <p style={{ fontSize: '0.82rem', color: 'var(--color-text-muted)' }}>No documents uploaded.</p>}
              </div>
            </div>

            <div>
              <div className={w.card} style={{ marginBottom: 16 }}>
                <div className={w.sectionTitle}>Application Timeline</div>
                <Stepper steps={stepsFor(data.state)} />
              </div>

              <div className={w.panel}>
                <div className={w.panelLabel}>Decision</div>
                <div className={w.field}>
                  <span className={w.fieldLabel}>Internal Notes</span>
                  <textarea className={w.textarea} placeholder="Add internal notes..." value={notes} onChange={(e) => setNotes(e.target.value)} />
                </div>
                <div className={w.btnRow}>
                  <button className={`${w.btn} ${w.btnPrimary} ${w.btnFull}`} disabled={busy} onClick={() => decide('accepted', 'Accepted')}>✓ Accept Application</button>
                  <button className={`${w.btn} ${w.btnOutline} ${w.btnFull}`} disabled={busy} onClick={() => decide('under_review', 'Returned for review')}>↻ Mark Under Review</button>
                  <button className={`${w.btn} ${w.btnDanger} ${w.btnFull}`} disabled={busy} onClick={() => decide('rejected', 'Rejected')}>✕ Reject Application</button>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </AppShell>
  );
}
