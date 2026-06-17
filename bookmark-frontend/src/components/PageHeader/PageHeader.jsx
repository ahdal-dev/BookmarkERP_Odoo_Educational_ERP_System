import { SplatterDot } from '../../styles/brand';
import styles from './PageHeader.module.css';

/* ============================================================
   PAGE HEADER — Large heading with optional pill badge,
   subtitle, splatter accents, and action button slot.
   ============================================================ */

export default function PageHeader({
  title,
  subtitle,
  badge,
  badgeVariant = 'green',
  actions,
  useBrandFont = false,
  className = '',
}) {
  return (
    <div className={`${styles.header} ${className}`}>
      <div className={styles.titleRow}>
        <div className={styles.titleGroup}>
          <h1 className={`${styles.title} ${useBrandFont ? styles.titleBrand : ''}`}>
            {title}
            {badge && (
              <span className={`${styles.badge} ${styles[badgeVariant]}`}>
                {badge}
              </span>
            )}
          </h1>
          {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
        </div>

        {actions && <div className={styles.actions}>{actions}</div>}

        {/* Decorative splatters */}
        <SplatterDot color="#e8613a" size={14} top="-5px" right="100px" delay="0.2s" />
        <SplatterDot color="#f5c842" size={9} top="8px" right="80px" delay="0.4s" />
        <SplatterDot color="#e8613a" size={7} top="30px" right="115px" delay="0.3s" $animate />
      </div>
    </div>
  );
}
