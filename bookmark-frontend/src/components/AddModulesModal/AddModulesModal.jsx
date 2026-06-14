import { useState, useEffect } from 'react';
import styles from './AddModulesModal.module.css';
import { modulesAPI } from '../../api/apiGateway';
import { BRAND } from '../../styles/brand';

/* ============================================================
   ADD MODULES MODAL — Install/activate Odoo core modules
   Super-admin only functionality
   ============================================================ */

const CORE_MODULES = [
  { name: 'sale', label: 'Sales', icon: '💰', description: 'Quotations, sales orders, invoicing' },
  { name: 'purchase', label: 'Purchase', icon: '🛒', description: 'Vendor management, purchase orders' },
  { name: 'account', label: 'Accounting', icon: '📊', description: 'Invoicing, payments, reports' },
  { name: 'hr', label: 'Human Resources', icon: '👥', description: 'Employee management, departments' },
  { name: 'project', label: 'Project', icon: '📋', description: 'Project planning, task management' },
  { name: 'calendar', label: 'Calendar', icon: '📅', description: 'Events, scheduling, reminders' },
  { name: 'contacts', label: 'Contacts', icon: '📇', description: 'Contact directory, address book' },
  { name: 'website', label: 'Website', icon: '🌐', description: 'Website builder, CMS' },
  { name: 'stock', label: 'Inventory', icon: '📦', description: 'Warehouse, stock management' },
  { name: 'crm', label: 'CRM', icon: '🎯', description: 'Leads, opportunities, pipeline' },
  { name: 'fleet', label: 'Fleet', icon: '🚗', description: 'Vehicle management' },
  { name: 'survey', label: 'Survey', icon: '📝', description: 'Surveys, questionnaires' },
];

export default function AddModulesModal({ isOpen, onClose }) {
  const [installing, setInstalling] = useState(null);
  const [installed, setInstalled] = useState(new Set());
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    if (!isOpen) {
      setSearchTerm('');
      setError(null);
    }
  }, [isOpen]);

  const handleInstall = async (moduleName) => {
    setInstalling(moduleName);
    setError(null);
    try {
      await modulesAPI.installModule(moduleName);
      setInstalled((prev) => new Set([...prev, moduleName]));
    } catch (err) {
      setError(`Failed to install ${moduleName}: ${err.response?.data?.detail || err.message}`);
    } finally {
      setInstalling(null);
    }
  };

  const filteredModules = CORE_MODULES.filter(
    (m) =>
      m.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
      m.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (!isOpen) return null;

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className={styles.header}>
          <div>
            <h2 className={styles.title}>Add Core Odoo Modules</h2>
            <p className={styles.subtitle}>
              Install standard Odoo applications to extend your ERP capabilities.
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

        {/* Error */}
        {error && (
          <div className={styles.error}>
            <span>⚠️</span> {error}
          </div>
        )}

        {/* Module Grid */}
        <div className={styles.grid}>
          {filteredModules.map((mod) => {
            const isInstalled = installed.has(mod.name);
            const isInstalling = installing === mod.name;

            return (
              <div key={mod.name} className={styles.moduleCard}>
                <div className={styles.moduleIcon}>{mod.icon}</div>
                <div className={styles.moduleInfo}>
                  <span className={styles.moduleName}>{mod.label}</span>
                  <span className={styles.moduleDesc}>{mod.description}</span>
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

        {filteredModules.length === 0 && (
          <div className={styles.empty}>No modules match your search.</div>
        )}
      </div>
    </div>
  );
}
