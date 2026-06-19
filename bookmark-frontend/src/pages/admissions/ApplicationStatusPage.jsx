import { useState } from 'react';
import PublicShell from '../../components/PublicShell/PublicShell';
import StatusPill from '../../components/StatusPill/StatusPill';
import Stepper from '../../components/Stepper/Stepper';
import w from '../_shared/workflow.module.css';

/* Public reference-number application status tracker. */

const STEPS = [
  { label: 'Submitted', status: 'completed' },
  { label: 'OCR Verified', status: 'completed' },
  { label: 'Under Review', status: 'active' },
  { label: 'Decision', status: 'future' },
];

export default function ApplicationStatusPage() {
  const [ref, setRef] = useState('');
  const [result, setResult] = useState(null);

  const track = () => {
    if (!ref.trim()) return;
    setResult({ ref: ref.trim().toUpperCase(), name: 'Julianne Abernathy', program: 'M.S. Architecture', status: 'Under Review', updated: 'Oct 16, 2026 · 14:20' });
  };

  return (
    <PublicShell active="Track Application">
      <div style={{ maxWidth: 600, margin: '0 auto' }}>
        <h1 style={{ fontWeight: 800, fontSize: '1.8rem', textAlign: 'center', marginBottom: 8 }}>Track Your Application</h1>
        <p style={{ textAlign: 'center', color: 'var(--color-text-muted)', marginBottom: 24 }}>Enter your reference number to see your admission status.</p>

        <div className={w.card} style={{ marginBottom: 20 }}>
          <div style={{ display: 'flex', gap: 10 }}>
            <input className={w.search} placeholder="e.g. ADM-2024-0012" value={ref} onChange={(e) => setRef(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && track()} />
            <button className={`${w.btn} ${w.btnPrimary}`} onClick={track}>Track</button>
          </div>
        </div>

        {result && (
          <div className={`${w.card} ${w.cardAccent}`}>
            <div className={w.metaRow}>
              <StatusPill status={result.ref} variant="black" />
              <span><strong>{result.name}</strong></span>
              <StatusPill status={result.program} variant="green" />
            </div>
            <div style={{ textAlign: 'center', margin: '16px 0' }}>
              <StatusPill status={result.status} variant="yellow" />
            </div>
            <Stepper steps={STEPS} />
            <p style={{ textAlign: 'center', fontSize: '0.75rem', color: 'var(--color-text-muted)', marginTop: 16 }}>Last updated: {result.updated}</p>
          </div>
        )}
      </div>
    </PublicShell>
  );
}
