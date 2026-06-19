import { useState, useEffect } from 'react';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import ToggleSwitch from '../../components/ToggleSwitch/ToggleSwitch';
import CircularGauge from '../../components/CircularGauge/CircularGauge';
import { adminSettingsNav } from '../../config/navConfigs';
import { adminAPI, registrationAPI } from '../../api/apiGateway';
import { mockRuleset } from '../../mocks/rulesetMocks';
import styles from './InstitutionalRulesetPage.module.css';

/* ============================================================
   INSTITUTIONAL RULESET — Admin settings for registration rules.
   Scalar rules (toggles, GPA, application status) persist to the
   gateway (ir.config_parameter). Registration windows / prerequisite
   list have no Odoo model yet and remain UI-local structure.
   ============================================================ */

// Map gateway rules payload → form fields (rest comes from mockRuleset structure).
function mergeRules(base, rules) {
  if (!rules) return base;
  return {
    ...base,
    autoEnroll: rules.autoEnroll ?? base.autoEnroll,
    prerequisiteCheck: rules.prerequisiteCheck ?? base.prerequisiteCheck,
    waitlistManagement: rules.waitlistManagement ?? base.waitlistManagement,
    gpa: rules.minGpa || base.gpa,
    applicationStatus: rules.applicationStatus || base.applicationStatus,
    prerequisites: (Array.isArray(rules.prerequisites) && rules.prerequisites.length)
      ? rules.prerequisites
      : base.prerequisites,
  };
}

