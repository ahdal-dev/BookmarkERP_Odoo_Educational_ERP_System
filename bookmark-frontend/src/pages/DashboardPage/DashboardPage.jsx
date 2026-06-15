import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import AppTile from '../../components/AppTile/AppTile';
import AddModulesModal from '../../components/AddModulesModal/AddModulesModal';
import { SplatterDot } from '../../styles/brand';
import styles from './DashboardPage.module.css';
import logoUrl from '../../assets/logos/bookark_logo.svg';

/* ============================================================
   DASHBOARD PAGE — App Launcher Grid
   3×2 grid of module tiles + Backend button + FAB
   ============================================================ */

/* --- Module Icon SVGs --- */
const RegistrationIcon = () => (
  <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="10" y="4" width="28" height="40" rx="3" stroke="currentColor" strokeWidth="2.5" />
    <path d="M18 16h12M18 24h12M18 32h8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    <path d="M15 16l1.5 1.5L19 15" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M15 24l1.5 1.5L19 23" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    <circle cx="16.5" cy="32" r="1.5" fill="currentColor" />
  </svg>
);

const AdmissionIcon = () => (
  <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M24 4L6 14v4h36v-4L24 4z" stroke="currentColor" strokeWidth="2.5" strokeLinejoin="round" />
    <rect x="12" y="18" width="24" height="22" rx="1" stroke="currentColor" strokeWidth="2" />
    <path d="M20 27l4 4 6-8" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
    <circle cx="24" cy="11" r="3" stroke="currentColor" strokeWidth="1.5" />
  </svg>
);

const AuthenticationIcon = () => (
  <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="10" y="20" width="20" height="18" rx="3" stroke="currentColor" strokeWidth="2.5" />
    <path d="M15 20v-6a5 5 0 0110 0v6" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
    <circle cx="20" cy="29" r="2.5" fill="currentColor" />
    <path d="M20 31v3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    <path d="M34 18l6-6M34 12l6 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    <path d="M34 24h8M34 30h6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
  </svg>
);

const PetitionIcon = () => (
  <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 4h18l8 8v32a2 2 0 01-2 2H12a2 2 0 01-2-2V6a2 2 0 012-2z" stroke="currentColor" strokeWidth="2.5" strokeLinejoin="round" />
    <path d="M30 4v8h8" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
    <path d="M16 20h16M16 26h16M16 32h10" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    <path d="M34 34c-2-1-4 1-3 3l2 6 3-4c1-1.5 0-4-2-5z" stroke="currentColor" strokeWidth="1.5" fill="none" />
  </svg>
);

const WebsiteIcon = () => (
  <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="4" y="6" width="40" height="30" rx="3" stroke="currentColor" strokeWidth="2.5" />
    <line x1="4" y1="14" x2="44" y2="14" stroke="currentColor" strokeWidth="2" />
    <circle cx="9" cy="10" r="1.5" fill="currentColor" />
    <circle cx="14" cy="10" r="1.5" fill="currentColor" />
    <circle cx="19" cy="10" r="1.5" fill="currentColor" />
    <path d="M24 42l-6-6h12l-6 6z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
    <circle cx="30" cy="26" r="6" stroke="currentColor" strokeWidth="1.8" />
    <path d="M30 20v12M24 26h12" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
    <ellipse cx="30" cy="26" rx="3" ry="6" stroke="currentColor" strokeWidth="1" />
  </svg>
);

const PortalGatewayIcon = () => (
  <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M8 44V18a16 16 0 0132 0v26" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
    <rect x="16" y="28" width="16" height="16" rx="1" stroke="currentColor" strokeWidth="2" />
    <path d="M24 28v-10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    <circle cx="24" cy="14" r="3" stroke="currentColor" strokeWidth="1.5" />
    <line x1="8" y1="44" x2="40" y2="44" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
    <path d="M12 44V22M36 44V22" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
  </svg>
);

