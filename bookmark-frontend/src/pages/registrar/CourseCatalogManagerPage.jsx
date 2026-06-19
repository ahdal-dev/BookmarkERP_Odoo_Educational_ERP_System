import { useState, useMemo } from 'react';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import DataTable from '../../components/DataTable/DataTable';
import StatusPill from '../../components/StatusPill/StatusPill';
import { registrarNav } from '../../config/navConfigs';
import { registrationAPI, registrarAPI } from '../../api/apiGateway';
import useAsync from '../../hooks/useAsync';
import w from '../_shared/workflow.module.css';

/* Registrar — course catalog with live data and per-course prerequisite editing. */

const STATUS_VARIANT = { Active: 'green', Inactive: 'black' };
const FILTERS = ['All', 'Active', 'Inactive'];

function mapCourse(c) {
  const enrolled = (c.total_seats ?? 0) - (c.available_seats ?? 0);
  return {
    id: c.id,
    code: c.code,
    name: c.name,
    credits: c.credits ?? 0,
    instructor: c.instructor || 'TBA',
    seats: `${enrolled}/${c.total_seats ?? 0}`,
    status: c.registration_open ? 'Active' : 'Inactive',
    prerequisites: c.prerequisites || [],
  };
}

export default function CourseCatalogManagerPage() {
  const { data, loading, error, reload } = useAsync(() => registrationAPI.getCourses(), []);
  const courses = useMemo(() => (data?.courses || []).map(mapCourse), [data]);

  const [q, setQ] = useState('');
  const [filter, setFilter] = useState('All');
  const [drawer, setDrawer] = useState(null);

  const rows = courses.filter((c) =>
    (filter === 'All' || c.status === filter) &&
    (c.name?.toLowerCase().includes(q.toLowerCase()) || c.code?.toLowerCase().includes(q.toLowerCase())));

  const columns = [
    { key: 'code', header: 'Code', sortable: true, render: (v) => <strong>{v}</strong> },
    { key: 'name', header: 'Course Name', sortable: true },
    { key: 'credits', header: 'Credits' },
    { key: 'instructor', header: 'Instructor' },
    { key: 'seats', header: 'Seats' },
    {
      key: 'prerequisites', header: 'Prerequisites',
      render: (v) => (v && v.length ? v.map((p) => p.code).join(', ') : '—'),
    },
    { key: 'status', header: 'Status', render: (v) => <StatusPill status={v} variant={STATUS_VARIANT[v]} /> },
    { key: 'actions', header: 'Actions', render: (_, r) => (
      <span className={w.cardLink} onClick={(e) => { e.stopPropagation(); setDrawer(r); }}>Edit Prerequisites</span>
    ) },
  ];

  return (
    <AppShell navItems={registrarNav} logoVariant="stacked" sidebarLabel="REGISTRAR">
      <PageHeader
        title="Course Catalog Manager" subtitle={`Fall 2026 · ${courses.length} courses configured`} useBrandFont
      />

      <div className={w.toolbar}>
        <input className={w.search} placeholder="Search courses..." value={q} onChange={(e) => setQ(e.target.value)} />
        <div className={w.filterTabs}>
          {FILTERS.map((f) => <button key={f} className={`${w.filterTab} ${filter === f ? w.filterTabActive : ''}`} onClick={() => setFilter(f)}>{f}</button>)}
        </div>
      </div>

      <div className={w.card} style={{ padding: 0 }}>
        {loading ? (
          <div className={w.empty}>Loading courses…</div>
        ) : error ? (
          <div className={w.empty}>
            <div className={w.emptyTitle}>Couldn't load courses</div>
            <p>{error}</p>
            <button className={`${w.btn} ${w.btnOutline} ${w.btnSm}`} onClick={reload}>Retry</button>
          </div>
        ) : (
          <DataTable columns={columns} data={rows} />
        )}
      </div>

      {drawer && (
        <PrereqDrawer
          course={drawer}
          allCourses={courses}
          onClose={() => setDrawer(null)}
          onSaved={() => { setDrawer(null); reload(); }}
        />
      )}
    </AppShell>
  );
}

function PrereqDrawer({ course, allCourses, onClose, onSaved }) {
  const [selected, setSelected] = useState(() => new Set((course.prerequisites || []).map((p) => p.id)));
  const [saving, setSaving] = useState(false);
  const options = allCourses.filter((c) => c.id !== course.id);

  const toggle = (id) => setSelected((prev) => {
    const next = new Set(prev);
    next.has(id) ? next.delete(id) : next.add(id);
    return next;
  });

  const save = async () => {
    setSaving(true);
    try {
      await registrarAPI.setCoursePrerequisites(course.id, [...selected]);
      onSaved();
    } catch {
      setSaving(false);
    }
  };

  return (
    <>
      <div onClick={onClose} style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.35)', zIndex: 40 }} />
      <aside style={{ position: 'fixed', top: 0, right: 0, bottom: 0, width: 'min(440px, 92vw)', background: '#fff', boxShadow: '-4px 0 24px rgba(0,0,0,0.15)', zIndex: 41, padding: 28, overflowY: 'auto' }}>
        <h2 style={{ fontWeight: 800, fontSize: '1.3rem', marginBottom: 6 }}>Prerequisites — {course.code}</h2>
        <p className={w.cardSub}>Select courses a student must pass before enrolling in {course.code}.</p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6, margin: '8px 0 20px' }}>
          {options.length === 0 ? (
            <span style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem' }}>No other courses available.</span>
          ) : options.map((c) => (
            <label key={c.id} style={{ display: 'flex', gap: 10, alignItems: 'center', padding: '8px 10px', borderRadius: 8, background: selected.has(c.id) ? 'var(--color-bg-warm)' : 'transparent', cursor: 'pointer' }}>
              <input type="checkbox" checked={selected.has(c.id)} onChange={() => toggle(c.id)} />
              <span style={{ fontSize: '0.85rem' }}><strong>{c.code}</strong> — {c.name}</span>
            </label>
          ))}
        </div>
        <div style={{ display: 'flex', gap: 12 }}>
          <button className={`${w.btn} ${w.btnPrimary} ${w.btnFull}`} onClick={save} disabled={saving}>
            {saving ? 'Saving…' : 'Save Prerequisites'}
          </button>
          <button className={`${w.btn} ${w.btnOutline} ${w.btnFull}`} onClick={onClose}>Cancel</button>
        </div>
      </aside>
    </>
  );
}
