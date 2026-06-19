import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import DataTable from '../../components/DataTable/DataTable';
import StatusPill from '../../components/StatusPill/StatusPill';
import { facultyNav } from '../../config/navConfigs';
import { facultyAPI, petitionsAPI } from '../../api/apiGateway';
import useAsync from '../../hooks/useAsync';
import w from '../_shared/workflow.module.css';

/* Petition review queue (Instructor / Advisor / Chair) — live + persisted actions. */

const URGENCY_VARIANT = { High: 'coral', Medium: 'yellow', Low: 'green' };
function urgencyOf(d) { return (d ?? 0) > 7 ? 'High' : (d ?? 0) >= 3 ? 'Medium' : 'Low'; }

function mapPetition(p) {
  return {
    id: p.id,
    ref: p.name,
    studentName: p.student_id?.name || 'Student',
    type: p.petition_type_id?.name || p.subject || 'Petition',
    subject: p.subject,
    date: p.submitted_date || '',
    tier: p.current_tier,
    urgency: urgencyOf(p.days_pending),
  };
}

export default function FacultyPetitionQueuePage() {
  const navigate = useNavigate();
  const { data, loading, error, reload } = useAsync(() => facultyAPI.getPetitionQueue(), []);
  const petitions = (data?.petitions || []).map(mapPetition);
  const [selected, setSelected] = useState(null);
  const [busy, setBusy] = useState(false);

  const act = async (action) => {
    if (!selected) return;
    setBusy(true);
    try {
      await petitionsAPI.facultyAction(selected.id, action);
      setSelected(null);
      await reload();
    } finally {
      setBusy(false);
    }
  };

  const columns = [
    { key: 'ref', header: 'REF', sortable: true, render: (v) => <strong>{v}</strong> },
    { key: 'studentName', header: 'Student', sortable: true },
    { key: 'type', header: 'Petition Type', render: (v) => <StatusPill status={v} variant="yellow" /> },
    { key: 'date', header: 'Submission', sortable: true },
    { key: 'urgency', header: 'Urgency', render: (v) => <StatusPill status={v} variant={URGENCY_VARIANT[v]} /> },
    { key: 'action', header: 'Action', render: (_, r) => <button className={`${w.btn} ${w.btnPrimary} ${w.btnSm}`} onClick={(e) => { e.stopPropagation(); navigate(`/faculty/petitions/${r.id}`); }}>Review →</button> },
  ];

  return (
    <AppShell navItems={facultyNav} logoVariant="stacked" sidebarLabel="FACULTY">
      <PageHeader title="Petition Queue" subtitle={`Petitions requiring your review · ${petitions.length} pending`} useBrandFont />

      {loading ? (
        <div className={w.card}><div className={w.empty}>Loading petitions…</div></div>
      ) : error ? (
        <div className={w.card}><div className={w.empty}><div className={w.emptyTitle}>Couldn't load the queue</div><p>{error}</p><button className={`${w.btn} ${w.btnOutline} ${w.btnSm}`} onClick={reload}>Retry</button></div></div>
      ) : petitions.length === 0 ? (
        <div className={w.card}><div className={w.empty}><div className={w.emptyTitle}>Queue clear</div><p>No petitions awaiting your review.</p></div></div>
      ) : (
        <div className={w.split}>
          <div className={w.card} style={{ padding: 0 }}>
            <DataTable columns={columns} data={petitions} onRowClick={setSelected} rowAccentColor={(r) => `var(--color-${URGENCY_VARIANT[r.urgency]})`} />
          </div>

          {selected && (
            <aside className={w.sidePanel}>
              <StatusPill status={`PETITION ${selected.ref}`} variant="coral" />
              <h3 className={w.cardTitle} style={{ marginTop: 12 }}>{selected.type}</h3>
              <div className={w.metaRow}><span>{selected.studentName}</span><span>Tier: {selected.tier}</span></div>

              <div className={w.section}>
                <div className={w.sectionTitle}>Subject</div>
                <div className={w.quote}>{selected.subject || '—'}</div>
              </div>

              <div className={w.btnRow}>
                <button className={`${w.btn} ${w.btnGreen}`} disabled={busy} onClick={() => act('approve')}>✓ Approve</button>
                <button className={`${w.btn} ${w.btnDanger}`} disabled={busy} onClick={() => act('reject')}>✕ Reject</button>
                <button className={`${w.btn} ${w.btnOutline}`} onClick={() => navigate(`/faculty/petitions/${selected.id}`)}>Open full review →</button>
              </div>
            </aside>
          )}
        </div>
      )}
    </AppShell>
  );
}
