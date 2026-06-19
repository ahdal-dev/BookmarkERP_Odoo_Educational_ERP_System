import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import StatusPill from '../../components/StatusPill/StatusPill';
import { studentNav } from '../../config/navConfigs';
import { petitionsAPI } from '../../api/apiGateway';
import useAsync from '../../hooks/useAsync';
import w from '../_shared/workflow.module.css';

/* Student petition history — live list of submitted requests. */

const STATE_LABEL = { draft: 'Draft', submitted: 'Pending', under_review: 'Pending', approved: 'Approved', rejected: 'Denied', cancelled: 'Cancelled' };
const STATE_VARIANT = { Pending: 'yellow', Approved: 'green', Denied: 'coral', Draft: 'black', Cancelled: 'black' };
const FILTERS = ['All', 'Pending', 'Approved', 'Denied'];

export default function PetitionListPage() {
  const navigate = useNavigate();
  const { data, loading, error, reload } = useAsync(() => petitionsAPI.getMyPetitions(), []);
  const petitions = (data?.petitions || []).map((p) => ({ ...p, label: STATE_LABEL[p.state] || p.state }));
  const [filter, setFilter] = useState('All');

  const rows = petitions.filter((p) => filter === 'All' || p.label === filter);

  return (
    <AppShell navItems={studentNav} logoVariant="stacked" sidebarLabel="STUDENT PORTAL">
      <PageHeader
        title="My Petitions" subtitle="Track all submitted academic requests" useBrandFont
        actions={<button className={`${w.btn} ${w.btnPrimary}`} onClick={() => navigate('/petitions/new')}>+ New Petition</button>}
      />

      <div className={w.filterTabs} style={{ marginBottom: 18 }}>
        {FILTERS.map((f) => (
          <button key={f} className={`${w.filterTab} ${filter === f ? w.filterTabActive : ''}`} onClick={() => setFilter(f)}>{f}</button>
        ))}
      </div>

      {loading ? (
        <div className={`${w.card} ${w.empty}`}>Loading petitions…</div>
      ) : error ? (
        <div className={`${w.card} ${w.empty}`}><div className={w.emptyTitle}>Couldn't load petitions</div><p>{error}</p><button className={`${w.btn} ${w.btnOutline} ${w.btnSm}`} onClick={reload}>Retry</button></div>
      ) : rows.length === 0 ? (
        <div className={`${w.card} ${w.empty}`}>
          <div className={w.emptyTitle}>No petitions yet</div>
          <p>Submit one if you hit a registration block or need an academic exception.</p>
          <button className={`${w.btn} ${w.btnPrimary}`} style={{ marginTop: 16 }} onClick={() => navigate('/petitions/new')}>+ New Petition</button>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {rows.map((p) => (
            <div key={p.id} className={w.card} style={{ display: 'flex', alignItems: 'center', gap: 20, padding: 18 }}>
              <div style={{ minWidth: 150 }}>
                <div style={{ fontWeight: 800 }}>{p.ref}</div>
                <StatusPill status={p.type} variant="yellow" />
                <div style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)', marginTop: 6 }}>{p.date}</div>
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600, fontSize: '0.88rem' }}>{p.subject}</div>
                <div style={{ fontSize: '0.82rem', color: 'var(--color-text-secondary)' }}>Tier: {p.tier} · {p.days_pending} day(s) pending</div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <StatusPill status={p.label} variant={STATE_VARIANT[p.label] || 'yellow'} />
              </div>
            </div>
          ))}
        </div>
      )}
    </AppShell>
  );
}
