import styles from './BookmarkLogo.module.css';
import markUrl from '../../assets/logos/bookark_logo.svg';
import wordmarkUrl from '../../assets/logos/Bookmark.svg';

/* ============================================================
   BOOKMARK LOGO — Hand-sketched book+plus mark in its own
   black brush-circle (the SVG already carries the green rim
   and paint splatters). We cross-fade the icon mark with the
   "Bookmark" wordmark for a lively, switching brand animation.
   ============================================================ */

export default function BookmarkLogo({ size = 'large', animate = true }) {
  const box = size === 'large' ? 240 : size === 'medium' ? 120 : 48;

  return (
    <div
      className={`${styles.logoWrapper} ${animate ? styles.animate : ''}`}
      style={{ width: box, height: box }}
    >
      {/* Soft glow that pulses behind the active mark */}
      <span className={styles.glow} aria-hidden="true" />

      {/* Frame A — the book+plus circle mark */}
      <img
        src={markUrl}
        alt="Bookmark Logo"
        className={`${styles.frame} ${styles.frameMark}`}
      />

      {/* Frame B — the "Bookmark" wordmark */}
      <img
        src={wordmarkUrl}
        alt=""
        aria-hidden="true"
        className={`${styles.frame} ${styles.frameWord}`}
      />
    </div>
  );
}
