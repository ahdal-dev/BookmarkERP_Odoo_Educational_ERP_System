import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

/* ============================================================
   PROTECTED ROUTE — Redirects unauthenticated users to /login
   Supports optional role-based access control.
   ============================================================ */

export default function ProtectedRoute({ children, roles }) {
  const { isAuthenticated, isLoading, user } = useAuth();

  if (isLoading) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        background: '#f9f8f3',
      }}>
        <div style={{
          width: 40,
          height: 40,
          border: '3px solid #e5e3db',
          borderTopColor: '#4caf27',
          borderRadius: '50%',
          animation: 'spin 0.8s linear infinite',
        }} />
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Role-based access: if roles prop is specified, check the user's role
  if (roles && roles.length > 0) {
    const userRole = user?.role?.toLowerCase();
    const hasAccess = roles.some((r) => r.toLowerCase() === userRole);
    if (!hasAccess) {
      // Redirect users without the required role to the dashboard
      return <Navigate to="/dashboard" replace />;
    }
  }

  return children;
}
