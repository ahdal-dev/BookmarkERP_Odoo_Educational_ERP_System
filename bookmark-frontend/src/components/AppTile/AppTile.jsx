import { HoverTile, SplatterDot } from '../../styles/brand';
import styles from './AppTile.module.css';

/* ============================================================
   APP TILE — Dashboard module card with hover effects
   ============================================================ */

export default function AppTile({ icon, label, description, onClick }) {
  return (
    <HoverTile onClick={onClick} className={styles.tile} role="button" tabIndex={0}>
      {/* Hover splatters — hidden by default, shown on hover via styled-components */}
      <SplatterDot
        className="hover-splatter"
        color="#e8613a"
        size={8}
        top="-6px"
        right="-6px"
        delay="0s"
      />
      <SplatterDot
        className="hover-splatter"
        color="#f5c842"
        size={6}
        top="8px"
        right="-12px"
        delay="0.1s"
      />
      <SplatterDot
        className="hover-splatter"
        color="#e8613a"
        size={10}
        bottom="-8px"
        left="-8px"
        delay="0.05s"
      />
      <SplatterDot
        className="hover-splatter"
        color="#f5c842"
        size={5}
        bottom="10px"
        left="-14px"
        delay="0.15s"
      />

      {/* Icon */}
      <div className={`tile-icon ${styles.iconWrap}`}>
        {icon}
      </div>

      {/* Label */}
      <span className={styles.label}>{label}</span>
      {description && <span className={styles.description}>{description}</span>}
    </HoverTile>
  );
}
