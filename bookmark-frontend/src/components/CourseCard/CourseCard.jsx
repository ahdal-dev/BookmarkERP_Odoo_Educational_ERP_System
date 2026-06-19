import StatusPill from '../StatusPill/StatusPill';
import styles from './CourseCard.module.css';

/* ============================================================
   COURSE CARD — White card with colored left border
   Displays course code, title, meta info, and action button.
   ============================================================ */

const STATUS_BORDER = {
  open: 'var(--color-lime)',
  waitlist: 'var(--color-yellow)',
  closed: 'var(--color-coral)',
};

const ACTION_CONFIG = {
  open: { label: 'Add Course', className: 'actionGreen' },
  waitlist: { label: 'Join Waitlist', className: 'actionYellow' },
  closed: { label: 'Add Course', className: 'actionGray' },
};

export default function CourseCard({ course, onAction }) {
  const status = course.status?.toLowerCase() || 'open';
  const borderColor = STATUS_BORDER[status] || STATUS_BORDER.open;
  const action = ACTION_CONFIG[status] || ACTION_CONFIG.open;

  return (
    <div className={styles.card} style={{ '--border-color': borderColor }}>
      {/* Header: code + status */}
      <div className={styles.header}>
        <span className={styles.code}>{course.code}</span>
        <StatusPill status={course.status} />
      </div>

      {/* Title */}
      <h3 className={styles.title}>{course.title} —</h3>

      {/* Meta lines */}
      <div className={styles.meta}>
        <div className={styles.metaLine}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/></svg>
          <span>{course.credits} CREDITS · {course.type}</span>
        </div>
        <div className={styles.metaLine}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
          <span>Instructor: {course.instructor}</span>
        </div>
        <div className={styles.metaLine}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
          <span>Schedule: {course.schedule}</span>
        </div>
        <div className={styles.metaLine}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75"/></svg>
          <span>Seats: {course.seats}</span>
        </div>
        {course.prerequisites && course.prerequisites.length > 0 && (
          <div className={styles.metaLine}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/></svg>
            <span>Prerequisites: {course.prerequisites.map((p) => p.code).join(', ')}</span>
          </div>
        )}
      </div>

      {/* Footer: action button + icon badge */}
      <div className={styles.footer}>
        <button
          className={`${styles.actionBtn} ${styles[action.className]}`}
          onClick={() => onAction?.(course)}
          disabled={status === 'closed'}
        >
          {action.label}
        </button>
        <div className={styles.iconBadge}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"><circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/></svg>
        </div>
      </div>
    </div>
  );
}
