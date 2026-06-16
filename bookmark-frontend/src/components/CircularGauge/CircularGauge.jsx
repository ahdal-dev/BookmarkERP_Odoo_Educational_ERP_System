import styles from './CircularGauge.module.css';

/* ============================================================
   CIRCULAR GAUGE — SVG ring progress on a dark card
   ============================================================ */

export default function CircularGauge({ value = 0, label, caption }) {
  const radius = 70;
  const stroke = 10;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (value / 100) * circumference;

  return (
    <div className={styles.card}>
      {caption && <span className={styles.caption}>{caption}</span>}

      <div className={styles.gaugeWrap}>
        <svg
          width="170"
          height="170"
          viewBox="0 0 170 170"
          className={styles.svg}
        >
          {/* Background ring */}
          <circle
            cx="85"
            cy="85"
            r={radius}
            fill="none"
            stroke="rgba(255,255,255,0.1)"
            strokeWidth={stroke}
          />
          {/* Progress ring */}
          <circle
            cx="85"
            cy="85"
            r={radius}
            fill="none"
            stroke="var(--color-lime)"
            strokeWidth={stroke}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            transform="rotate(-90 85 85)"
            className={styles.progress}
          />
        </svg>
        <div className={styles.valueOverlay}>
          <span className={styles.value}>{value}%</span>
          <span className={styles.valueLabel}>of capacity reached</span>
        </div>
      </div>

      {label && <span className={styles.label}>{label}</span>}
    </div>
  );
}
