import { useState, useEffect } from 'react';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import ToggleSwitch from '../../components/ToggleSwitch/ToggleSwitch';
import { registrarNav } from '../../config/navConfigs';
import { registrationAPI, registrarAPI } from '../../api/apiGateway';
import useAsync from '../../hooks/useAsync';
import w from '../_shared/workflow.module.css';

/* Registrar — registration window/tier builder (live, persisted). */

export default function TimeSlotConfiguratorPage() {
  const { data, loading, error, reload } = useAsync(() => registrationAPI.getTiers(), []);
  const [tiers, setTiers] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (data?.tiers) {
      setTiers(data.tiers);
      setSelectedId((prev) => prev ?? data.tiers[0]?.id ?? null);
    }
  }, [data]);

  const selected = tiers.find((t) => t.id === selectedId);
  const update = (patch) => setTiers((prev) => prev.map((t) => (t.id === selectedId ? { ...t, ...patch } : t)));

  const commit = async () => {
    if (!selected) return;
    setSaving(true);
    try {
      await registrarAPI.updateTier(selected.id, {
        registration_start: selected.registration_start || null,
        registration_end: selected.registration_end || null,
        min_credits: selected.min_credits,
        max_credits: selected.max_credits,
        notify_students: selected.notify_students,
      });
      await reload();
    } finally {
      setSaving(false);
    }
  };

  return (
    <AppShell navItems={registrarNav} logoVariant="stacked" sidebarLabel="REGISTRAR">
      <div className={w.breadcrumb}>Registrar › Configuration › Time Slot Configurator</div>
      <PageHeader title="Registration Window Builder" subtitle="Define priority tiers and their registration windows" useBrandFont />

      {loading ? <div className={w.card}><div className={w.empty}>Loading tiers…</div></div>
      : error ? <div className={w.card}><div className={w.empty}><div className={w.emptyTitle}>Couldn't load tiers</div><p>{error}</p><button className={`${w.btn} ${w.btnOutline} ${w.btnSm}`} onClick={reload}>Retry</button></div></div>
      : !selected ? <div className={w.card}><div className={w.empty}><div className={w.emptyTitle}>No tiers configured</div></div></div>
      : (
        <>
          <div className={w.splitWide}>
            <div className={`${w.card} ${w.cardAccent}`}>
              <h3 className={w.cardTitle}>Tier Priority Order</h3>
              <p className={w.cardSub}>Click to configure</p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {tiers.map((t) => (
                  <div key={t.id} onClick={() => setSelectedId(t.id)}
                       style={{ display: 'flex', alignItems: 'center', gap: 12, padding: 14, borderRadius: 10, cursor: 'pointer',
                                border: `1.5px solid ${t.id === selectedId ? 'var(--color-lime)' : 'var(--color-border-light)'}`,
                                background: t.id === selectedId ? 'rgba(76,175,39,0.06)' : '#fff' }}>
                    <span style={{ flex: 1, fontWeight: 600 }}>{t.name}</span>
                    <span style={{ fontSize: '0.72rem', background: 'var(--color-bg-warm)', padding: '2px 10px', borderRadius: 999, color: 'var(--color-text-muted)' }}>{t.credit_range}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className={w.card}>
              <h3 className={w.cardTitle}>{selected.name}</h3>
              <p className={w.cardSub}>Window &amp; eligibility configuration</p>
              <div className={w.cardGrid2}>
                <div className={w.field}><span className={w.fieldLabel}>Open Date</span><input type="date" className={w.input} value={selected.registration_start || ''} onChange={(e) => update({ registration_start: e.target.value })} /></div>
                <div className={w.field}><span className={w.fieldLabel}>Close Date</span><input type="date" className={w.input} value={selected.registration_end || ''} onChange={(e) => update({ registration_end: e.target.value })} /></div>
              </div>
              <div className={w.cardGrid2}>
                <div className={w.field}><span className={w.fieldLabel}>Min Earned Credits</span><input type="number" className={w.input} value={selected.min_credits ?? 0} onChange={(e) => update({ min_credits: +e.target.value })} /></div>
                <div className={w.field}><span className={w.fieldLabel}>Max Earned Credits (0 = none)</span><input type="number" className={w.input} value={selected.max_credits ?? 0} onChange={(e) => update({ max_credits: +e.target.value })} /></div>
              </div>
              <div style={{ margin: '8px 0 4px' }}>
                <ToggleSwitch checked={!!selected.notify_students} onChange={(v) => update({ notify_students: v })} label="Notify Students When Window Opens" description="Send an in-portal alert" />
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12, marginTop: 20 }}>
            <button className={`${w.btn} ${w.btnOutline}`} onClick={reload}>Discard Changes</button>
            <button className={`${w.btn} ${w.btnPrimary}`} onClick={commit} disabled={saving}>{saving ? 'Saving…' : 'Commit Changes'}</button>
          </div>
        </>
      )}
    </AppShell>
  );
}
