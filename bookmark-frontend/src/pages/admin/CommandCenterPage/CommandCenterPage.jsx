import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AppShell from '../../../components/AppShell/AppShell';
import TopBar from '../../../components/TopBar/TopBar';
import StatCard from '../../../components/StatCard/StatCard';
import CircularGauge from '../../../components/CircularGauge/CircularGauge';
import StatusPill from '../../../components/StatusPill/StatusPill';
import useAsync from '../../../hooks/useAsync';
import { adminAPI, auditAPI } from '../../../api/apiGateway';
import { adminDashboardNav } from '../../../config/navConfigs';
import {
  mockRecentSecurityEvents,
  openTicketCount,
  mockAdmissionSummary,
  mockUserGrowth,
  mockUserGrowth90d,
} from '../../../mocks/adminMocks';
import styles from './CommandCenterPage.module.css';

const SERVICE_STATUS_COLOR = { Online: 'green', Degraded: 'yellow', Offline: 'coral' };
const SEVERITY_COLOR = { high: '#e8613a', medium: '#f5c842', low: 'rgba(255,255,255,0.3)' };

const navWithActive = adminDashboardNav.map((n) =>
  n.path === '/admin' ? { ...n, active: true } : n
);

function exportSummaryReport(kpis, growth) {
  const lines = [
    'Bookmark Academic ERP — Command Center Summary Report',
    `Generated: ${new Date().toLocaleString()}`,
    '======================================================',
    '',
    'KPI SUMMARY',
    `Total Users: ${kpis.totalUsers}`,
    `Active Today: ${kpis.activeToday} (${kpis.activeTodayPct})`,
    `AI Requests / Day: ${kpis.aiRequests} (${kpis.aiRequestsDelta})`,
    `Open Tickets: ${kpis.openTickets} (${kpis.criticalTickets} critical)`,
    `System Uptime: ${kpis.systemUptime}`,
    '',
    'USER GROWTH (30d)',
    ...growth.map((p) => `  ${p.label}: ${p.value.toLocaleString()}`),
  ].join('\n');
  const blob = new Blob([lines], { type: 'text/plain;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `command-center-report-${new Date().toISOString().split('T')[0]}.txt`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

const MONTH_ABBR = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

function parseGrowthData(analyticsData) {
  if (!analyticsData?.data?.length) return null;
  return analyticsData.data.map((d) => {
    const [, month] = (d.month || '').split('-');
    const label = month ? (MONTH_ABBR[parseInt(month, 10) - 1] || d.month) : d.month;
    return { label, value: d.users };
  });
}

const SEVERITY_MAP = { high: 'high', warning: 'medium', info: 'low', error: 'high' };

function parseAuditEvents(auditData) {
  if (!auditData?.events?.length) return null;
  return auditData.events.slice(0, 5).map((e, i) => ({
    id: i + 1,
    severity: SEVERITY_MAP[e.severity] || 'low',
    message: e.detail || `${e.event_type} — ${e.actor}`,
    time: e.date ? new Date(e.date).toLocaleString() : '',
  }));
}

export default function CommandCenterPage() {
  const navigate = useNavigate();
  const [alertDismissed, setAlertDismissed] = useState(false);
  const [chartPeriod, setChartPeriod] = useState('30d');

  const { data: statsData } = useAsync(adminAPI.getStats);
  const { data: healthData } = useAsync(adminAPI.getHealth);
  const { data: analyticsData } = useAsync(adminAPI.getAnalytics);
  const { data: auditData } = useAsync(() => auditAPI.getLog({ limit: 5 }));

  const kpis = {
    totalUsers: statsData?.totalUsers || 0,
    totalUsersDelta: statsData?.totalUsersDelta || '+0%',
    activeToday: statsData?.activeUsers || 0,
    activeTodayPct: statsData?.activeTodayPct || '0%',
    aiRequests: statsData?.aiRequests || 0,
    aiRequestsDelta: statsData?.aiRequestsDelta || '+0%',
    openTickets: statsData?.openTickets ?? statsData?.pendingPetitions ?? 0,
    criticalTickets: statsData?.criticalTickets || 0,
    systemUptime: statsData?.systemUptime || 0,
  };

  const aiSummary = healthData?.services?.map((s) => ({
    slug: s.name.toLowerCase().replace(/\s+/g, '-'),
    name: s.name,
    status: s.status === 'Healthy' ? 'Online' : s.status,
    requests: s.latency || 0,
  })) || [];
  const degraded = aiSummary.filter((s) => s.status === 'Degraded' || s.status === 'Offline');

  const liveAdmission = {
    newApplications: statsData?.totalApplications || 0,
    inReview: statsData?.inReviewApplications || 0,
    missingDocs: statsData?.missingDocs || 0,
    approvedToday: statsData?.admittedApplications || 0,
  };

  const liveGrowth = parseGrowthData(analyticsData);
  const chartData = liveGrowth ?? (chartPeriod === '30d' ? mockUserGrowth : mockUserGrowth90d);

  const liveSecurityEvents = parseAuditEvents(auditData);
  const securityEvents = liveSecurityEvents ?? mockRecentSecurityEvents;

  return (
    <AppShell
      navItems={navWithActive}
      logoVariant="icon-text"
      sidebarLabel="ADMIN PANEL"
      topBar={<TopBar searchPlaceholder="Search users, pages, settings..." notificationCount={kpis.openTickets} />}
    >
      {!alertDismissed && degraded.length > 0 && (
        <div className={styles.alertBanner}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><path d="M12 9v4m0 4h.01"/></svg>
          <span>
            {degraded.length} AI {degraded.length === 1 ? 'service' : 'services'} degraded
            &nbsp;·&nbsp;
            {degraded.map((s) => s.name).join(', ')}
          </span>
          <button className={styles.alertView} onClick={() => navigate('/admin/ai')}>View Services →</button>
          <button className={styles.alertClose} onClick={() => setAlertDismissed(true)} aria-label="Dismiss">✕</button>
        </div>
      )}

      <div className={styles.breadcrumb}>ADMIN CONTROL / COMMAND CENTER</div>

      <div className={styles.pageHeader}>
        <div>
          <h1 className={styles.title}>Command Center</h1>
          <p className={styles.subtitle}>Platform overview — users, AI services, and system health at a glance.</p>
        </div>
        <div className={styles.headerActions}>
          <button className={styles.secondaryBtn} onClick={() => navigate('/admin/analytics')}>View Analytics</button>
          <button className={styles.primaryBtn} onClick={() => navigate('/admin/users')}>+ Create User</button>
        </div>
      </div>

      <div className={styles.kpiStrip}>
        <StatCard label="TOTAL USERS" value={kpis.totalUsers} delta={kpis.totalUsersDelta} />
        <StatCard label="ACTIVE TODAY" value={kpis.activeToday} delta={kpis.activeTodayPct} />
        <StatCard label="AI REQUESTS / DAY" value={kpis.aiRequests} delta={kpis.aiRequestsDelta} />
        <div className={styles.ticketKpiCard}>
          <div className={styles.ticketTop}>
            <span className={styles.ticketLabel}>OPEN TICKETS</span>
            <span className={styles.ticketValue}>{kpis.openTickets}</span>
          </div>
          <span className={styles.ticketSub}>{kpis.criticalTickets} critical</span>
        </div>
      </div>

      <div className={styles.row2}>
        <div className={styles.card}>
          <div className={styles.cardHeader}>
            <span className={styles.cardTitle}>User Growth</span>
            <div className={styles.periodToggle}>
              {['30d', '90d'].map((p) => (
                <button
                  key={p}
                  className={`${styles.periodBtn} ${chartPeriod === p ? styles.periodActive : ''}`}
                  onClick={() => setChartPeriod(p)}
                >{p}</button>
              ))}
            </div>
          </div>
          <div className={styles.barChart}>
            {chartData.map((point) => {
              const max = Math.max(...chartData.map((p) => p.value));
              const pct = (point.value / max) * 100;
              return (
                <div key={point.label} className={styles.barGroup}>
                  <div className={styles.barWrap}>
                    <div className={styles.bar} style={{ height: `${pct}%` }} />
                  </div>
                  <span className={styles.barLabel}>{point.label}</span>
                  <span className={styles.barValue}>{(point.value / 1000).toFixed(1)}k</span>
                </div>
              );
            })}
          </div>
        </div>

        <div className={styles.card}>
          <div className={styles.cardHeader}>
            <span className={styles.cardTitle}>AI Service Status</span>
            <button className={styles.viewAllBtn} onClick={() => navigate('/admin/ai')}>View All →</button>
          </div>
          <div className={styles.serviceList}>
            {aiSummary.map((svc) => (
              <div key={svc.slug} className={styles.serviceRow}>
                <span
                  className={styles.statusDot}
                  style={{ background: svc.status === 'Online' ? 'var(--color-lime)' : 'var(--color-coral)' }}
                />
                <span className={styles.serviceName}>{svc.name}</span>
                <span className={styles.serviceReqs}>{(svc.requests || 0).toLocaleString()} req</span>
                <StatusPill status={svc.status} variant={SERVICE_STATUS_COLOR[svc.status] || 'black'} />
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className={styles.row3}>
        <div className={styles.card}>
          <div className={styles.cardHeader}>
            <span className={styles.cardTitle}>Admission Pipeline</span>
            <button className={styles.viewAllBtn} onClick={() => navigate('/admin/admissions')}>View →</button>
          </div>
          <div className={styles.admissionGrid}>
            {[
              { label: 'New Applications', value: liveAdmission.newApplications, color: 'var(--color-lime)' },
              { label: 'In Review', value: liveAdmission.inReview, color: 'var(--color-yellow)' },
              { label: 'Missing Docs', value: liveAdmission.missingDocs, color: 'var(--color-coral)' },
              { label: 'Approved Today', value: liveAdmission.approvedToday, color: 'var(--color-lime)' },
            ].map((item) => (
              <div key={item.label} className={styles.admissionItem} style={{ '--accent-color': item.color }}>
                <span className={styles.admissionValue}>{item.value}</span>
                <span className={styles.admissionLabel}>{item.label}</span>
              </div>
            ))}
          </div>
        </div>

        <div className={styles.card}>
          <div className={styles.cardHeader}>
            <span className={styles.cardTitle}>Recent Security Events</span>
            <button className={styles.viewAllBtn} onClick={() => navigate('/admin/security')}>View All →</button>
          </div>
          <div className={styles.securityList}>
            {securityEvents.map((ev) => (
              <div key={ev.id} className={styles.securityRow}>
                <span
                  className={styles.severityDot}
                  style={{ background: SEVERITY_COLOR[ev.severity] }}
                />
                <div className={styles.securityText}>
                  <span className={styles.securityMsg}>{ev.message}</span>
                  <span className={styles.securityTime}>{ev.time}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <CircularGauge
          value={typeof kpis.systemUptime === 'number' ? kpis.systemUptime : parseFloat(kpis.systemUptime)}
          caption="ACTIVE CYCLE INSIGHT"
          label="System Uptime"
        />
      </div>

      <div className={styles.card}>
        <span className={styles.cardTitle}>Quick Actions</span>
        <div className={styles.quickActions}>
          {[
            { label: '+ Create User', path: '/admin/users' },
            { label: 'Upload KB Doc', path: '/admin/knowledge-base' },
            { label: 'Run Audit', path: '/admin/security' },
            { label: 'View Analytics', path: '/admin/analytics' },
            { label: 'Feature Flags', path: '/admin/system' },
            { label: 'Export Report', path: null },
          ].map((action) => (
            <button
              key={action.label}
              className={styles.quickBtn}
              onClick={() =>
                action.path
                  ? navigate(action.path)
                  : exportSummaryReport(kpis, chartData)
              }
            >
              {action.label}
            </button>
          ))}
        </div>
      </div>
    </AppShell>
  );
}
