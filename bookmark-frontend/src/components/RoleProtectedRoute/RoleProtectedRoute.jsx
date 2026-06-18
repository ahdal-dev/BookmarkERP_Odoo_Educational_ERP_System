import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { ROLES, landingFor } from '../../config/roles';

/* ============================================================
   ROLE PROTECTED ROUTE
   - Not authenticated            -> /login
   - Authenticated, wrong role    -> redirect to OWN landing view
                                     (avoids a dead /unauthorized loop
                                      while still blocking cross-role access)
   - Super Admin                  -> bypasses the role check (inspect any route)
   ============================================================ */

export default function RoleProtectedRoute({ allowedRoles = [], children }) {
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

  const role = user?.role;

  // Super Admin can inspect any route.
  if (role === ROLES.SUPER_ADMIN) return children;

  if (allowedRoles.length && !allowedRoles.includes(role)) {
    // Wrong scope: bounce to this user's own landing view.
    return <Navigate to={landingFor(role)} replace />;
  }

  return children;
}
