import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import DataTable from '../../components/DataTable/DataTable';
import StatusPill from '../../components/StatusPill/StatusPill';
import SegmentedControl from '../../components/SegmentedControl/SegmentedControl';
import { facultyNav } from '../../config/navConfigs';
import { facultyAPI } from '../../api/apiGateway';
import useAsync from '../../hooks/useAsync';
import { exportCsv } from '../../utils/exportCsv';
import w from '../_shared/workflow.module.css';

/* Enrolled student list for a course (also the /faculty/courses landing). */

export default function ClassRosterPage() {
  const { courseId } = useParams();
  const navigate = useNavigate();
  const [tab, setTab] = useState('Roster');
  const [q, setQ] = useState('');

  const { data, loading, error, reload } = useAsync(async () => {
    let id = courseId;
    if (!id) {
      const dash = await facultyAPI.getDashboard();
      id = dash.courses?.[0]?.id;
      if (!id) return { course: null, roster: [] };
    }
    return facultyAPI.getCourseRoster(id);
  }, [courseId]);

  const course = data?.course;
  const roster = (data?.roster || []).filter(
    (s) => (s.student_name || '').toLowerCase().includes(q.toLowerCase()),
  );

  const columns = [
    { key: 'idx', header: '#', render: (_, row) => roster.indexOf(row) + 1 },
    { key: 'student_name', header: 'Student Name', sortable: true, render: (v) => <strong>{v}</strong> },
    { key: 'registration_date', header: 'Enrollment Date', sortable: true },
    { key: 'state', header: 'Status', render: (v) => <StatusPill status={v === 'enrolled' ? 'Enrolled' : v} variant={v === 'enrolled' ? 'green' : 'yellow'} /> },
  ];

  return (
    <AppShell navItems={facultyNav} logoVariant="stacked" sidebarLabel="FACULTY">
      <div className={w.breadcrumb}>
        <span onClick={() => navigate('/faculty/dashboard')} style={{ cursor: 'pointer' }}>Faculty</span> › My Courses › {course?.code || '…'}
      </div>

      {loading ? (
        <div className={w.card}><div className={w.empty}>Loading roster…</div></div>
      ) : error ? (
        <div className={w.card}><div className={w.empty}>
          <div className={w.emptyTitle}>Couldn't load roster</div>
          <p>{error}</p>
          <button className={`${w.btn} ${w.btnOutline} ${w.btnSm}`} onClick={reload}>Retry</button>
        </div></div>
      ) : !course ? (
        <div className={w.card}><div className={w.empty}>
          <div className={w.emptyTitle}>No course selected</div>
          <p>You have no assigned courses to display.</p>
        </div></div>
      ) : (
        <>
          <PageHeader title={`${course.code} — ${course.name}`} useBrandFont />

          <div style={{ marginBottom: 16 }}>
            <SegmentedControl options={['Roster', 'Attendance', 'Grades']} value={tab} onChange={setTab} />
          </div>

          {tab === 'Roster' ? (
            <>
              <div className={w.metaRow}>
                <span>Enrolled: <strong>{course.enrolled}</strong></span>
                <span>Capacity: <strong>{course.capacity}</strong></span>
                <span>Open Seats: <strong>{course.available_seats ?? 0}</strong></span>
              </div>
              <div className={w.toolbar}>
                <input className={w.search} placeholder="Search by name..." value={q} onChange={(e) => setQ(e.target.value)} />
                <button className={`${w.btn} ${w.btnOutline} ${w.btnSm}`} disabled={!roster.length}
                        onClick={() => exportCsv(`${course.code}_roster.csv`, [
                          { key: 'student_name', header: 'Student Name' },
                          { key: 'registration_date', header: 'Enrollment Date' },
                          { key: 'state', header: 'Status' },
                        ], roster)}>Export CSV</button>
              </div>
              <div className={w.card} style={{ padding: 0 }}>
                <DataTable columns={columns} data={roster} />
              </div>
            </>
          ) : (
            <div className={`${w.card} ${w.empty}`}>
              <div className={w.emptyTitle}>{tab}</div>
              <p>{tab} management for {course.code} will appear here.</p>
            </div>
          )}
        </>
      )}
    </AppShell>
  );
}
