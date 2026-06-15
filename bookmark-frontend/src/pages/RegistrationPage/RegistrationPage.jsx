import { useState, useMemo } from 'react';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import CourseCard from '../../components/CourseCard/CourseCard';
import Pagination from '../../components/Pagination/Pagination';
import SegmentedControl from '../../components/SegmentedControl/SegmentedControl';
import { registrationNav } from '../../config/navConfigs';
import { mockCourses, mockDepartments, mockCredits } from '../../mocks/registrationMocks';
import styles from './RegistrationPage.module.css';

/* ============================================================
   REGISTRATION PAGE — Course catalog with filters and grid
   ============================================================ */

const ITEMS_PER_PAGE = 6;

export default function RegistrationPage() {
  const [search, setSearch] = useState('');
  const [department, setDepartment] = useState('All Departments');
  const [credits, setCredits] = useState('Any Credits');
  const [statusFilter, setStatusFilter] = useState('All');
  const [page, setPage] = useState(1);

  const filtered = useMemo(() => {
    return mockCourses.filter((c) => {
      const matchSearch = !search ||
        c.code.toLowerCase().includes(search.toLowerCase()) ||
        c.title.toLowerCase().includes(search.toLowerCase()) ||
        c.instructor.toLowerCase().includes(search.toLowerCase());
      const matchDept = department === 'All Departments' || c.department === department;
      const matchCredits = credits === 'Any Credits' || String(c.credits) === credits;
      const matchStatus = statusFilter === 'All' || c.status.toLowerCase() === statusFilter.toLowerCase();
      return matchSearch && matchDept && matchCredits && matchStatus;
    });
  }, [search, department, credits, statusFilter]);

  const totalPages = Math.ceil(filtered.length / ITEMS_PER_PAGE);
  const paged = filtered.slice((page - 1) * ITEMS_PER_PAGE, page * ITEMS_PER_PAGE);

  const handlePageChange = (p) => setPage(p);

  return (
    <AppShell navItems={registrationNav} logoVariant="icon-text">
      {/* Page Header */}
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
            value={department}
            onChange={(e) => { setDepartment(e.target.value); setPage(1); }}
          >
            {mockDepartments.map((d) => <option key={d} value={d}>{d}</option>)}
          </select>

          <select
            className={styles.select}
            value={credits}
            onChange={(e) => { setCredits(e.target.value); setPage(1); }}
          >
            {mockCredits.map((c) => <option key={c} value={c}>{c}</option>)}
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
      {paged.length > 0 ? (
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
      <div className={styles.paginationWrap}>
        <Pagination
          currentPage={page}
          totalPages={totalPages}
          onPageChange={handlePageChange}
        />
      </div>
    </AppShell>
  );
}
