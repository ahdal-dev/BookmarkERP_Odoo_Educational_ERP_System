import styles from './StatCard.module.css';

/* ============================================================
   STAT CARD — White card with colored top accent bar,
   large bold number, label, optional delta or custom content.
   ============================================================ */

export default function StatCard({
  value,
  label,
  delta,
  accentColor = 'var(--color-lime)',
  dark = false,
  children,
  className = '',
}) {
  return (
    <div
      className={`${styles.card} ${dark ? styles.dark : ''} ${className}`}
      style={{ '--accent': accentColor }}
    >
      <div className={styles.accent} />
      <div className={styles.body}>
        <span className={styles.label}>{label}</span>
        <div className={styles.valueRow}>
          <span className={styles.value}>{value}</span>
          {children}
        </div>
        {delta && (
          <span className={styles.delta}>{delta}</span>
        )}
      </div>
    </div>
  );
}
