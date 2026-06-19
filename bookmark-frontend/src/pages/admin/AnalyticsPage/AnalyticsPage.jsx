import { useState } from 'react';
import AppShell from '../../../components/AppShell/AppShell';
import TopBar from '../../../components/TopBar/TopBar';
import PageHeader from '../../../components/PageHeader/PageHeader';
import StatusPill from '../../../components/StatusPill/StatusPill';
import { adminDashboardNav } from '../../../config/navConfigs';
import {
  mockAnalyticsByPeriod,
  mockAdmissionFunnel,
  mockServiceHealthTable,
  openTicketCount,
} from '../../../mocks/adminMocks';
import styles from './AnalyticsPage.module.css';

// Analytics & monitoring dashboard — KPIs, charts, system health

const navWithActive = adminDashboardNav.map((n) =>
  n.path === '/admin/analytics' ? { ...n, active: true } : n
);

const SECTIONS = ['Overview', 'Users', 'Admissions', 'AI Services', 'System Health'];

const STATUS_VARIANT = { Online: 'green', Degraded: 'yellow', Offline: 'coral' };

function MiniSparkBar({ value, max, color = 'var(--color-lime)' }) {
  return (
    <div className={styles.sparkBar}>
      <div className={styles.sparkFill} style={{ width: `${(value / max) * 100}%`, background: color }} />
    </div>
  );
}

function KpiTile({ label, value, delta, trend }) {
  const trendColor = trend === 'up' ? 'var(--color-lime-dark)' : trend === 'down' ? 'var(--color-coral)' : 'var(--color-text-muted)';
  return (
    <div className={styles.kpiTile}>
      <span className={styles.kpiLabel}>{label}</span>
      <span className={styles.kpiValue}>{value}</span>
      {delta && <span className={styles.kpiDelta} style={{ color: trendColor }}>{delta}</span>}
    </div>
  );
}

