import { RoughCircle, SplatterDot } from '../../styles/brand';
import styles from './BookmarkLogo.module.css';
import logoUrl from '../../assets/logos/bookark_logo.svg';

/* ============================================================
   BOOKMARK LOGO — Hand-sketched open book in a rough circle
   with coral/yellow paint splatters
   ============================================================ */

export default function BookmarkLogo({ size = 'large' }) {
  const circleSize = size === 'large' ? 240 : size === 'medium' ? 120 : 48;
  const iconScale = size === 'large' ? 1 : size === 'medium' ? 0.5 : 0.2;

  return (
    <div className={styles.logoWrapper}>
      {/* Splatters behind/around the logo */}
      {size === 'large' && (
        <>
          <SplatterDot color="#e8613a" size={18} top="-10px" right="30px" delay="0.2s" $animate />
          <SplatterDot color="#f5c842" size={10} top="20px" right="-20px" delay="0.4s" $animate />
          <SplatterDot color="#e8613a" size={8} top="60px" right="10px" delay="0.3s" />
          <SplatterDot color="#f5c842" size={22} top="-30px" left="60%" delay="0.1s" $animate />
          <SplatterDot color="#e8613a" size={14} bottom="40px" left="-25px" delay="0.5s" />
          <SplatterDot color="#e8613a" size={28} bottom="-20px" left="-40px" delay="0.6s" $animate />
          <SplatterDot color="#f5c842" size={10} bottom="-10px" left="-15px" delay="0.7s" />
          <SplatterDot color="#e8613a" size={12} bottom="80px" left="-35px" delay="0.4s" />
          <SplatterDot color="#f5c842" size={16} top="10%" right="-30px" delay="0.5s" $animate />
        </>
      )}

      <RoughCircle size={circleSize}>
        {/* Inner dark circle background */}
        <div
          className={styles.innerCircle}
          style={{
            width: circleSize * 0.85,
            height: circleSize * 0.85,
          }}
        >
          {/* SVG Book Icon */}
          <img
            src={logoUrl}
            alt="Bookmark Logo"
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'contain'
            }}
          />
        </div>
      </RoughCircle>
    </div>
  );
}
