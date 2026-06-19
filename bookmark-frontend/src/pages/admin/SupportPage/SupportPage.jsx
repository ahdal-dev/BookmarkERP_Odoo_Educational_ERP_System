import { useState } from 'react';
import AppShell from '../../../components/AppShell/AppShell';
import TopBar from '../../../components/TopBar/TopBar';
import StatusPill from '../../../components/StatusPill/StatusPill';
import { adminDashboardNav } from '../../../config/navConfigs';
import {
  mockTickets,
  mockFeedback,
  mockServiceStatus,
  openTicketCount,
} from '../../../mocks/adminMocks';
import styles from './SupportPage.module.css';

const TABS = ['Tickets', 'User Feedback', 'Service Status'];

const navWithActive = adminDashboardNav.map((n) =>
  n.path === '/admin/support' ? { ...n, active: true } : n
);

const TICKET_STATUS_VARIANT = {
  Open: 'coral',
  'In Progress': 'yellow',
  Resolved: 'green',
};

const SERVICE_VARIANT = {
  Operational: 'green',
  Degraded: 'yellow',
  Outage: 'coral',
};

const PRIORITY_COLOR = { High: '#e8613a', Medium: '#f5c842', Low: '#b5b3ab' };

const STAR_COUNT = 5;

function StarRating({ rating }) {
  return (
    <span className={styles.stars}>
      {Array.from({ length: STAR_COUNT }, (_, i) => (
        <span key={i} style={{ color: i < rating ? '#f5c842' : '#e5e3db' }}>★</span>
      ))}
    </span>
  );
}