const MODULES = [
  { key: 'registration', label: 'Registration', icon: <RegistrationIcon />, description: 'Course catalog & enrollment' },
  { key: 'admission', label: 'Admission', icon: <AdmissionIcon />, description: 'Applications & reviews' },
  { key: 'authentication', label: 'Authentication', icon: <AuthenticationIcon />, description: 'Users, roles & access' },
  { key: 'petition', label: 'Petition', icon: <PetitionIcon />, description: 'Student requests & approvals' },
  { key: 'website', label: 'Website', icon: <WebsiteIcon />, description: 'Public portal & CMS' },
  { key: 'portal-gateway', label: 'Portal Gateway', icon: <PortalGatewayIcon />, description: 'Secure portal routing' },
];

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  const odooBackendUrl = import.meta.env.VITE_ODOO_URL || 'http://localhost:8081';

  const handleModuleClick = (moduleKey) => {
    // In production, navigate to the module's sub-page
    console.log(`Navigate to module: ${moduleKey}`);
  };

  const handleLogout = async () => {
    await logout();
  };

  return (
    <div className={styles.page}>
      {/* ===== HEADER ===== */}
      <header className={styles.header}>
        <div className={styles.headerLeft}>
          <img src={logoUrl} alt="Bookmark Logo" style={{ height: '36px', width: 'auto', objectFit: 'contain' }} />
        </div>

        <div className={styles.headerRight}>
          {/* Backend Button */}
          <a
            href={`${odooBackendUrl}/web`}
            target="_blank"
            rel="noopener noreferrer"
            className={styles.backendBtn}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <rect x="3" y="3" width="7" height="7" rx="1" stroke="currentColor" strokeWidth="2" />
              <rect x="14" y="3" width="7" height="7" rx="1" stroke="currentColor" strokeWidth="2" />
              <rect x="3" y="14" width="7" height="7" rx="1" stroke="currentColor" strokeWidth="2" />
              <rect x="14" y="14" width="7" height="7" rx="1" stroke="currentColor" strokeWidth="2" />
            </svg>
            Backend
          </a>

          {/* User Avatar */}
          <div className={styles.avatarWrap}>
            <button
              className={styles.avatar}
              onClick={() => setUserMenuOpen(!userMenuOpen)}
              aria-label="User menu"
            >
              <span className={styles.avatarInitial}>
                {user?.name?.charAt(0)?.toUpperCase() || 'U'}
              </span>
              <span className={styles.statusDot} />
            </button>

            {/* Dropdown */}
            {userMenuOpen && (
              <div className={styles.dropdown}>
                <div className={styles.dropdownHeader}>
                  <span className={styles.dropdownName}>{user?.name || 'User'}</span>
                  <span className={styles.dropdownEmail}>{user?.email || ''}</span>
                </div>
                <hr className={styles.dropdownDivider} />
                <button className={styles.dropdownItem} onClick={handleLogout}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                    <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    <polyline points="16,17 21,12 16,7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    <line x1="21" y1="12" x2="9" y2="12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                  </svg>
                  Sign Out
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* ===== MAIN CONTENT ===== */}
      <main className={styles.main}>
        {/* Title Section */}
        <div className={styles.titleSection}>
          <div className={styles.titleWrap}>
            <SplatterDot color="#e8613a" size={12} top="-8px" left="-20px" delay="0.2s" $animate />
            <SplatterDot color="#f5c842" size={8} top="-16px" right="-16px" delay="0.3s" />
            <SplatterDot color="#e8613a" size={6} bottom="-4px" right="-24px" delay="0.5s" $animate />
            <SplatterDot color="#f5c842" size={14} top="4px" right="-40px" delay="0.4s" $animate />
            <h1 className={styles.title}>Institution Applications</h1>
          </div>
          <p className={styles.subtitle}>
            Select a module to manage your academic operations.
          </p>
        </div>

        {/* Module Grid */}
        <div className={styles.grid}>
          {MODULES.map((mod, index) => (
            <div
              key={mod.key}
              className={styles.gridItem}
              style={{ animationDelay: `${index * 0.08}s` }}
            >
              <AppTile
                icon={mod.icon}
                label={mod.label}
                description={mod.description}
                onClick={() => handleModuleClick(mod.key)}
              />
            </div>
          ))}
        </div>
      </main>

      {/* ===== FAB — Add Core Odoo Modules ===== */}
      <button
        className={styles.fab}
        onClick={() => setIsModalOpen(true)}
        aria-label="Add Core Odoo Modules"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
          <line x1="12" y1="5" x2="12" y2="19" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
          <line x1="5" y1="12" x2="19" y2="12" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
        </svg>
        <span className={styles.fabLabel}>Add Core Odoo Modules</span>
      </button>

      {/* ===== Modal ===== */}
      <AddModulesModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />

      {/* Click-away listener for user menu */}
      {userMenuOpen && (
        <div className={styles.overlay} onClick={() => setUserMenuOpen(false)} />
      )}
    </div>
  );
}
