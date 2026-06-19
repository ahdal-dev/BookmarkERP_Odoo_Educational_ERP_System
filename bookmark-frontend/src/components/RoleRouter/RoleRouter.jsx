import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { landingFor } from '../../config/roles';

/* ============================================================
   ROLE ROUTER — Sends an authenticated user to their landing
   view based on the role claim in the JWT (via AuthContext).
   Mounted at "/" so every fresh login resolves here first.
   ============================================================ */

export default function RoleRouter() {
  const { isAuthenticated, isLoading, user } = useAuth();

  if (isLoading) return null; // ProtectedRoute / guards render the spinner

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <Navigate to={landingFor(user?.role)} replace />;
}
