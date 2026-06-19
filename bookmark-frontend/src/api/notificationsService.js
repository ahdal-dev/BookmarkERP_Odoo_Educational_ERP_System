import api from './apiGateway';

/* ============================================================
   NOTIFICATIONS SERVICE — Adapter layer for the centralized
   notifications hub. Backed by the edu.notification Odoo model
   via the FastAPI gateway.

   Gateway routes:
     GET   /api/v1/notifications            -> Notification[]
     PATCH /api/v1/notifications/:id/read   -> { ok: true }
     POST  /api/v1/notifications/read-all   -> { ok: true }

   Notification shape (already mapped by the gateway):
     { id, category, title, message, timestamp(ISO), read(bool), link? }
   ============================================================ */

export const NOTIFICATION_CATEGORIES = {
  petition: { key: 'petition', label: 'Petitions', accent: 'var(--color-coral)' },
  registration: { key: 'registration', label: 'Registration', accent: 'var(--color-lime)' },
  system: { key: 'system', label: 'System Updates', accent: 'var(--color-yellow)' },
  other: { key: 'other', label: 'Other', accent: 'var(--color-text-muted)' },
};

export const CATEGORY_ORDER = ['petition', 'registration', 'system', 'other'];

/** Fetch the full notification feed for the current user. */
export async function fetchNotifications() {
  const { data } = await api.get('/api/v1/notifications');
  return Array.isArray(data) ? data : data?.notifications ?? [];
}

/** Mark a single notification as read. */
export async function markAsRead(id) {
  await api.patch(`/api/v1/notifications/${id}/read`);
}

/** Mark every notification as read. */
export async function markAllAsRead() {
  await api.post('/api/v1/notifications/read-all');
}

/** Group a flat feed into the fixed category buckets. */
export function groupByCategory(items) {
  const groups = Object.fromEntries(CATEGORY_ORDER.map((k) => [k, []]));
  items.forEach((n) => {
    const bucket = groups[n.category] ? n.category : 'other';
    groups[bucket].push(n);
  });
  return groups;
}
