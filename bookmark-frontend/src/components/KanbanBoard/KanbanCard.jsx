import StatusPill from '../StatusPill/StatusPill';
import styles from './KanbanCard.module.css';

/* ============================================================
   KANBAN CARD — White card for kanban boards
   ============================================================ */

export default function KanbanCard({
  title,
  subtitle,
  tag,
  tagColor,
  warning,
  avatars = [],
  starred,
  onStarToggle,
  onClick,
  draggable = true,
  onDragStart,
  accentColor = 'var(--color-lime)',
}) {
  return (
    <div
      className={styles.card}
      style={{ '--card-accent': accentColor }}
      onClick={onClick}
      draggable={draggable}
      onDragStart={onDragStart}
    >
      <div className={styles.accent} />

      <div className={styles.body}>
        {/* Header row: title + star */}
        <div className={styles.headerRow}>
          <span className={styles.title}>{title}</span>
          {onStarToggle && (
            <button
              className={`${styles.star} ${starred ? styles.starred : ''}`}
              onClick={(e) => { e.stopPropagation(); onStarToggle(); }}
              aria-label="Toggle favorite"
            >
              {starred ? '★' : '☆'}
            </button>
          )}
        </div>

        {/* Subtitle */}
        {subtitle && <span className={styles.subtitle}>{subtitle}</span>}

        {/* Tag */}
        {tag && <StatusPill status={tag} variant={tagColor} />}

        {/* Warning */}
        {warning && (
          <div className={styles.warning}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--color-coral)" strokeWidth="2" strokeLinecap="round">
              <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><path d="M12 9v4m0 4h.01"/>
            </svg>
            <span>{warning}</span>
          </div>
        )}

        {/* Avatars */}
        {avatars.length > 0 && (
          <div className={styles.avatars}>
            {avatars.map((a, i) => (
              <div key={i} className={styles.avatarCircle} title={a.name}>
                {a.initial || a.name?.charAt(0)?.toUpperCase()}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
