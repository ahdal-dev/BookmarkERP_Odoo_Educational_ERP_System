import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import DataTable from '../../components/DataTable/DataTable';
import StatusPill from '../../components/StatusPill/StatusPill';
import { facultyNav } from '../../config/navConfigs';
import { facultyPetitions, URGENCY_VARIANT } from '../../mocks/facultyMocks';
import w from '../_shared/workflow.module.css';

/* Petition review queue (shared by Instructor & Advisor; data scope differs). */

const TYPES = ['All', 'Prereq Override', 'Course Overload', 'Late Drop', 'Grade Appeal'];

export default function FacultyPetitionQueuePage() {
  const navigate = useNavigate();
  const [type, setType] = useState('All');
  const [selected, setSelected] = useState(facultyPetitions[0]);

  const rows = facultyPetitions.filter((p) => type === 'All' || p.type === type);

  const columns = [
    { key: 'ref', header: 'REF', sortable: true, render: (v) => <strong>{v}</strong> },
    { key: 'studentName', header: 'Student', sortable: true, render: (v, r) => <span>{v}<br /><span style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)' }}>{r.sid}</span></span> },
    { key: 'type', header: 'Petition Type', render: (v) => <StatusPill status={v} variant="yellow" /> },
    { key: 'date', header: 'Submission', sortable: true },
    { key: 'urgency', header: 'Urgency', render: (v) => <StatusPill status={v} variant={URGENCY_VARIANT[v]} /> },
    { key: 'action', header: 'Action', render: (_, r) => <button className={`${w.btn} ${w.btnPrimary} ${w.btnSm}`} onClick={(e) => { e.stopPropagation(); navigate(`/faculty/petitions/${r.id}`); }}>Review →</button> },
  ];

  return (
    <AppShell navItems={facultyNav} logoVariant="stacked" sidebarLabel="FACULTY">
      <PageHeader title="Petition Queue" subtitle={`Petitions requiring your review · ${rows.length} pending`} useBrandFont />

      <div className={w.filterTabs} style={{ marginBottom: 16 }}>
        {TYPES.map((t) => (
          <button key={t} className={`${w.filterTab} ${type === t ? w.filterTabActive : ''}`} onClick={() => setType(t)}>{t}</button>
        ))}
      </div>

      <div className={w.split}>
        <div className={w.card} style={{ padding: 0 }}>
          <DataTable columns={columns} data={rows} onRowClick={setSelected} rowAccentColor={(r) => `var(--color-${URGENCY_VARIANT[r.urgency]})`} />
        </div>

        {selected && (
          <aside className={w.sidePanel}>
            <StatusPill status={`PETITION ${selected.ref}`} variant="coral" />
            <h3 className={w.cardTitle} style={{ marginTop: 12 }}>{selected.type}</h3>
            <div className={w.metaRow}><span>{selected.studentName}</span><span>{selected.department}</span></div>

            <div className={w.section}>
              <div className={w.sectionTitle}>Justification</div>
              <div className={w.quote}>{selected.justification}</div>
            </div>

            <div className={w.section}>
              <div className={w.sectionTitle}>Student Snapshot</div>
              <div className={w.metaRow}>
                <span>GPA <strong>{selected.snapshot.gpa}</strong></span>
                <span>Credits <strong>{selected.snapshot.credits}</strong></span>
                <StatusPill status={selected.snapshot.standing} variant="green" />
              </div>
            </div>

            <div className={w.btnRow}>
              <button className={`${w.btn} ${w.btnGreen}`}>✓ Approve</button>
              <button className={`${w.btn} ${w.btnDanger}`}>✕ Reject</button>
              <button className={`${w.btn} ${w.btnOutline}`} onClick={() => navigate(`/faculty/petitions/${selected.id}`)}>Open full review →</button>
            </div>
          </aside>
        )}
      </div>
    </AppShell>
  );
}
