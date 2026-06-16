import { Link } from 'react-router-dom';

/* ============================================================
   UNAUTHORIZED PAGE — Shown when a user reaches a route
   outside their role scope.
   ============================================================ */

export default function UnauthorizedPage() {
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
      <div style={{ fontSize: 56, fontWeight: 800, color: '#e8613a' }}>403</div>
      <h1 style={{ margin: '8px 0 0', fontSize: 24, color: '#1a1a1a' }}>
        Access Restricted
      </h1>
      <p style={{ marginTop: 8, maxWidth: 440, color: '#6b6b6b', lineHeight: 1.5 }}>
        You don't have permission to view this page. If you believe this is an
        error, contact your system administrator.
      </p>
      <Link
        to="/"
        style={{
          marginTop: 24,
          padding: '10px 20px',
          borderRadius: 8,
          background: '#4caf27',
          color: '#fff',
          textDecoration: 'none',
          fontSize: 14,
        }}
      >
        Go to my dashboard
      </Link>
    </div>
  );
}
