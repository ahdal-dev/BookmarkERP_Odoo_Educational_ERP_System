import { useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import StatusPill from '../../components/StatusPill/StatusPill';
import { navForRole } from '../../config/navConfigs';
import { useAuth } from '../../context/AuthContext';
import {
  fetchNotifications,
  markAsRead,
  markAllAsRead,
  groupByCategory,
  NOTIFICATION_CATEGORIES,
  CATEGORY_ORDER,
} from '../../api/notificationsService';
import w from '../_shared/workflow.module.css';

/* Centralized Notifications hub — categorizes alerts across the app
   (Petitions, Registration, System updates, Other). Cross-role. */

function relativeTime(iso) {
  const diff = Date.now() - new Date(iso).getTime();
  const min = Math.round(diff / 60000);
  if (min < 1) return 'just now';
  if (min < 60) return `${min}m ago`;
  const hr = Math.round(min / 60);
  if (hr < 24) return `${hr}h ago`;
  return `${Math.round(hr / 24)}d ago`;
}

export default function NotificationsPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const navItems = useMemo(() => navForRole(user?.role), [user?.role]);

  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all'); // 'all' | category key | 'unread'

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchNotifications();
      setItems(data);
    } catch {
      setError('Could not load notifications. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  // SSE: real-time notification push — reload feed whenever a new event arrives
  const sseRef = useRef(null);
  useEffect(() => {
    const token = localStorage.getItem('bookmark_token');
    if (!token) return;
    const es = new EventSource(`/api/v1/notifications/stream?token=${encodeURIComponent(token)}`);
    sseRef.current = es;
    es.addEventListener('notification', () => load());
    // EventSource reconnects automatically on error — no manual retry needed
    return () => { es.close(); sseRef.current = null; };
  }, []);

  const unreadCount = items.filter((n) => !n.read).length;
  const grouped = useMemo(() => groupByCategory(items), [items]);

  const visible = useMemo(() => {
    if (filter === 'all') return items;
    if (filter === 'unread') return items.filter((n) => !n.read);
    return grouped[filter] || [];
  }, [filter, items, grouped]);

  const handleOpen = async (n) => {
    if (!n.read) {
      await markAsRead(n.id);
      setItems((prev) => prev.map((x) => (x.id === n.id ? { ...x, read: true } : x)));
    }
    if (n.link) navigate(n.link);
  };

  const handleMarkAll = async () => {
    await markAllAsRead();
    setItems((prev) => prev.map((x) => ({ ...x, read: true })));
  };

  const filterTabs = [
    { key: 'all', label: 'All' },
    { key: 'unread', label: `Unread${unreadCount ? ` (${unreadCount})` : ''}` },
    ...CATEGORY_ORDER.map((k) => ({ key: k, label: NOTIFICATION_CATEGORIES[k].label })),
  ];

  return (
    <AppShell navItems={navItems} logoVariant="stacked" sidebarLabel="NOTIFICATIONS">
      <PageHeader
        title="Notifications"
        subtitle="All alerts across your portal, in one place"
        useBrandFont
        badge={unreadCount ? `${unreadCount} NEW` : undefined}
        badgeVariant="coral"
      />

      {/* Category summary */}
      <div className={`${w.statRow} ${w.cols4}`}>
        {CATEGORY_ORDER.map((k) => {
          const cat = NOTIFICATION_CATEGORIES[k];
          const count = grouped[k].length;
          const unread = grouped[k].filter((n) => !n.read).length;
          return (
            <button
              key={k}
              className={`${w.card}`}
              style={{ textAlign: 'left', cursor: 'pointer', border: 'none', borderTop: `5px solid ${cat.accent}`, fontFamily: 'inherit' }}
              onClick={() => setFilter(k)}
            >
              <div style={{ fontSize: '1.6rem', fontWeight: 800 }}>{count}</div>
              <div className={w.cardSub} style={{ marginBottom: 0 }}>{cat.label}</div>
              {unread > 0 && <div style={{ marginTop: 6 }}><StatusPill status={`${unread} unread`} variant="coral" /></div>}
            </button>
          );
        })}
      </div>

      {/* Toolbar */}
      <div className={w.toolbar}>
        <div className={w.filterTabs}>
          {filterTabs.map((t) => (
            <button
              key={t.key}
              className={`${w.filterTab} ${filter === t.key ? w.filterTabActive : ''}`}
              onClick={() => setFilter(t.key)}
            >
              {t.label}
            </button>
          ))}
        </div>
        <div style={{ marginLeft: 'auto', display: 'flex', gap: 8 }}>
          <button className={`${w.btn} ${w.btnOutline} ${w.btnSm}`} onClick={load}>Refresh</button>
          <button className={`${w.btn} ${w.btnPrimary} ${w.btnSm}`} onClick={handleMarkAll} disabled={!unreadCount}>
            Mark all read
          </button>
        </div>
      </div>

      {/* Feed */}
      <div className={w.card} style={{ padding: 0 }}>
        {loading ? (
          <div className={w.empty}>Loading notifications…</div>
        ) : error ? (
          <div className={w.empty}>
            <div className={w.emptyTitle}>{error}</div>
            <button className={`${w.btn} ${w.btnOutline} ${w.btnSm}`} onClick={load}>Retry</button>
          </div>
        ) : visible.length === 0 ? (
          <div className={w.empty}>
            <div className={w.emptyTitle}>You're all caught up</div>
            <p>No notifications in this category.</p>
          </div>
        ) : (
          visible.map((n, i) => {
            const cat = NOTIFICATION_CATEGORIES[n.category] || NOTIFICATION_CATEGORIES.other;
            return (
              <button
                key={n.id}
                onClick={() => handleOpen(n)}
                style={{
                  display: 'flex', gap: 14, alignItems: 'flex-start', width: '100%', textAlign: 'left',
                  padding: '16px 20px', border: 'none', cursor: 'pointer', fontFamily: 'inherit',
                  background: n.read ? 'transparent' : 'var(--color-bg-warm)',
                  borderTop: i === 0 ? 'none' : '1px solid var(--color-border-light)',
                }}
              >
                <span style={{ width: 10, height: 10, borderRadius: '50%', background: cat.accent, marginTop: 6, flexShrink: 0 }} />
                <span style={{ flex: 1 }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                    <strong style={{ fontSize: '0.92rem' }}>{n.title}</strong>
                    {!n.read && <StatusPill status="New" variant="coral" />}
                  </span>
                  <span style={{ display: 'block', fontSize: '0.85rem', color: 'var(--color-text-secondary)', marginTop: 2 }}>{n.message}</span>
                  <span style={{ display: 'block', fontSize: '0.72rem', color: 'var(--color-text-muted)', marginTop: 6 }}>
                    {cat.label} · {relativeTime(n.timestamp)}
                  </span>
                </span>
                {n.link && <span className={w.cardLink} style={{ flexShrink: 0 }}>Open →</span>}
              </button>
            );
          })
        )}
      </div>
    </AppShell>
  );
}
