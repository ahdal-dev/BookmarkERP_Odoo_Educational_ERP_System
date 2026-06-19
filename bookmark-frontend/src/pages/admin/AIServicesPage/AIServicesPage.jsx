import { useState } from 'react';
import AppShell from '../../../components/AppShell/AppShell';
import TopBar from '../../../components/TopBar/TopBar';
import PageHeader from '../../../components/PageHeader/PageHeader';
import StatusPill from '../../../components/StatusPill/StatusPill';
import ToggleSwitch from '../../../components/ToggleSwitch/ToggleSwitch';
import useAsync from '../../../hooks/useAsync';
import { adminAPI } from '../../../api/apiGateway';
import { adminDashboardNav } from '../../../config/navConfigs';
import { mockAIServices, mockAIErrorLogs, openTicketCount } from '../../../mocks/adminMocks';
import styles from './AIServicesPage.module.css';

// AI services page — monitor, configure and enable/disable AI microservices

const navWithActive = adminDashboardNav.map((n) =>
  n.path === '/admin/ai' ? { ...n, active: true } : n
);

const STATUS_VARIANT = { Online: 'green', Degraded: 'yellow', Offline: 'coral' };

const TYPE_ICON = {
  OCR: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6"/><path d="M16 13H8m8 4H8"/></svg>
  ),
  Prediction: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><path d="M18 20V10m-6 10V4M6 20v-6"/></svg>
  ),
  RAG: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><path d="M21 11.5a8.38 8.38 0 01-.9 3.8 8.5 8.5 0 01-7.6 4.7 8.38 8.38 0 01-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 01-.9-3.8 8.5 8.5 0 014.7-7.6 8.38 8.38 0 013.8-.9h.5a8.48 8.48 0 018 8v.5z"/></svg>
  ),
  Embedding: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><circle cx="12" cy="12" r="3"/><path d="M3 12h3m12 0h3M12 3v3m0 12v3"/></svg>
  ),
};