function exportCSV(kpis, period) {
  const rows = Object.entries(kpis).map(([key, kpi]) =>
    `"${key}","${kpi.value}","${kpi.delta || ''}","${kpi.trend || ''}"`
  );
  const csv = ['"Metric","Value","Change","Trend"', ...rows].join('\n');
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `analytics-${period}-${new Date().toISOString().split('T')[0]}.csv`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export default function AnalyticsPage() {
  const [section, setSection] = useState('Overview');
  const [period, setPeriod] = useState('30d');

  const kpis = mockAnalyticsByPeriod[period];

  return (
    <AppShell
      navItems={navWithActive}
      logoVariant="icon-text"
      sidebarLabel="ADMIN PANEL"
      topBar={<TopBar searchPlaceholder="Search analytics..." notificationCount={openTicketCount} />}
    >
      <div className={styles.breadcrumb}>INSIGHTS / ANALYTICS</div>

      <PageHeader
        title="Analytics & Monitoring"
        subtitle="Platform-wide metrics — users, admissions, AI services, and system health."
        actions={
          <div className={styles.headerRight}>
            <div className={styles.periodToggle}>
              {['24h', '7d', '30d', '90d'].map((p) => (
                <button
                  key={p}
                  className={`${styles.periodBtn} ${period === p ? styles.periodActive : ''}`}
                  onClick={() => setPeriod(p)}
                >{p}</button>
              ))}
            </div>
            <button className={styles.exportBtn} onClick={() => exportCSV(kpis, period)}>Export CSV</button>
          </div>
        }
      />

      {/* Section Tabs */}
      <div className={styles.tabs}>
        {SECTIONS.map((s) => (
          <button
            key={s}
            className={`${styles.tab} ${section === s ? styles.tabActive : ''}`}
            onClick={() => setSection(s)}
          >{s}</button>
        ))}
      </div>

      {/* ── OVERVIEW ─────────────────────────────────────── */}
      {section === 'Overview' && (
        <>
          <div className={styles.kpiGrid}>
            <KpiTile label="Total Users" {...kpis.totalUsers} />
            <KpiTile label="Active Users" {...kpis.activeUsers} />
            <KpiTile label="New Registrations" {...kpis.newRegistrations} />
            <KpiTile label="Applications" {...kpis.applicationsSubmitted} />
            <KpiTile label="API Requests" {...kpis.apiRequests} />
            <KpiTile label="System Uptime" {...kpis.systemUptime} />
            <KpiTile label="Error Rate" {...kpis.errorRate} />
            <KpiTile label="Avg Response" {...kpis.avgResponseTime} />
          </div>

          {/* Charts Row */}
          <div className={styles.chartsRow}>
            {/* User Growth */}
            <div className={styles.chartCard}>
              <div className={styles.chartHeader}>
                <span className={styles.chartTitle}>User Growth</span>
                <span className={styles.chartSubtitle}>{period}</span>
              </div>
              <div className={styles.fakeLineChart}>
                <svg viewBox="0 0 300 80" preserveAspectRatio="none" className={styles.chartSvg}>
                  <defs>
                    <linearGradient id="lineGrad" x1="0" x2="0" y1="0" y2="1">
                      <stop offset="0%" stopColor="#4caf27" stopOpacity="0.3"/>
                      <stop offset="100%" stopColor="#4caf27" stopOpacity="0"/>
                    </linearGradient>
                  </defs>
                  <path d="M0,70 C30,65 60,55 90,45 C120,35 150,30 180,25 C210,20 240,15 300,5" stroke="#4caf27" strokeWidth="2.5" fill="none"/>
                  <path d="M0,70 C30,65 60,55 90,45 C120,35 150,30 180,25 C210,20 240,15 300,5 L300,80 L0,80Z" fill="url(#lineGrad)"/>
                </svg>
                <div className={styles.chartLabels}>
                  {['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'].map((m) => (
                    <span key={m} className={styles.chartLabel}>{m}</span>
                  ))}
                </div>
              </div>
            </div>

            {/* AI Requests */}
            <div className={styles.chartCard}>
              <div className={styles.chartHeader}>
                <span className={styles.chartTitle}>AI Requests by Service</span>
              </div>
              {[
                { name: 'RAG Chatbot', value: 2100, max: 3000, color: 'var(--color-lime)' },
                { name: 'OCR Engine', value: 847, max: 3000, color: 'var(--color-coral)' },
                { name: 'Embedding', value: 541, max: 3000, color: 'var(--color-yellow)' },
                { name: 'Grade Pred.', value: 312, max: 3000, color: '#60a5fa' },
              ].map((item) => (
                <div key={item.name} className={styles.barItem}>
                  <span className={styles.barItemName}>{item.name}</span>
                  <MiniSparkBar value={item.value} max={item.max} color={item.color} />
                  <span className={styles.barItemValue}>{item.value.toLocaleString()}</span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {/* ── USERS ────────────────────────────────────────── */}
      {section === 'Users' && (
        <div className={styles.sectionContent}>
          <div className={styles.kpiGrid}>
            <KpiTile label="Total Users" {...kpis.totalUsers} />
            <KpiTile label="Active Users" {...kpis.activeUsers} />
            <KpiTile label="New Registrations" {...kpis.newRegistrations} />
          </div>
          <div className={styles.chartsRow}>
            <div className={styles.chartCard}>
              <div className={styles.chartHeader}><span className={styles.chartTitle}>Users by Role</span></div>
              {[
                { role: 'Students', count: 11890, pct: 95 },
                { role: 'Instructors', count: 312, pct: 2.5 },
                { role: 'Admission Officers', count: 18, pct: 0.14 },
                { role: 'Registrars', count: 14, pct: 0.11 },
                { role: 'Admins', count: 8, pct: 0.06 },
              ].map((r) => (
                <div key={r.role} className={styles.barItem}>
                  <span className={styles.barItemName}>{r.role}</span>
                  <MiniSparkBar value={r.pct} max={100} />
                  <span className={styles.barItemValue}>{r.count.toLocaleString()}</span>
                </div>
              ))}
            </div>
            <div className={styles.chartCard}>
              <div className={styles.chartHeader}><span className={styles.chartTitle}>Account Status Breakdown</span></div>
              {[
                { status: 'Active', count: 10842, color: 'var(--color-lime)' },
                { status: 'Inactive', count: 1284, color: 'var(--color-yellow)' },
                { status: 'Suspended', count: 312, color: 'var(--color-coral)' },
                { status: 'Pending', count: 44, color: '#94a3b8' },
              ].map((s) => (
                <div key={s.status} className={styles.barItem}>
                  <span className={styles.barItemName}>{s.status}</span>
                  <MiniSparkBar value={s.count} max={12000} color={s.color} />
                  <span className={styles.barItemValue}>{s.count.toLocaleString()}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ── ADMISSIONS ───────────────────────────────────── */}
      {section === 'Admissions' && (
        <div className={styles.sectionContent}>
          <div className={styles.kpiGrid}>
            <KpiTile label="Applications" {...kpis.applicationsSubmitted} />
            <KpiTile label="Approved" {...kpis.applicationsApproved} />
            <KpiTile label="Avg Processing Time" {...kpis.avgProcessingTime} />
          </div>
          <div className={styles.chartCard} style={{ maxWidth: 600 }}>
            <div className={styles.chartHeader}><span className={styles.chartTitle}>Admission Funnel</span></div>
            {mockAdmissionFunnel.map((stage) => (
              <div key={stage.stage} className={styles.funnelRow}>
                <span className={styles.funnelStage}>{stage.stage}</span>
                <div className={styles.funnelBar}>
                  <div className={styles.funnelFill} style={{ width: `${stage.pct}%` }} />
                </div>
                <span className={styles.funnelCount}>{stage.count.toLocaleString()}</span>
                <span className={styles.funnelPct}>{stage.pct}%</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── AI SERVICES ──────────────────────────────────── */}
      {section === 'AI Services' && (
        <div className={styles.sectionContent}>
          <div className={styles.kpiGrid}>
            <KpiTile label="OCR Requests" {...kpis.ocrRequests} />
            <KpiTile label="OCR Success Rate" {...kpis.ocrSuccessRate} />
            <KpiTile label="Chatbot Sessions" {...kpis.chatbotSessions} />
          </div>
          <div className={styles.chartCard}>
            <div className={styles.chartHeader}><span className={styles.chartTitle}>Service Performance</span></div>
            {[
              { name: 'OCR Accuracy', value: 94.2, unit: '%', good: true },
              { name: 'Chatbot Satisfaction', value: 87.4, unit: '%', good: true },
              { name: 'Grade Pred. RMSE', value: 0.42, unit: '', good: true },
              { name: 'Avg RAG Latency', value: 3.8, unit: 's', good: false },
            ].map((m) => (
              <div key={m.name} className={styles.barItem}>
                <span className={styles.barItemName}>{m.name}</span>
                <MiniSparkBar value={Math.min(m.value, 100)} max={100} color={m.good ? 'var(--color-lime)' : 'var(--color-coral)'} />
                <span className={styles.barItemValue} style={{ color: m.good ? 'var(--color-lime-dark)' : 'var(--color-coral)' }}>
                  {m.value}{m.unit}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── SYSTEM HEALTH ────────────────────────────────── */}
      {section === 'System Health' && (
        <div className={styles.sectionContent}>
          <div className={styles.kpiGrid}>
            <KpiTile label="API Requests" {...kpis.apiRequests} />
            <KpiTile label="System Uptime" {...kpis.systemUptime} />
            <KpiTile label="Error Rate" {...kpis.errorRate} />
            <KpiTile label="Avg Response" {...kpis.avgResponseTime} />
          </div>

          {/* Infrastructure gauges */}
          <div className={styles.infraRow}>
            {[
              { label: 'CPU Usage', value: 68, warn: false },
              { label: 'Memory', value: 74, warn: false },
              { label: 'DB Connections', value: 82, warn: true },
              { label: 'Storage', value: 61, warn: false },
            ].map((g) => (
              <div key={g.label} className={styles.gaugeCard}>
                <span className={styles.gaugeLabel}>{g.label}</span>
                <div className={styles.gaugeTrack}>
                  <div
                    className={styles.gaugeFill}
                    style={{
                      width: `${g.value}%`,
                      background: g.warn ? 'var(--color-yellow)' : g.value > 85 ? 'var(--color-coral)' : 'var(--color-lime)',
                    }}
                  />
                </div>
                <span className={styles.gaugeValue} style={{ color: g.warn ? 'var(--color-yellow)' : 'inherit' }}>
                  {g.value}%{g.warn && ' !'}
                </span>
              </div>
            ))}
          </div>

          {/* Service table */}
          <div className={styles.tableCard}>
            <table className={styles.serviceTable}>
              <thead>
                <tr>
                  {['Service', 'Uptime', 'P50', 'P99', 'Error Rate', 'Status'].map((h) => (
                    <th key={h} className={styles.th}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {mockServiceHealthTable.map((row) => (
                  <tr key={row.service} className={styles.tr}>
                    <td className={styles.td}><strong>{row.service}</strong></td>
                    <td className={styles.td}>{row.uptime}</td>
                    <td className={styles.td}>{row.p50}</td>
                    <td className={styles.td}>{row.p99}</td>
                    <td className={styles.td} style={{ color: parseFloat(row.errors) > 2 ? 'var(--color-coral)' : 'inherit' }}>
                      {row.errors}
                    </td>
                    <td className={styles.td}>
                      <StatusPill status={row.status} variant={STATUS_VARIANT[row.status] || 'black'} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </AppShell>
  );
}
