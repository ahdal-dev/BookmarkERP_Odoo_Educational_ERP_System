import { useState, useEffect } from 'react';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import DataTable from '../../components/DataTable/DataTable';
import StatusPill from '../../components/StatusPill/StatusPill';
import SegmentedControl from '../../components/SegmentedControl/SegmentedControl';
import { useAuth } from '../../context/AuthContext';
import { petitionsAdminNav } from '../../config/navConfigs';
import { petitionsAPI } from '../../api/apiGateway';
import useAsync from '../../hooks/useAsync';
import styles from './PetitionTrackingPage.module.css';

/* ============================================================
   PETITION TRACKING BOARD — Admin petition management
   List view with detail panel, and Kanban toggle (stubbed).
   ============================================================ */

const URGENCY_COLORS = { Critical: 'coral', Normal: 'green', Low: 'yellow' };

const columns = [
  { key: 'ref', header: 'REF', sortable: true },
  {
    key: 'studentName', header: 'Student ID & Name', sortable: true,
    render: (val, row) => <span><strong>{row.ref}</strong> — {val}</span>,
  },
  {
    key: 'type', header: 'Petition Type', sortable: true,
    render: (val) => <StatusPill status={val} variant="yellow" />,
  },
  { key: 'date', header: 'Submission', sortable: true },
  {
    key: 'urgency', header: 'Urgency',
    render: (val, row) => (
      <StatusPill
        status={val}
        variant={URGENCY_COLORS[val] || 'green'}
      />
    ),
  },
  {
    key: 'expand', header: '→',
    render: () => <span style={{ cursor: 'pointer', fontSize: '1.1rem' }}>→</span>,
  },
];

export default function PetitionTrackingPage() {
  const { logout } = useAuth();
  const [viewMode, setViewMode] = useState('List View');
  const { data, loading, error, reload } = useAsync(() => petitionsAPI.listPetitions(), []);
  const petitions = data?.petitions || [];
  const [selectedPetition, setSelectedPetition] = useState(null);

  useEffect(() => {
    if (petitions.length && !selectedPetition) setSelectedPetition(petitions[0]);
  }, [petitions, selectedPetition]);

  const handleRowClick = (row) => {
    const petition = petitions.find((p) => p.id === row.id);
    if (petition) setSelectedPetition(petition);
  };

  const sidebarFooter = (
    <>
      <button className={styles.newPetitionBtn}>+ New Petition</button>
      <a href="/help" className={styles.footerLink}>Help Center</a>
      <button className={styles.footerLink} onClick={logout}>Logout</button>
    </>
  );

  return (
    <AppShell
      navItems={petitionsAdminNav}
      logoVariant="stacked"
      sidebarLabel="ACADEMIC MANAGEMENT"
      sidebarFooter={sidebarFooter}
    >
      <PageHeader
        title="Petition Tracking Board"
        subtitle={`Reviewing ${petitions.length} institutional requests`}
        useBrandFont
        actions={
          <SegmentedControl
            options={['List View', 'Kanban']}
            value={viewMode}
            onChange={setViewMode}
          />
        }
      />

      <div className={styles.layout}>
        {/* Table */}
        <div className={styles.tableSection}>
          <div className={styles.tableCard}>
            {loading ? (
              <div style={{ padding: 40, textAlign: 'center', color: 'var(--color-text-muted)' }}>Loading petitions…</div>
            ) : error ? (
              <div style={{ padding: 40, textAlign: 'center', color: 'var(--color-text-muted)' }}>
                {error} <button onClick={reload} style={{ marginLeft: 8 }}>Retry</button>
              </div>
            ) : (
              <DataTable
                columns={columns}
                data={petitions}
                onRowClick={handleRowClick}
                rowAccentColor={(row) => row.accentColor}
              />
            )}
          </div>
        </div>

        {/* Detail Panel */}
        {selectedPetition && (
          <aside className={styles.detailPanel}>
            <div className={styles.detailHeader}>
              <StatusPill status={`PETITION ${selectedPetition.ref}`} variant="coral" />
            </div>

            <h2 className={styles.detailTitle}>{selectedPetition.detail.title}</h2>
            <div className={styles.detailMeta}>
              <span className={styles.detailName}>{selectedPetition.studentName}</span>
              <span className={styles.detailDept}>{selectedPetition.detail.department}</span>
            </div>

            {/* Justification */}
            <div className={styles.section}>
              <h4 className={styles.sectionTitle}>JUSTIFICATION</h4>
              <div className={styles.quote}>
                {selectedPetition.detail.justification}
              </div>
            </div>

            {/* Attachments */}
            <div className={styles.section}>
              <h4 className={styles.sectionTitle}>ATTACHMENTS</h4>
              <div className={styles.attachmentCard}>
                <div className={styles.attachIcon}>
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6"/></svg>
                </div>
                <div className={styles.attachInfo}>
                  <span className={styles.attachName}>{selectedPetition.studentName}</span>
                  <span className={styles.attachType}>document</span>
                </div>
                <span className={styles.pdfBadge}>PDF</span>
              </div>
            </div>

            {/* Activity Timeline */}
            <div className={styles.section}>
              <h4 className={styles.sectionTitle}>PREVIOUS ACTIVITY</h4>
              <div className={styles.timeline}>
                {selectedPetition.detail.activity.map((act, i) => (
                  <div key={i} className={styles.timelineItem}>
                    <div className={styles.timelineDot} style={{ background: act.color }} />
                    {i < selectedPetition.detail.activity.length - 1 && (
                      <div className={styles.timelineLine} />
                    )}
                    <div className={styles.timelineContent}>
                      <span className={styles.timelineText}>{act.text}</span>
                      <span className={styles.timelineActor}>{act.actor}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </aside>
        )}
      </div>
    </AppShell>
  );
}
