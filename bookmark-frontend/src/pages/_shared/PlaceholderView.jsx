import { useAuth } from '../../context/AuthContext';

/* ============================================================
   PLACEHOLDER VIEW — Temporary scaffold for role landing pages.
   Replace each consumer with the real screen (see
   docs/User_stories/Missing_Views_ToDo.md).
   ============================================================ */

export default function PlaceholderView({ title, subtitle, accent = '#4caf27' }) {
  const { user, logout } = useAuth();

  return (
    <div style={{
      minHeight: '100vh',
      background: '#f9f8f3',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 24,
      textAlign: 'center',
    }}>
      <div style={{
        width: 56,
        height: 56,
        borderRadius: 14,
        background: accent,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: '#fff',
        fontSize: 28,
        fontWeight: 700,
        marginBottom: 20,
      }}>
        {title?.charAt(0) || 'B'}
      </div>

      <h1 style={{ margin: 0, fontSize: 26, color: '#1a1a1a' }}>{title}</h1>
      {subtitle && (
        <p style={{ marginTop: 8, maxWidth: 480, color: '#6b6b6b', lineHeight: 1.5 }}>
          {subtitle}
        </p>
      )}

      {user && (
        <p style={{ marginTop: 16, fontSize: 14, color: '#8a8a8a' }}>
          Signed in as <strong>{user.name || user.email}</strong>
          {user.role ? ` — role: ${user.role}` : ''}
        </p>
      )}

      <button
        onClick={logout}
        style={{
          marginTop: 24,
          padding: '10px 20px',
          border: '1px solid #e5e3db',
          borderRadius: 8,
          background: '#fff',
          color: '#1a1a1a',
          cursor: 'pointer',
          fontSize: 14,
        }}
      >
        Sign Out
      </button>
    </div>
  );
}
