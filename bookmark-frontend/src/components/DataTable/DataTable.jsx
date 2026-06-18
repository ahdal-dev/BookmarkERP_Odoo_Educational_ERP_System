import { useState, useMemo } from 'react';
import styles from './DataTable.module.css';

/* ============================================================
   DATA TABLE — Generic table with optional checkboxes,
   sortable headers, custom cell renderers, and row accents.
   ============================================================ */

export default function DataTable({
  columns = [],
  data = [],
  selectable = false,
  onRowClick,
  rowAccentColor,
  className = '',
}) {
  const [selectedRows, setSelectedRows] = useState(new Set());
  const [sortKey, setSortKey] = useState(null);
  const [sortDir, setSortDir] = useState('asc');

  const sortedData = useMemo(() => {
    if (!sortKey) return data;
    const col = columns.find((c) => c.key === sortKey);
    if (!col?.sortable) return data;

    return [...data].sort((a, b) => {
      const aVal = a[sortKey] ?? '';
      const bVal = b[sortKey] ?? '';
      const cmp = String(aVal).localeCompare(String(bVal), undefined, { numeric: true });
      return sortDir === 'asc' ? cmp : -cmp;
    });
  }, [data, sortKey, sortDir, columns]);

  const handleSort = (key) => {
    const col = columns.find((c) => c.key === key);
    if (!col?.sortable) return;
    if (sortKey === key) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortKey(key);
      setSortDir('asc');
    }
  };

  const toggleAll = () => {
    if (selectedRows.size === data.length) {
      setSelectedRows(new Set());
    } else {
      setSelectedRows(new Set(data.map((_, i) => i)));
    }
  };

  const toggleRow = (i) => {
    setSelectedRows((prev) => {
      const next = new Set(prev);
      next.has(i) ? next.delete(i) : next.add(i);
      return next;
    });
  };

  return (
    <div className={`${styles.wrapper} ${className}`}>
      <table className={styles.table}>
        <thead>
          <tr>
            {selectable && (
              <th className={styles.checkCol}>
                <input
                  type="checkbox"
                  checked={selectedRows.size === data.length && data.length > 0}
                  onChange={toggleAll}
                  className={styles.checkbox}
                />
              </th>
            )}
            {columns.map((col) => (
              <th
                key={col.key}
                className={`${styles.th} ${col.sortable ? styles.sortable : ''}`}
                onClick={() => handleSort(col.key)}
              >
                {col.header}
                {col.sortable && sortKey === col.key && (
                  <span className={styles.sortIcon}>
                    {sortDir === 'asc' ? '↑' : '↓'}
                  </span>
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sortedData.map((row, i) => {
            const accent = rowAccentColor ? rowAccentColor(row) : null;
            return (
              <tr
                key={row.id || i}
                className={`${styles.row} ${onRowClick ? styles.clickable : ''}`}
                onClick={() => onRowClick?.(row, i)}
                style={accent ? { '--row-accent': accent } : undefined}
              >
                {selectable && (
                  <td className={styles.checkCol} onClick={(e) => e.stopPropagation()}>
                    <input
                      type="checkbox"
                      checked={selectedRows.has(i)}
                      onChange={() => toggleRow(i)}
                      className={styles.checkbox}
                    />
                  </td>
                )}
                {columns.map((col) => (
                  <td key={col.key} className={styles.td}>
                    {col.render ? col.render(row[col.key], row) : row[col.key]}
                  </td>
                ))}
                {accent && <div className={styles.rowAccent} />}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
