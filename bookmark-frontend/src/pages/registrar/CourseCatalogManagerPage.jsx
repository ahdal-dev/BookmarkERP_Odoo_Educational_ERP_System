import { useState } from 'react';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import DataTable from '../../components/DataTable/DataTable';
import StatusPill from '../../components/StatusPill/StatusPill';
import ToggleSwitch from '../../components/ToggleSwitch/ToggleSwitch';
import { registrarNav } from '../../config/navConfigs';
import w from '../_shared/workflow.module.css';

/* Registrar — full CRUD course catalog manager. */

const COURSES = [
  { code: 'CSAI 301', name: 'Advanced Algorithms', dept: 'Computer Science', credits: 3, instructor: 'Dr. Alan Turing', seats: '45/50', status: 'Active' },
  { code: 'MATH 200', name: 'Calculus II', dept: 'Mathematics', credits: 4, instructor: 'Dr. K. Johnson', seats: '25/25', status: 'Active' },
  { code: 'BIO 102', name: 'General Biology', dept: 'Biology', credits: 3, instructor: 'Dr. R. Franklin', seats: '0/40', status: 'Inactive' },
  { code: 'CSAI 410', name: 'Machine Learning', dept: 'Computer Science', credits: 4, instructor: 'Dr. R. Feynman', seats: '32/40', status: 'Active' },
  { code: 'ENG 105', name: 'Academic Writing', dept: 'Humanities', credits: 3, instructor: 'Prof. M. Angelou', seats: '12/28', status: 'Draft' },
];

const STATUS_VARIANT = { Active: 'green', Inactive: 'black', Draft: 'yellow' };
const FILTERS = ['All', 'Active', 'Inactive', 'Draft'];

export default function CourseCatalogManagerPage() {
  const [q, setQ] = useState('');
  const [filter, setFilter] = useState('All');
  const [drawer, setDrawer] = useState(null); // null | course | {} (new)

  const rows = COURSES.filter((c) =>
    (filter === 'All' || c.status === filter) &&
    (c.name.toLowerCase().includes(q.toLowerCase()) || c.code.toLowerCase().includes(q.toLowerCase())));

  const columns = [
    { key: 'code', header: 'Code', sortable: true, render: (v) => <strong>{v}</strong> },
    { key: 'name', header: 'Course Name', sortable: true },
    { key: 'dept', header: 'Dept', sortable: true },
    { key: 'credits', header: 'Credits' },
    { key: 'instructor', header: 'Instructor' },
    { key: 'seats', header: 'Seats' },
    { key: 'status', header: 'Status', render: (v) => <StatusPill status={v} variant={STATUS_VARIANT[v]} /> },
    { key: 'actions', header: 'Actions', render: (_, r) => (
      <span style={{ display: 'flex', gap: 10 }}>
        <span className={w.cardLink} onClick={(e) => { e.stopPropagation(); setDrawer(r); }}>Edit</span>
        <span style={{ color: 'var(--color-coral)', cursor: 'pointer', fontSize: '0.82rem', fontWeight: 700 }}>Delete</span>
      </span>
    ) },
  ];

  return (
    <AppShell navItems={registrarNav} logoVariant="stacked" sidebarLabel="REGISTRAR">
      <PageHeader
        title="Course Catalog Manager" subtitle={`Fall 2026 · ${COURSES.length} courses configured`} useBrandFont
        actions={<button className={`${w.btn} ${w.btnPrimary}`} onClick={() => setDrawer({})}>+ Add Course</button>}
      />

      <div className={w.toolbar}>
        <input className={w.search} placeholder="Search courses..." value={q} onChange={(e) => setQ(e.target.value)} />
        <div className={w.filterTabs}>
          {FILTERS.map((f) => <button key={f} className={`${w.filterTab} ${filter === f ? w.filterTabActive : ''}`} onClick={() => setFilter(f)}>{f}</button>)}
        </div>
      </div>

      <div className={w.card} style={{ padding: 0 }}>
        <DataTable columns={columns} data={rows} />
      </div>

      {drawer && (
        <Drawer course={drawer} onClose={() => setDrawer(null)} />
      )}
    </AppShell>
  );
}

function Drawer({ course, onClose }) {
  const isNew = !course.code;
  const [active, setActive] = useState(course.status !== 'Inactive');
  return (
    <>
      <div onClick={onClose} style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.35)', zIndex: 40 }} />
      <aside style={{ position: 'fixed', top: 0, right: 0, bottom: 0, width: 'min(440px, 92vw)', background: '#fff', boxShadow: '-4px 0 24px rgba(0,0,0,0.15)', zIndex: 41, padding: 28, overflowY: 'auto' }}>
        <h2 style={{ fontWeight: 800, fontSize: '1.3rem', marginBottom: 18 }}>{isNew ? 'Add Course' : `Edit ${course.code}`}</h2>
        <div className={w.cardGrid2}>
          <div className={w.field}><span className={w.fieldLabel}>Course Code</span><input className={w.input} defaultValue={course.code} /></div>
          <div className={w.field}><span className={w.fieldLabel}>Credits</span><input type="number" className={w.input} defaultValue={course.credits || 3} /></div>
        </div>
        <div className={w.field}><span className={w.fieldLabel}>Course Name</span><input className={w.input} defaultValue={course.name} /></div>
        <div className={w.field}><span className={w.fieldLabel}>Department</span><input className={w.input} defaultValue={course.dept} /></div>
        <div className={w.field}><span className={w.fieldLabel}>Instructor</span><input className={w.input} defaultValue={course.instructor} /></div>
        <div className={w.cardGrid2}>
          <div className={w.field}><span className={w.fieldLabel}>Total Seats</span><input type="number" className={w.input} defaultValue={50} /></div>
          <div className={w.field}><span className={w.fieldLabel}>Schedule</span><input className={w.input} placeholder="MWF 10:00-11:00" /></div>
        </div>
        <div className={w.field}><span className={w.fieldLabel}>Description</span><textarea className={w.textarea} /></div>
        <div style={{ margin: '4px 0 18px' }}><ToggleSwitch checked={active} onChange={setActive} label="Active" description="Visible in the student catalog" /></div>
        <div style={{ display: 'flex', gap: 12 }}>
          <button className={`${w.btn} ${w.btnPrimary} ${w.btnFull}`} onClick={onClose}>Save Changes</button>
          <button className={`${w.btn} ${w.btnOutline} ${w.btnFull}`} onClick={onClose}>Cancel</button>
        </div>
      </aside>
    </>
  );
}