export default function SupportPage() {
  const [activeTab, setActiveTab] = useState('Tickets');
  const [tickets, setTickets] = useState(mockTickets);
  const [priorityFilter, setPriorityFilter] = useState('All');
  const [statusFilter, setStatusFilter] = useState('All');
  const [viewingTicket, setViewingTicket] = useState(null);

  const filteredTickets = tickets.filter((t) => {
    const matchPriority = priorityFilter === 'All' || t.priority === priorityFilter;
    const matchStatus = statusFilter === 'All' || t.status === statusFilter;
    return matchPriority && matchStatus;
  });

  const resolveTicket = (id) =>
    setTickets((prev) =>
      prev.map((t) => (t.id === id ? { ...t, status: 'Resolved' } : t))
    );

  const openCount = tickets.filter((t) => t.status === 'Open').length;
  const inProgressCount = tickets.filter((t) => t.status === 'In Progress').length;
  const resolvedCount = tickets.filter((t) => t.status === 'Resolved').length;
  const highCount = tickets.filter((t) => t.priority === 'High').length;

  return (
    <AppShell
      navItems={navWithActive}
      logoVariant="icon-text"
      sidebarLabel="ADMIN PANEL"
      topBar={<TopBar searchPlaceholder="Search tickets, users..." notificationCount={openTicketCount} />}
    >
      <div className={styles.breadcrumb}>ADMIN CONTROL / SUPPORT & OPERATIONS</div>

      <div className={styles.pageHeader}>
        <div>
          <h1 className={styles.title}>Support & Operations</h1>
          <p className={styles.subtitle}>Manage support tickets, user feedback, and monitor platform service health.</p>
        </div>
      </div>

      {/* Summary Strip */}
      <div className={styles.summaryStrip}>
        <div className={styles.summaryCard} style={{ '--accent': '#e8613a' }}>
          <span className={styles.summaryValue}>{openCount}</span>
          <span className={styles.summaryLabel}>Open Tickets</span>
        </div>
        <div className={styles.summaryCard} style={{ '--accent': '#f5c842' }}>
          <span className={styles.summaryValue}>{inProgressCount}</span>
          <span className={styles.summaryLabel}>In Progress</span>
        </div>
        <div className={styles.summaryCard} style={{ '--accent': '#4caf27' }}>
          <span className={styles.summaryValue}>{resolvedCount}</span>
          <span className={styles.summaryLabel}>Resolved</span>
        </div>
        <div className={styles.summaryCard} style={{ '--accent': '#e8613a' }}>
          <span className={styles.summaryValue}>{highCount}</span>
          <span className={styles.summaryLabel}>High Priority</span>
        </div>
      </div>

      {/* Tabs */}
      <div className={styles.tabs}>
        {TABS.map((t) => (
          <button
            key={t}
            className={`${styles.tab} ${activeTab === t ? styles.tabActive : ''}`}
            onClick={() => setActiveTab(t)}
          >
            {t}
          </button>
        ))}
      </div>

      {/* ── Tickets Tab ── */}
      {activeTab === 'Tickets' && (
        <div className={styles.card}>
          <div className={styles.toolbar}>
            <select
              className={styles.filterSelect}
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
            >
              <option value="All">All Priorities</option>
              <option>High</option>
              <option>Medium</option>
              <option>Low</option>
            </select>
            <select
              className={styles.filterSelect}
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="All">All Statuses</option>
              <option>Open</option>
              <option>In Progress</option>
              <option>Resolved</option>
            </select>
            <span className={styles.countLabel}>{filteredTickets.length} tickets</span>
          </div>

          <table className={styles.table}>
            <thead>
              <tr>
                <th>ID</th>
                <th>Subject</th>
                <th>User</th>
                <th>Role</th>
                <th>Priority</th>
                <th>Status</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredTickets.map((tkt) => (
                <tr key={tkt.id}>
                  <td className={styles.ticketId}>{tkt.id}</td>
                  <td className={styles.titleCell}>{tkt.subject}</td>
                  <td className={styles.muted}>{tkt.user}</td>
                  <td className={styles.muted}>{tkt.role}</td>
                  <td>
                    <span
                      className={styles.priorityPill}
                      style={{ background: PRIORITY_COLOR[tkt.priority] + '22', color: PRIORITY_COLOR[tkt.priority] }}
                    >
                      {tkt.priority}
                    </span>
                  </td>
                  <td>
                    <StatusPill status={tkt.status} variant={TICKET_STATUS_VARIANT[tkt.status] || 'black'} />
                  </td>
                  <td className={styles.muted}>{tkt.created}</td>
                  <td>
                    <div className={styles.rowActions}>
                      <button className={styles.viewBtn} onClick={() => setViewingTicket(tkt)}>View</button>
                      {tkt.status !== 'Resolved' && (
                        <button className={styles.resolveBtn} onClick={() => resolveTicket(tkt.id)}>Resolve</button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* ── Feedback Tab ── */}
      {activeTab === 'User Feedback' && (
        <div className={styles.feedbackGrid}>
          {mockFeedback.map((fb) => (
            <div key={fb.id} className={styles.feedbackCard}>
              <div className={styles.feedbackTop}>
                <div>
                  <div className={styles.feedbackUser}>{fb.from}</div>
                  <div className={styles.feedbackRole}>{fb.role} · {fb.date}</div>
                </div>
                <span className={styles.featureTag}>{fb.feature}</span>
              </div>
              <StarRating rating={fb.rating} />
              <p className={styles.feedbackComment}>"{fb.comment}"</p>
            </div>
          ))}
        </div>
      )}

      {/* ── Service Status Tab ── */}
      {activeTab === 'Service Status' && (
        <div className={styles.card}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Service</th>
                <th>Uptime (30d)</th>
                <th>Last Incident</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {mockServiceStatus.map((svc) => (
                <tr key={svc.name}>
                  <td className={styles.titleCell}>{svc.name}</td>
                  <td className={styles.uptimeCell}>{svc.uptime}</td>
                  <td className={styles.muted}>{svc.lastIncident}</td>
                  <td>
                    <StatusPill status={svc.status} variant={SERVICE_VARIANT[svc.status] || 'black'} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* ── View Ticket Modal ── */}
      {viewingTicket && (
        <div className={styles.modalOverlay} onClick={() => setViewingTicket(null)}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <span className={styles.modalTitle}>{viewingTicket.id}</span>
              <button className={styles.modalClose} onClick={() => setViewingTicket(null)}>✕</button>
            </div>
            <div className={styles.modalBody}>
              <div className={styles.ticketDetailRow}>
                <span className={styles.detailLabel}>Subject</span>
                <span className={styles.detailValue}>{viewingTicket.subject}</span>
              </div>
              <div className={styles.ticketDetailRow}>
                <span className={styles.detailLabel}>Submitted By</span>
                <span className={styles.detailValue}>{viewingTicket.user} ({viewingTicket.role})</span>
              </div>
              <div className={styles.ticketDetailRow}>
                <span className={styles.detailLabel}>Priority</span>
                <span
                  className={styles.priorityPill}
                  style={{ background: PRIORITY_COLOR[viewingTicket.priority] + '22', color: PRIORITY_COLOR[viewingTicket.priority] }}
                >
                  {viewingTicket.priority}
                </span>
              </div>
              <div className={styles.ticketDetailRow}>
                <span className={styles.detailLabel}>Status</span>
                <StatusPill status={viewingTicket.status} variant={TICKET_STATUS_VARIANT[viewingTicket.status] || 'black'} />
              </div>
              <div className={styles.ticketDetailRow}>
                <span className={styles.detailLabel}>Created</span>
                <span className={styles.detailValue}>{viewingTicket.created}</span>
              </div>
              <div className={styles.replyBox}>
                <label className={styles.fieldLabel}>Reply / Internal Note</label>
                <textarea className={styles.fieldTextarea} rows={3} placeholder="Add a reply or internal note..." />
              </div>
            </div>
            <div className={styles.modalFooter}>
              <button className={styles.cancelBtn} onClick={() => setViewingTicket(null)}>Close</button>
              {viewingTicket.status !== 'Resolved' && (
                <button
                  className={styles.saveBtn}
                  onClick={() => { resolveTicket(viewingTicket.id); setViewingTicket(null); }}
                >
                  Resolve Ticket
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </AppShell>
  );
}
