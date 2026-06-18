import styles from './KanbanBoard.module.css';

/* ============================================================
   KANBAN BOARD — Horizontal scroll container for columns
   ============================================================ */

export default function KanbanBoard({ children, className = '' }) {
  return (
    <div className={`${styles.board} ${className}`}>
      {children}
    </div>
  );
}
