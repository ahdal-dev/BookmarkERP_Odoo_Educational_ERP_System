import { useState, useMemo } from 'react';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import CourseCard from '../../components/CourseCard/CourseCard';
import Pagination from '../../components/Pagination/Pagination';
import SegmentedControl from '../../components/SegmentedControl/SegmentedControl';
import { registrationNav } from '../../config/navConfigs';
import { registrationAPI } from '../../api/apiGateway';
import useAsync from '../../hooks/useAsync';
import styles from './RegistrationPage.module.css';

/* ============================================================
   REGISTRATION PAGE — Live course catalog with filters and grid
   ============================================================ */

const ITEMS_PER_PAGE = 6;

// Map an education.course record to the CourseCard shape.
function mapCourse(c) {
  const open = c.registration_open;
  const seatsOpen = (c.available_seats ?? 0) > 0;
  const status = !open ? 'Closed' : seatsOpen ? 'Open' : 'Waitlist';
  const schedule = c.schedule
    || (c.timing_start != null ? `${c.timing_start}:00 – ${c.timing_end}:00` : 'TBA');
  return {
    id: c.id,
    code: c.code,
    title: c.name,
    credits: c.credits ?? 0,
    type: 'Course',
    instructor: c.instructor || 'TBA',
    schedule,
    seats: `${c.available_seats ?? 0}/${c.total_seats ?? 0}`,
    status,
    prerequisites: c.prerequisites || [],
  };
}

export default function RegistrationPage() {
  const { data, loading, error, reload } = useAsync(() => registrationAPI.getCourses(), []);
  const courses = useMemo(() => (data?.courses || []).map(mapCourse), [data]);

  const [search, setSearch] = useState('');
  const [credits, setCredits] = useState('Any Credits');
  const [statusFilter, setStatusFilter] = useState('All');
  const [page, setPage] = useState(1);

  const creditOptions = useMemo(() => {
    const set = [...new Set(courses.map((c) => String(c.credits)))].sort();
    return ['Any Credits', ...set];
  }, [courses]);

  const filtered = useMemo(() => {
    return courses.filter((c) => {
      const matchSearch = !search ||
        c.code.toLowerCase().includes(search.toLowerCase()) ||
        c.title.toLowerCase().includes(search.toLowerCase()) ||
        c.instructor.toLowerCase().includes(search.toLowerCase());
      const matchCredits = credits === 'Any Credits' || String(c.credits) === credits;
      const matchStatus = statusFilter === 'All' || c.status.toLowerCase() === statusFilter.toLowerCase();
      return matchSearch && matchCredits && matchStatus;
    });
  }, [courses, search, credits, statusFilter]);

  const totalPages = Math.ceil(filtered.length / ITEMS_PER_PAGE);
  const paged = filtered.slice((page - 1) * ITEMS_PER_PAGE, page * ITEMS_PER_PAGE);

  return (
    <AppShell navItems={registrationNav} logoVariant="icon-text">
      <PageHeader
        title="Course Registration"
        badge="FALL 2026"
        badgeVariant="green"
        subtitle="Browse and select your courses for the upcoming semester."
      />

      {/* Filter Bar */}
      <div className={styles.filterBar}>
        <div className={styles.searchGroup}>
          <label className={styles.filterLabel}>QUICK SEARCH</label>
          <div className={styles.searchWrap}>
            <input
              type="text"
              className={styles.searchInput}
              placeholder="Search course code, name, or instructor..."
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            />
            <button className={styles.searchBtn} aria-label="Search">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.5" strokeLinecap="round"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
            </button>
          </div>
        </div>

        <div className={styles.dropdowns}>
          <select
            className={styles.select}
            value={credits}
            onChange={(e) => { setCredits(e.target.value); setPage(1); }}
          >
            {creditOptions.map((c) => <option key={c} value={c}>{c === 'Any Credits' ? c : `${c} Credits`}</option>)}
          </select>
        </div>

        <div className={styles.statusGroup}>
          <label className={styles.filterLabel}>STATUS</label>
          <SegmentedControl
            options={['All', 'Open', 'Waitlist']}
            value={statusFilter}
            onChange={(v) => { setStatusFilter(v); setPage(1); }}
          />
        </div>
      </div>

      {/* Course Grid */}
      {loading ? (
        <div className={styles.empty}><p>Loading course catalog…</p></div>
      ) : error ? (
        <div className={styles.empty}>
          <p>{error}</p>
          <button className={styles.searchBtn} onClick={reload} style={{ width: 'auto', padding: '8px 16px' }}>Retry</button>
        </div>
      ) : paged.length > 0 ? (
        <div className={styles.grid}>
          {paged.map((course) => (
            <CourseCard key={course.id} course={course} onAction={(c) => console.log('Action:', c.code)} />
          ))}
        </div>
      ) : (
        <div className={styles.empty}>
          <p>No courses match your filters.</p>
        </div>
      )}

      {/* Pagination */}
      {!loading && !error && totalPages > 1 && (
        <div className={styles.paginationWrap}>
          <Pagination
            currentPage={page}
            totalPages={totalPages}
            onPageChange={setPage}
          />
        </div>
      )}
    </AppShell>
  );
}
