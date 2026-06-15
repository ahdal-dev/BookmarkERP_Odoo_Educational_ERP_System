import { useState, useRef, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import styles from './TopBar.module.css';

/* ============================================================
   TOP BAR — Light header with search, notifications, avatar
   Used on User Management and Admissions pages.
   ============================================================ */

export default function TopBar({ searchPlaceholder = 'Search users, roles, or departments...' }) {
  const { user, logout } = useAuth();
  const [searchValue, setSearchValue] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClick = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  return (
    <div className={styles.topBar}>
      {/* Brand + Search */}
      <div className={styles.left}>
        <span className={styles.brandName}>Bookmark</span>
        <div className={styles.searchWrap}>
          <input
            type="text"
            className={styles.searchInput}
            placeholder={searchPlaceholder}
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
          />
          <button className={styles.searchBtn} aria-label="Search">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.5" strokeLinecap="round">
              <circle cx="11" cy="11" r="8" /><path d="M21 21l-4.35-4.35" />
            </svg>
          </button>
        </div>
      </div>

      {/* Right Actions */}
      <div className={styles.right}>
        {/* Notification Bell */}
        <button className={styles.iconBtn} aria-label="Notifications">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
            <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9" />
            <path d="M13.73 21a2 2 0 01-3.46 0" />
          </svg>
          <span className={styles.badge}>1</span>
        </button>

        {/* Chat */}
        <button className={styles.iconBtn} aria-label="Messages">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" />
          </svg>
        </button>

        {/* Avatar Dropdown */}
        <div className={styles.avatarWrap} ref={dropdownRef}>
          <button
            className={styles.avatar}
            onClick={() => setShowDropdown(!showDropdown)}
            aria-label="User menu"
          >
            <span className={styles.avatarInitial}>
              {user?.name?.charAt(0)?.toUpperCase() || 'U'}
            </span>
          </button>
          {showDropdown && (
            <div className={styles.dropdown}>
              <div className={styles.dropdownHeader}>
                <strong>{user?.name || 'User'}</strong>
                <span>{user?.email || ''}</span>
              </div>
              <hr className={styles.divider} />
              <button className={styles.dropdownItem} onClick={logout}>
                Sign Out
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
