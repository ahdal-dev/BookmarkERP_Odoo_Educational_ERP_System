import styles from './KanbanColumn.module.css';

/* ============================================================
   KANBAN COLUMN — Column with colored top border
   ============================================================ */

export default function KanbanColumn({
  title,
  count,
  color = 'var(--color-lime)',
  children,
  onDragOver,
  onDrop,
}) {
  return (
    <div
      className={styles.column}
      style={{ '--col-color': color }}
      onDragOver={onDragOver}
      onDrop={onDrop}
    >
      <div className={styles.header}>
        <h3 className={styles.title}>{title}</h3>
        {count !== undefined && (
          <span className={styles.count}>{count}</span>
        )}
      </div>
      <div className={styles.cards}>
        {children}
      </div>
    </div>
  );
}
