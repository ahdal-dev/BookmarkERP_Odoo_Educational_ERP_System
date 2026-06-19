import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import StatusPill from '../../components/StatusPill/StatusPill';
import Stepper from '../../components/Stepper/Stepper';
import { admissionsOfficerNav } from '../../config/navConfigs';
import w from '../_shared/workflow.module.css';

/* Admission Officer — detailed application review with decision actions. */

const STEPS = [
  { label: 'Submitted', status: 'completed' },
  { label: 'OCR Processing', status: 'completed' },
  { label: 'Under Review', status: 'active' },
  { label: 'Decision', status: 'future' },
];

const OCR = [
  { label: 'Full Name', value: 'Julianne Abernathy' },
  { label: 'GPA', value: '3.81 / 4.00' },
  { label: 'Institution', value: 'Cairo University' },
  { label: 'Degree', value: 'B.Sc. Civil Engineering' },
];

export default function ApplicationReviewPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [notes, setNotes] = useState('');
  const [decision, setDecision] = useState(null);
  const [rejectReason, setRejectReason] = useState('');

  return (
    <AppShell navItems={admissionsOfficerNav} logoVariant="stacked" sidebarLabel="ADMISSIONS">
      <div className={w.breadcrumb}>
        <span onClick={() => navigate('/admissions/officer')} style={{ cursor: 'pointer' }}>Admissions</span> › Pipeline › {id || 'ADM-2024-0012'} — Julianne Abernathy
      </div>
      <PageHeader title="Julianne Abernathy" useBrandFont badge="M.S. Architecture" badgeVariant="green" />

      {decision && (
        <div className={`${w.alert} ${decision === 'accept' ? w.alertGreen : w.alertCoral}`}>
          Application {decision === 'accept' ? 'accepted' : decision === 'reject' ? 'rejected' : 'returned for more documents'}.
        </div>
      )}

      <div className={w.split}>
        {/* LEFT */}
        <div>
          <div className={w.card} style={{ marginBottom: 16 }}>
            <div className={w.sectionTitle}>Applicant Info</div>
            <div className={w.metaRow}>
              <span>DOB <strong>1999-04-12</strong></span><span>Nationality <strong>Egyptian</strong></span>
            </div>
            <div className={w.metaRow}>
              <span>Email <strong>julianne.a@example.com</strong></span><span>Phone <strong>+20 100 555 1234</strong></span>
            </div>
          </div>

          <div className={w.card} style={{ marginBottom: 16 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
              <div className={w.sectionTitle} style={{ margin: 0 }}>OCR Extracted Data</div>
              <StatusPill status="OCR Verified" variant="green" />
            </div>
            <div className={w.cardGrid2}>
              {OCR.map((f) => (
                <div key={f.label} style={{ border: '1.5px solid var(--color-lime)', borderRadius: 10, padding: '10px 12px', background: 'rgba(76,175,39,0.05)' }}>
                  <div style={{ fontSize: '0.66rem', textTransform: 'uppercase', letterSpacing: '0.04em', color: 'var(--color-text-muted)', fontWeight: 700 }}>{f.label}</div>
                  <div style={{ fontWeight: 700 }}>{f.value}</div>
                </div>
              ))}
            </div>
          </div>

          <div className={w.card}>
            <div className={w.sectionTitle}>Documents</div>
            {['official_transcript.pdf', 'national_id.pdf', 'statement_of_purpose.pdf'].map((d) => (
              <div key={d} style={{ display: 'flex', alignItems: 'center', gap: 10, border: '1px solid var(--color-border-light)', borderRadius: 10, padding: 10, marginBottom: 8 }}>
                <span style={{ background: 'var(--color-coral)', color: '#fff', fontSize: '0.62rem', fontWeight: 700, padding: '2px 6px', borderRadius: 4 }}>PDF</span>
                <span style={{ flex: 1, fontSize: '0.85rem' }}>{d}</span>
                <StatusPill status="Verified" variant="green" />
                <span className={w.cardLink}>Download</span>
              </div>
            ))}
          </div>
        </div>

        {/* RIGHT */}
        <div>
          <div className={w.card} style={{ marginBottom: 16 }}>
            <div className={w.sectionTitle}>Application Timeline</div>
            <Stepper steps={STEPS} />
          </div>

          <div className={w.panel}>
            <div className={w.panelLabel}>Decision</div>
            <div className={w.field}>
              <span className={w.fieldLabel}>Internal Notes</span>
              <textarea className={w.textarea} placeholder="Add internal notes..." value={notes} onChange={(e) => setNotes(e.target.value)} />
            </div>
            {decision === 'reject' && (
              <div className={w.field}>
                <span className={w.fieldLabel}>Rejection Reason (required)</span>
                <select className={w.select} value={rejectReason} onChange={(e) => setRejectReason(e.target.value)}>
                  <option value="">Select a reason…</option>
                  <option>Below GPA threshold</option>
                  <option>Incomplete documentation</option>
                  <option>Program capacity reached</option>
                </select>
              </div>
            )}
            <div className={w.btnRow}>
              <button className={`${w.btn} ${w.btnPrimary} ${w.btnFull}`} onClick={() => setDecision('accept')}>✓ Accept Application</button>
              <button className={`${w.btn} ${w.btnOutline} ${w.btnFull}`} onClick={() => setDecision('docs')}>↻ Request More Documents</button>
              <button className={`${w.btn} ${w.btnDanger} ${w.btnFull}`} onClick={() => setDecision('reject')}>✕ Reject Application</button>
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
