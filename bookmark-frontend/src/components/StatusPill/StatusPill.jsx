import styles from './StatusPill.module.css';

/* ============================================================
   STATUS PILL — Colored rounded pill for statuses/roles/urgency
   Centralizes color mapping for consistency across all pages.
   ============================================================ */

const STATUS_COLORS = {
  // Green
  open: 'green', approved: 'green', active: 'green', normal: 'green',
  instructor: 'green', completed: 'green', enrolled: 'green', verified: 'green',
  // Yellow
  waitlist: 'yellow', pending: 'yellow', low: 'yellow', student: 'yellow',
  'in review': 'yellow', 'in_review': 'yellow', 'under review': 'yellow',
  // Coral
  closed: 'coral', denied: 'coral', critical: 'coral', admin: 'coral',
  missing: 'coral', rejected: 'coral', dropped: 'coral',
  // Black
  registrar: 'black', default: 'black',
};

export default function StatusPill({ status, variant, className = '' }) {
  const normalizedStatus = status?.toLowerCase?.() || '';
  const colorKey = variant || STATUS_COLORS[normalizedStatus] || 'black';

  return (
    <span className={`${styles.pill} ${styles[colorKey]} ${className}`}>
      {status}
    </span>
  );
}