export default function AIServicesPage() {
  const { data: liveAI } = useAsync(adminAPI.getAIServices);

  const liveServices = liveAI?.services?.map((s, i) => {
    const mock = mockAIServices[i] || mockAIServices[0];
    return {
      ...mock,
      id: i + 1,
      name: s.name,
      status: s.status === 'Healthy' ? 'Online' : s.status,
      avgLatency: (s.latency / 1000).toFixed(2),
    };
  });

  const [services, setServices] = useState(null);
  const [selected, setSelected] = useState(null);
  const [showRegister, setShowRegister] = useState(false);

  const effectiveServices = services ?? liveServices ?? mockAIServices;
  const effectiveSelected = selected ?? effectiveServices[0];

  const toggleService = (id) => {
    const base = effectiveServices;
    setServices(base.map((s) => s.id === id ? { ...s, isEnabled: !s.isEnabled } : s));
    if (effectiveSelected?.id === id) {
      setSelected((prev) => ({ ...(prev ?? effectiveSelected), isEnabled: !effectiveSelected.isEnabled }));
    }
  };

  return (
    <AppShell
      navItems={navWithActive}
      logoVariant="icon-text"
      sidebarLabel="ADMIN PANEL"
      topBar={<TopBar searchPlaceholder="Search AI services..." notificationCount={openTicketCount} />}
    >
      <div className={styles.breadcrumb}>INTELLIGENCE / AI SERVICES</div>

      <PageHeader
        title="AI Services Management"
        subtitle="Monitor, configure, and manage all AI microservices powering Bookmark ERP."
        actions={
          <button className={styles.primaryBtn} onClick={() => setShowRegister(true)}>
            + Register Service
          </button>
        }
      />

      {/* Summary Strip */}
      <div className={styles.summaryStrip}>
        {[
          { label: 'Total Services', value: effectiveServices.length },
          { label: 'Online', value: effectiveServices.filter((s) => s.status === 'Online').length, color: 'var(--color-lime)' },
          { label: 'Degraded', value: effectiveServices.filter((s) => s.status === 'Degraded').length, color: 'var(--color-yellow)' },
          { label: 'Requests Today', value: effectiveServices.reduce((a, s) => a + (s.requestsToday || 0), 0).toLocaleString() },
        ].map((item) => (
          <div key={item.label} className={styles.summaryItem}>
            <span className={styles.summaryValue} style={item.color ? { color: item.color } : {}}>
              {item.value}
            </span>
            <span className={styles.summaryLabel}>{item.label}</span>
          </div>
        ))}
      </div>

      <div className={styles.layout}>
        {/* Service Card List */}
        <div className={styles.serviceList}>
          {effectiveServices.map((svc) => (
            <div
              key={svc.id}
              className={`${styles.serviceCard} ${effectiveSelected?.id === svc.id ? styles.serviceCardActive : ''}`}
              onClick={() => setSelected(svc)}
            >
              <div className={styles.serviceCardTop}>
                <div className={`${styles.typeIcon} ${svc.status === 'Degraded' ? styles.typeIconWarn : ''}`}>
                  {TYPE_ICON[svc.type] || TYPE_ICON.Embedding}
                </div>
                <div className={styles.serviceInfo}>
                  <span className={styles.serviceName}>{svc.name}</span>
                  <span className={styles.serviceEndpoint}>{svc.endpoint}</span>
                </div>
                <StatusPill
                  status={svc.status}
                  variant={STATUS_VARIANT[svc.status] || 'black'}
                />
              </div>
              <div className={styles.serviceMetrics}>
                <span>↑ {svc.uptime}% uptime</span>
                <span>{svc.avgLatency}s avg</span>
                <span>{svc.requestsToday.toLocaleString()} req/day</span>
              </div>
              <div className={styles.serviceToggleRow}>
                <ToggleSwitch
                  checked={svc.isEnabled}
                  onChange={() => toggleService(svc.id)}
                  label={svc.isEnabled ? 'Enabled' : 'Disabled'}
                />
              </div>
            </div>
          ))}
        </div>

        {/* Detail Panel */}
        {effectiveSelected && (
          <div className={styles.detailPanel}>
            <div className={styles.detailHeader}>
              <h2 className={styles.detailTitle}>{effectiveSelected.name}</h2>
              <StatusPill status={effectiveSelected.status} variant={STATUS_VARIANT[effectiveSelected.status] || 'black'} />
            </div>

            {/* Config */}
            <div className={styles.configSection}>
              <span className={styles.sectionLabel}>CONFIGURATION</span>
              <div className={styles.configGrid}>
                <div className={styles.configField}>
                  <label className={styles.configLabel}>Endpoint URL</label>
                  <input className={styles.configInput} defaultValue={effectiveSelected.endpoint} readOnly />
                </div>
                <div className={styles.configField}>
                  <label className={styles.configLabel}>Model Version</label>
                  <input className={styles.configInput} defaultValue={effectiveSelected.modelVersion} />
                </div>
              </div>
              <button className={styles.saveConfigBtn}>Save Configuration</button>
            </div>

            {/* Stats */}
            <div className={styles.statsSection}>
              <span className={styles.sectionLabel}>PERFORMANCE — LAST 24H</span>
              <div className={styles.statsGrid}>
                {[
                  { label: 'Uptime', value: `${effectiveSelected.uptime}%`, good: effectiveSelected.uptime > 99 },
                  { label: 'Avg Latency', value: `${effectiveSelected.avgLatency}s`, good: effectiveSelected.avgLatency < 2 },
                  { label: 'P99 Latency', value: `${effectiveSelected.p99Latency}s`, good: effectiveSelected.p99Latency < 5 },
                  { label: 'Requests', value: (effectiveSelected.requestsToday || 0).toLocaleString(), good: true },
                  { label: 'Success Rate', value: `${effectiveSelected.successRate}%`, good: effectiveSelected.successRate > 95 },
                  { label: 'Error Rate', value: `${effectiveSelected.errorRate}%`, good: effectiveSelected.errorRate < 2 },
                ].map((stat) => (
                  <div key={stat.label} className={styles.statItem}>
                    <span
                      className={styles.statValue}
                      style={{ color: stat.good ? 'var(--color-lime)' : 'var(--color-coral)' }}
                    >
                      {stat.value}
                    </span>
                    <span className={styles.statLabel}>{stat.label}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Error Log */}
            <div className={styles.logSection}>
              <span className={styles.sectionLabel}>RECENT ERRORS</span>
              {mockAIErrorLogs.filter((l) => l.service === effectiveSelected.name || effectiveSelected.name.includes(l.service)).length === 0 ? (
                <p className={styles.noErrors}>No recent errors for this service.</p>
              ) : (
                <div className={styles.logList}>
                  {mockAIErrorLogs
                    .filter((l) => effectiveSelected.name.toLowerCase().includes(l.service.toLowerCase()) || l.service.toLowerCase().includes(effectiveSelected.name.toLowerCase().split(' ')[0]))
                    .map((log, i) => (
                      <div key={i} className={styles.logRow}>
                        <span className={styles.logTime}>{log.time}</span>
                        <span className={styles.logCode}>{log.code}</span>
                        <span className={styles.logDetail}>{log.detail}</span>
                      </div>
                    ))
                  }
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Register Service Modal */}
      {showRegister && (
        <div className={styles.modalOverlay} onClick={() => setShowRegister(false)}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>Register New AI Service</h2>
              <button className={styles.modalClose} onClick={() => setShowRegister(false)}>✕</button>
            </div>
            <div className={styles.modalBody}>
              {[
                { label: 'Service Name', placeholder: 'e.g. Fraud Detection Engine' },
                { label: 'Endpoint URL', placeholder: 'http://service-host:port/api/v1' },
                { label: 'Model Version', placeholder: 'e.g. v1.0.0' },
                { label: 'Health Check URL', placeholder: 'http://service-host:port/health' },
              ].map((f) => (
                <div key={f.label} className={styles.formField}>
                  <label className={styles.formLabel}>{f.label}</label>
                  <input className={styles.formInput} placeholder={f.placeholder} />
                </div>
              ))}
              <div className={styles.formField}>
                <label className={styles.formLabel}>Service Type</label>
                <select className={styles.formInput}>
                  <option>OCR</option>
                  <option>Prediction</option>
                  <option>RAG</option>
                  <option>Embedding</option>
                  <option>Custom</option>
                </select>
              </div>
            </div>
            <div className={styles.modalFooter}>
              <button className={styles.cancelBtn} onClick={() => setShowRegister(false)}>Cancel</button>
              <button className={styles.saveBtn} onClick={() => setShowRegister(false)}>Register Service</button>
            </div>
          </div>
        </div>
      )}
    </AppShell>
  );
}
