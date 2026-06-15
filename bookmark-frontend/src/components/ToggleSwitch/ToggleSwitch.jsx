import styles from './ToggleSwitch.module.css';

/* ============================================================
   TOGGLE SWITCH — Pill toggle, lime-green when on
   With label, description, and optional icon.
   ============================================================ */

export default function ToggleSwitch({ checked, onChange, label, description, icon }) {
  return (
    <div className={styles.wrapper}>
      {icon && <span className={styles.icon}>{icon}</span>}
      <div className={styles.text}>
        <span className={styles.label}>{label}</span>
        {description && <span className={styles.description}>{description}</span>}
      </div>
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        className={`${styles.toggle} ${checked ? styles.on : ''}`}
        onClick={() => onChange(!checked)}
      >
        <span className={styles.thumb} />
      </button>
    </div>
  );
}
