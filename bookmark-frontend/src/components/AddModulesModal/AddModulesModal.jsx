import { useState, useEffect } from 'react';
import styles from './AddModulesModal.module.css';
import { modulesAPI } from '../../api/apiGateway';

/* ============================================================
   ADD MODULES MODAL — Install/activate Odoo modules
   Super-admin only. Loads live data from ir.module.module.
   Custom (edu_mang_*) modules are excluded — they have their
   own React front-end tiles on the main dashboard.
   ============================================================ */

function isOpenEduCat(name) {
  return name.startsWith('openeducat_') || name === 'theme_web_openeducat';
}

function isCustom(name) {
  return name.startsWith('edu_mang_') || name.startsWith('custom_') || name === 'edu_portal_gateway';
}

export default function AddModulesModal({ isOpen, onClose }) {
  const [modules, setModules] = useState([]);
  const [loading, setLoading] = useState(false);
  const [fetchError, setFetchError] = useState(null);
  const [installing, setInstalling] = useState(null);
  const [installError, setInstallError] = useState(null);
  const [justInstalled, setJustInstalled] = useState(new Set());
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    if (!isOpen) {
      setSearchTerm('');
      setInstallError(null);
      return;
    }
    let cancelled = false;
    setLoading(true);
    setFetchError(null);
    modulesAPI.listModules()
      .then((data) => {
        if (!cancelled) setModules(Array.isArray(data) ? data : []);
      })
      .catch((err) => {
        if (!cancelled) setFetchError(err.response?.data?.detail || err.message || 'Failed to load modules');
      })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [isOpen]);

  const handleInstall = async (moduleName) => {
    setInstalling(moduleName);
    setInstallError(null);
    try {
      await modulesAPI.installModule(moduleName);
      setJustInstalled((prev) => new Set([...prev, moduleName]));
      // Optimistically update state in the list
      setModules((prev) =>
        prev.map((m) => m.name === moduleName ? { ...m, state: 'installed' } : m)
      );
    } catch (err) {
      setInstallError(`Failed to install ${moduleName}: ${err.response?.data?.detail || err.message}`);
    } finally {
      setInstalling(null);
    }
  };

  if (!isOpen) return null;

  // Partition modules: exclude custom front-end modules entirely
  const visible = modules.filter((m) => !isCustom(m.name));
  const term = searchTerm.toLowerCase();
  const filtered = term
    ? visible.filter((m) =>
        m.name.toLowerCase().includes(term) ||
        (m.shortdesc || '').toLowerCase().includes(term)
      )
    : visible;

  const openeducat = filtered.filter((m) => isOpenEduCat(m.name));
  const standard = filtered.filter((m) => !isOpenEduCat(m.name));

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className={styles.header}>
          <div>
            <h2 className={styles.title}>Add Odoo Modules</h2>
            <p className={styles.subtitle}>
              Install standard Odoo applications and view active OpenEduCat platform modules.
            </p>
          </div>
          <button className={styles.closeBtn} onClick={onClose} aria-label="Close modal">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M15 5L5 15M5 5l10 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </button>
        </div>

        {/* Search */}
        <div className={styles.searchWrap}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" className={styles.searchIcon}>
            <circle cx="11" cy="11" r="7" stroke="#7a7a72" strokeWidth="2" />
            <path d="M16 16l4 4" stroke="#7a7a72" strokeWidth="2" strokeLinecap="round" />
          </svg>
          <input
            type="text"
            placeholder="Search modules..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className={styles.searchInput}
          />
        </div>

        {/* Loading */}
        {loading && (
          <div className={styles.empty}>Loading modules from Odoo&hellip;</div>
        )}

        {/* Fetch error */}
        {fetchError && !loading && (
          <div className={styles.error}>
            <span>⚠️</span> {fetchError}
          </div>
        )}

        {/* Install error */}
        {installError && (
          <div className={styles.error}>
            <span>⚠️</span> {installError}
          </div>
        )}

        {!loading && !fetchError && (
          <>
            {/* Standard Odoo Modules */}
            {standard.length > 0 && (
              <>
                <h3 className={styles.sectionTitle}>Standard Odoo Modules</h3>
                <div className={styles.grid}>
                  {standard.map((mod) => {
                    const isInstalled = mod.state === 'installed' || justInstalled.has(mod.name);
                    const isInstalling = installing === mod.name;
                    return (
                      <div key={mod.name} className={styles.moduleCard}>
                        <div className={styles.moduleInfo}>
                          <span className={styles.moduleName}>{mod.shortdesc || mod.name}</span>
                          <span className={styles.moduleDesc}>{mod.summary || mod.name}</span>
                        </div>
                        <button
                          className={`${styles.installBtn} ${isInstalled ? styles.installed : ''}`}
                          onClick={() => handleInstall(mod.name)}
                          disabled={isInstalled || isInstalling}
                        >
                          {isInstalling ? (
                            <span className={styles.spinner} />
                          ) : isInstalled ? (
                            '✓ Installed'
                          ) : (
                            'Install'
                          )}
                        </button>
                      </div>
                    );
                  })}
                </div>
              </>
            )}

            {/* OpenEduCat Platform */}
            {openeducat.length > 0 && (
              <>
                <h3 className={styles.sectionTitle}>OpenEduCat Platform</h3>
                <div className={styles.grid}>
                  {openeducat.map((mod) => {
                    const isInstalled = mod.state === 'installed';
                    return (
                      <div key={mod.name} className={styles.moduleCard}>
                        <div className={styles.moduleInfo}>
                          <span className={styles.moduleName}>{mod.shortdesc || mod.name}</span>
                          <span className={styles.moduleDesc}>{mod.summary || mod.name}</span>
                        </div>
                        <span className={`${styles.installBtn} ${isInstalled ? styles.installed : styles.inactiveTag}`}>
                          {isInstalled ? '✓ Active' : 'Inactive'}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </>
            )}

            {!loading && filtered.length === 0 && (
              <div className={styles.empty}>
                {searchTerm ? 'No modules match your search.' : 'No modules returned from Odoo.'}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