export default function InstitutionalRulesetPage() {
  const [form, setForm] = useState({ ...mockRuleset });
  const [isDirty, setDirty] = useState(false);
  const [saving, setSaving] = useState(false);

  // Load persisted scalar rules + live registration tiers on mount.
  useEffect(() => {
    let active = true;
    adminAPI.getRules()
      .then((rules) => { if (active) setForm((prev) => mergeRules(prev, rules)); })
      .catch(() => { /* keep defaults if endpoint unavailable */ });
    registrationAPI.getTiers()
      .then((res) => {
        if (!active || !res?.tiers) return;
        const windows = res.tiers.map((t) => ({
          tier: t.name,
          openDate: t.registration_start || '—',
          closeDate: t.registration_end || '—',
          capacity: t.credit_range,
          color: t.color || 'var(--color-lime)',
        }));
        setForm((prev) => ({ ...prev, registrationWindows: windows }));
      })
      .catch(() => { /* keep mock windows if endpoint unavailable */ });
    return () => { active = false; };
  }, []);

  const update = (key, value) => {
    setForm((prev) => ({ ...prev, [key]: value }));
    setDirty(true);
  };

  const togglePrereq = (index) => {
    const next = [...form.prerequisites];
    next[index] = { ...next[index], checked: !next[index].checked };
    update('prerequisites', next);
  };

  const handleDiscard = () => {
    setForm({ ...mockRuleset });
    setDirty(false);
  };

  const handleCommit = async () => {
    setSaving(true);
    try {
      await adminAPI.updateRules({
        autoEnroll: form.autoEnroll,
        prerequisiteCheck: form.prerequisiteCheck,
        waitlistManagement: form.waitlistManagement,
        minGpa: String(form.gpa ?? ''),
        applicationStatus: form.applicationStatus,
        prerequisites: form.prerequisites,
      });
      setDirty(false);
    } catch {
      // leave dirty so the user can retry
    } finally {
      setSaving(false);
    }
  };

  return (
    <AppShell navItems={adminSettingsNav} logoVariant="stacked">
      {/* Breadcrumb */}
      <div className={styles.breadcrumb}>
        SYSTEM › CONFIGURATION › REGISTRATION & ADMISSIONS
      </div>

      {/* Action Buttons */}
      <div className={styles.actionBar}>
        <button
          className={styles.btnOutline}
          disabled={!isDirty}
          onClick={handleDiscard}
        >
          Discard Changes
        </button>
        <button
          className={styles.btnBlack}
          disabled={!isDirty || saving}
          onClick={handleCommit}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z"/><path d="M17 21v-8H7v8m0-16v5h8"/></svg>
          {saving ? 'Saving…' : 'Commit Changes'}
        </button>
      </div>

      <PageHeader
        title="Institutional Ruleset"
        subtitle="Define academic thresholds, prerequisite logic, and temporal registration windows."
      />

      {/* Main Content */}
      <div className={styles.layout}>
        {/* Left/Center Column */}
        <div className={styles.leftCol}>
          <div className={styles.cardRow}>
            {/* Ruleset Automation */}
            <div className={styles.card}>
              <h3 className={styles.cardTitle}>Ruleset Automation</h3>
              <ToggleSwitch
                checked={form.autoEnroll}
                onChange={(v) => update('autoEnroll', v)}
                label="Auto-Enroll Priority Students"
                description="Auto-enroll priority students during the registration cycle."
                icon={<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75"/></svg>}
              />
              <ToggleSwitch
                checked={form.prerequisiteCheck}
                onChange={(v) => update('prerequisiteCheck', v)}
                label="Global Prerequisite Check"
                description="Check prerequisite requirements for all course enrollments."
                icon={<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><path d="M22 4L12 14.01l-3-3"/></svg>}
              />
              <ToggleSwitch
                checked={form.waitlistManagement}
                onChange={(v) => update('waitlistManagement', v)}
                label="Waitlist Management"
                description="Manage waitlist queues for full-capacity courses."
                icon={<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6M16 13H8m8 4H8m2-8H8"/></svg>}
              />
            </div>

            {/* Admission Rules */}
            <div className={`${styles.card} ${styles.cardGreenBorder}`}>
              <h3 className={styles.cardTitle}>Admission Rules</h3>

              <div className={styles.field}>
                <label className={styles.fieldLabel}>GPA</label>
                <input
                  type="text"
                  className={styles.input}
                  value={form.gpa}
                  onChange={(e) => update('gpa', e.target.value)}
                />
              </div>

              <div className={styles.field}>
                <label className={styles.fieldLabel}>Application Status</label>
                <select
                  className={styles.selectField}
                  value={form.applicationStatus}
                  onChange={(e) => update('applicationStatus', e.target.value)}
                >
                  <option>Active – Accepting Submissions</option>
                  <option>Closed</option>
                  <option>Review Only</option>
                </select>
              </div>

              <div className={styles.field}>
                <label className={styles.fieldLabel}>Prerequisites</label>
                {form.prerequisites.map((p, i) => (
                  <label key={i} className={styles.checkRow}>
                    <input
                      type="checkbox"
                      checked={p.checked}
                      onChange={() => togglePrereq(i)}
                      className={styles.checkbox}
                    />
                    <span className={p.checked ? styles.checkGreen : styles.checkCoral}>{p.name}</span>
                  </label>
                ))}
              </div>

              <div className={styles.infoCallout}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-lime)" strokeWidth="2" strokeLinecap="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4m0-4h.01"/></svg>
                <span>Ruleset modifications take effect for the next academic cycle.</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column */}
        <div className={styles.rightCol}>
          <CircularGauge
            value={form.capacityPercent}
            label="Registration Velocity"
            caption="ACTIVE CYCLE INSIGHT"
          />

          {/* Registration Windows */}
          <div className={styles.card}>
            <h3 className={styles.cardTitle}>Registration Windows</h3>
            <table className={styles.windowsTable}>
              <thead>
                <tr>
                  <th>Tier</th>
                  <th>Open Date</th>
                  <th>Close Date</th>
                  <th>Capacity</th>
                </tr>
              </thead>
              <tbody>
                {form.registrationWindows.map((w, i) => (
                  <tr key={i} style={{ '--row-tint': w.color }}>
                    <td><span className={styles.tierBadge} style={{ background: w.color, color: '#fff' }}>{w.tier}</span></td>
                    <td>{w.openDate}</td>
                    <td>{w.closeDate}</td>
                    <td>{w.capacity}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Sticky Footer */}
      <div className={styles.footer}>
        <div className={styles.footerLeft}>
          <span className={styles.statusDot} />
          <span className={styles.statusText}>RULESET ENGINE ONLINE</span>
        </div>
        <div className={styles.footerRight}>
          <span className={styles.footerLink} style={{ cursor: 'pointer' }} onClick={() => window.print()}>EXPORT PDF</span>
        </div>
      </div>
    </AppShell>
  );
}
