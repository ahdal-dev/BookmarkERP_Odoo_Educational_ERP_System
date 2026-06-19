import { useState } from 'react';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import ToggleSwitch from '../../components/ToggleSwitch/ToggleSwitch';
import { registrarNav } from '../../config/navConfigs';
import w from '../_shared/workflow.module.css';

/* Registrar — priority-based registration window builder. */

const TIERS = [
  { id: 1, name: 'Tier 1 — Seniors', count: 612, open: '2026-05-17', close: '2026-12-17', cap: 1500, credits: 21, notify: true },
  { id: 2, name: 'Tier 2 — Juniors', count: 884, open: '2026-06-29', close: '2026-10-29', cap: 1500, credits: 18, notify: true },
  { id: 3, name: 'Tier 3 — Sophomores', count: 921, open: '2026-09-21', close: '2026-10-11', cap: 1500, credits: 18, notify: false },
  { id: 4, name: 'Tier 4 — Freshmen', count: 1003, open: '2026-09-28', close: '2026-10-18', cap: 1500, credits: 16, notify: false },
];

export default function TimeSlotConfiguratorPage() {
  const [tiers, setTiers] = useState(TIERS);
  const [selectedId, setSelectedId] = useState(TIERS[0].id);
  const selected = tiers.find((t) => t.id === selectedId);

  const update = (patch) => setTiers((prev) => prev.map((t) => (t.id === selectedId ? { ...t, ...patch } : t)));

  return (
    <AppShell navItems={registrarNav} logoVariant="stacked" sidebarLabel="REGISTRAR">
      <div className={w.breadcrumb}>Registrar › Configuration › Time Slot Configurator</div>
      <PageHeader title="Registration Window Builder" subtitle="Define priority tiers and their registration windows for Fall 2026" useBrandFont />

      <div className={w.splitWide}>
        {/* Tier priority order */}
        <div className={`${w.card} ${w.cardAccent}`}>
          <h3 className={w.cardTitle}>Tier Priority Order</h3>
          <p className={w.cardSub}>Drag to reorder · click to configure</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {tiers.map((t) => (
              <div key={t.id} onClick={() => setSelectedId(t.id)}
                   style={{ display: 'flex', alignItems: 'center', gap: 12, padding: 14, borderRadius: 10, cursor: 'pointer',
                            border: `1.5px solid ${t.id === selectedId ? 'var(--color-lime)' : 'var(--color-border-light)'}`,
                            background: t.id === selectedId ? 'rgba(76,175,39,0.06)' : '#fff' }}>
                <span style={{ color: 'var(--color-text-muted)', cursor: 'grab', fontSize: '1.1rem' }}>⠿</span>
                <span style={{ flex: 1, fontWeight: 600 }}>{t.name}</span>
                <span style={{ fontSize: '0.72rem', background: 'var(--color-bg-warm)', padding: '2px 10px', borderRadius: 999, color: 'var(--color-text-muted)' }}>{t.count} students</span>
              </div>
            ))}
          </div>
        </div>

        {/* Tier configuration form */}
        <div className={w.card}>
          <h3 className={w.cardTitle}>{selected.name}</h3>
          <p className={w.cardSub}>Window & capacity configuration</p>

          <div className={w.field}><span className={w.fieldLabel}>Tier Name</span><input className={w.input} value={selected.name} onChange={(e) => update({ name: e.target.value })} /></div>
          <div className={w.cardGrid2}>
            <div className={w.field}><span className={w.fieldLabel}>Open Date</span><input type="date" className={w.input} value={selected.open} onChange={(e) => update({ open: e.target.value })} /></div>
            <div className={w.field}><span className={w.fieldLabel}>Close Date</span><input type="date" className={w.input} value={selected.close} onChange={(e) => update({ close: e.target.value })} /></div>
          </div>
          <div className={w.cardGrid2}>
            <div className={w.field}><span className={w.fieldLabel}>Max Capacity</span><input type="number" className={w.input} value={selected.cap} onChange={(e) => update({ cap: +e.target.value })} /></div>
            <div className={w.field}><span className={w.fieldLabel}>Max Credits Allowed</span><input type="number" className={w.input} value={selected.credits} onChange={(e) => update({ credits: +e.target.value })} /></div>
          </div>
          <div style={{ margin: '8px 0 4px' }}>
            <ToggleSwitch checked={selected.notify} onChange={(v) => update({ notify: v })} label="Notify Students When Window Opens" description="Send an email + in-portal alert" />
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12, marginTop: 20 }}>
        <button className={`${w.btn} ${w.btnOutline}`}>Discard Changes</button>
        <button className={`${w.btn} ${w.btnPrimary}`}>Commit Changes</button>
      </div>
      <div className={w.readonlyBar} style={{ textTransform: 'uppercase', letterSpacing: '0.04em', fontWeight: 600 }}>
        ✓ Ruleset Engine Online · Last Modified Just Now · Export PDF · Change Log
      </div>
    </AppShell>
  );
}
