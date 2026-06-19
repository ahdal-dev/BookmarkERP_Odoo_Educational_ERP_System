import { useState, useCallback, useEffect } from 'react';
import AppShell from '../../components/AppShell/AppShell';
import TopBar from '../../components/TopBar/TopBar';
import PageHeader from '../../components/PageHeader/PageHeader';
import KanbanBoard from '../../components/KanbanBoard/KanbanBoard';
import KanbanColumn from '../../components/KanbanBoard/KanbanColumn';
import KanbanCard from '../../components/KanbanBoard/KanbanCard';
import { admissionsNav } from '../../config/navConfigs';
import { admissionsAPI } from '../../api/apiGateway';
import useAsync from '../../hooks/useAsync';
import w from '../_shared/workflow.module.css';
import styles from './AdmissionPipelinePage.module.css';

/* ============================================================
   ADMISSION PIPELINE — Kanban board for application stages (live)
   ============================================================ */

export default function AdmissionPipelinePage() {
  const { data, loading, error, reload } = useAsync(() => admissionsAPI.getPipeline(), []);
  const [columns, setColumns] = useState([]);
  const [dragItem, setDragItem] = useState(null);

  useEffect(() => {
    if (data?.columns) setColumns(data.columns);
  }, [data]);

  const handleDragStart = (cardId, fromColId) => {
    setDragItem({ cardId, fromColId });
  };

  const handleDrop = useCallback((toColId) => {
    if (!dragItem || dragItem.fromColId === toColId) return;

    let movedCardId = null;
    setColumns((prev) => {
      const next = prev.map((col) => ({ ...col, cards: [...col.cards] }));
      const fromCol = next.find((c) => c.id === dragItem.fromColId);
      const toCol = next.find((c) => c.id === toColId);
      if (!fromCol || !toCol) return prev;

      const cardIdx = fromCol.cards.findIndex((c) => c.id === dragItem.cardId);
      if (cardIdx === -1) return prev;

      const [card] = fromCol.cards.splice(cardIdx, 1);
      toCol.cards.push(card);
      movedCardId = card.id;
      return next;
    });

    // Persist the stage change; reload to resync on failure.
    if (movedCardId != null) {
      admissionsAPI.updateStage(movedCardId, toColId).catch(() => reload());
    }
    setDragItem(null);
  }, [dragItem, reload]);

  return (
    <AppShell
      navItems={admissionsNav}
      logoVariant="icon-text"
      topBar={<TopBar searchPlaceholder="Search applicants..." />}
    >
      <PageHeader
        title="Admission Pipeline"
        subtitle="ACADEMIC YEAR 2024-2025"
        useBrandFont
        actions={
          <div className={styles.actionBtns}>
            <button className={styles.filterBtn}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>
              Filters
            </button>
            <button className={styles.filterBtn}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
              Group By
            </button>
            <button className={styles.createBtn}>+ Create</button>
          </div>
        }
      />

      {loading && <div className={w.card}><div className={w.empty}>Loading admissions pipeline…</div></div>}
      {error && !loading && (
        <div className={`${w.alert} ${w.alertCoral}`}>
          {error} <span className={w.cardLink} style={{ color: '#842029' }} onClick={reload}>Retry →</span>
        </div>
      )}

      {/* Kanban Board */}
      <KanbanBoard>
        {columns.map((col) => (
          <KanbanColumn
            key={col.id}
            title={col.title}
            count={col.cards.length}
            color={col.color}
            onDragOver={(e) => e.preventDefault()}
            onDrop={() => handleDrop(col.id)}
          >
            {col.cards.map((card) => (
              <KanbanCard
                key={card.id}
                title={card.name}
                subtitle={`REF: ${card.ref}`}
                tag={card.program}
                tagColor="green"
                warning={card.warning}
                avatars={card.avatars || []}
                starred={card.starred}
                onStarToggle={() => {}}
                accentColor={card.accentColor}
                onDragStart={(e) => {
                  e.dataTransfer.effectAllowed = 'move';
                  handleDragStart(card.id, col.id);
                }}
              />
            ))}
          </KanbanColumn>
        ))}
      </KanbanBoard>

      {/* Floating Search FAB */}
      <button className={styles.searchFab} aria-label="Search applications">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
          <circle cx="11" cy="11" r="8" /><path d="M21 21l-4.35-4.35" />
        </svg>
      </button>
    </AppShell>
  );
}
