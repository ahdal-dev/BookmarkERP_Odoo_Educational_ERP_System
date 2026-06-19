import { useState } from 'react';
import PublicShell from '../../components/PublicShell/PublicShell';
import StatusPill from '../../components/StatusPill/StatusPill';
import Stepper from '../../components/Stepper/Stepper';
import { admissionsAPI } from '../../api/apiGateway';
import w from '../_shared/workflow.module.css';

/* Public reference-number application status tracker (live). */

const STAGE_ORDER = ['submitted', 'under_review', 'accepted', 'rejected'];
function stepsFor(state) {
  const idx = STAGE_ORDER.indexOf(state);
  const base = [
    { label: 'Submitted', key: 'submitted' },
    { label: 'Under Review', key: 'under_review' },
    { label: 'Decision', key: 'accepted' },
  ];
  return base.map((s, i) => ({
    label: s.label,
    status: i < idx ? 'completed' : i === idx ? 'active' : (state === 'accepted' || state === 'rejected') && i === 2 ? 'completed' : 'future',
  }));
}

export default function ApplicationStatusPage() {
  const [ref, setRef] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const track = async () => {
    if (!ref.trim()) return;
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const data = await admissionsAPI.getStatus(ref.trim());
      const rec = Array.isArray(data) ? data[0] : (data?.applications ? data.applications[0] : data);
      if (!rec) { setError('No application found for that reference.'); return; }
      setResult(rec);
    } catch {
      setError('No application found for that reference.');
    } finally {
      setLoading(false);
    }
  };

  const state = result?.state || result?.status;

  return (
    <PublicShell active="Track Application">
      <div style={{ maxWidth: 600, margin: '0 auto' }}>
        <h1 style={{ fontWeight: 800, fontSize: '1.8rem', textAlign: 'center', marginBottom: 8 }}>Track Your Application</h1>
        <p style={{ textAlign: 'center', color: 'var(--color-text-muted)', marginBottom: 24 }}>Enter your reference number to see your admission status.</p>

        <div className={w.card} style={{ marginBottom: 20 }}>
          <div style={{ display: 'flex', gap: 10 }}>
            <input className={w.search} placeholder="e.g. ADM-2024-0012" value={ref} onChange={(e) => setRef(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && track()} />
            <button className={`${w.btn} ${w.btnPrimary}`} onClick={track} disabled={loading}>{loading ? 'Tracking…' : 'Track'}</button>
          </div>
          {error && <p style={{ color: 'var(--color-coral)', fontSize: '0.85rem', marginTop: 10 }}>{error}</p>}
        </div>

        {result && (
          <div className={`${w.card} ${w.cardAccent}`}>
            <div className={w.metaRow}>
              <StatusPill status={result.reference || result.ref || ref.toUpperCase()} variant="black" />
              <span><strong>{result.name || result.full_name || 'Applicant'}</strong></span>
              {result.program_id && <StatusPill status={Array.isArray(result.program_id) ? result.program_id[1] : result.program_id} variant="green" />}
            </div>
            <div style={{ textAlign: 'center', margin: '16px 0' }}>
              <StatusPill status={state} variant={state === 'accepted' ? 'green' : state === 'rejected' ? 'coral' : 'yellow'} />
            </div>
            <Stepper steps={stepsFor(state)} />
          </div>
        )}
      </div>
    </PublicShell>
  );
}
