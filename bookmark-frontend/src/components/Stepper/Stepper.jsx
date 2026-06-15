import styles from './Stepper.module.css';

/* ============================================================
   STEPPER — Horizontal step indicator
   Completed = black circle + checkmark
   Active = lime-green numbered circle
   Future = gray numbered circle
   ============================================================ */

export default function Stepper({ steps = [] }) {
  return (
    <div className={styles.stepper}>
      {steps.map((step, i) => (
        <div key={i} className={styles.stepGroup}>
          {/* Connector line (before step, except first) */}
          {i > 0 && (
            <div
              className={`${styles.line} ${
                step.status === 'completed' ? styles.lineSolid :
                step.status === 'active' ? styles.lineDashed :
                styles.lineDashed
              }`}
            />
          )}

          {/* Step circle + label */}
          <div className={styles.step}>
            <div className={`${styles.circle} ${styles[step.status]}`}>
              {step.status === 'completed' ? (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M20 6L9 17l-5-5" />
                </svg>
              ) : (
                <span className={styles.number}>{i + 1}</span>
              )}
            </div>
            <div className={styles.labelWrap}>
              <span className={styles.stepLabel}>Step {i + 1}:</span>
              <span className={styles.stepTitle}>{step.label}</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
