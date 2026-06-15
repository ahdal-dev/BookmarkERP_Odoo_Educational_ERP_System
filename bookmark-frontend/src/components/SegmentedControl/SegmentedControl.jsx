import styles from './SegmentedControl.module.css';

/* ============================================================
   SEGMENTED CONTROL — Pill toggle for filtering/view modes
   Active option rendered as black pill, inactive as transparent.
   ============================================================ */

export default function SegmentedControl({ options, value, onChange }) {
  return (
    <div className={styles.wrapper}>
      {options.map((opt) => {
        const optValue = typeof opt === 'string' ? opt : opt.value;
        const optLabel = typeof opt === 'string' ? opt : opt.label;
        const isActive = optValue === value;

        return (
          <button
            key={optValue}
            className={`${styles.option} ${isActive ? styles.active : ''}`}
            onClick={() => onChange(optValue)}
            type="button"
          >
            {optLabel}
          </button>
        );
      })}
    </div>
  );
}
