import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute/ProtectedRoute';
import LoginPage from './pages/LoginPage/LoginPage';
import DashboardPage from './pages/DashboardPage/DashboardPage';
import RegistrationPage from './pages/RegistrationPage/RegistrationPage';
import InstitutionalRulesetPage from './pages/InstitutionalRulesetPage/InstitutionalRulesetPage';
import UserManagementPage from './pages/UserManagementPage/UserManagementPage';
import DocumentVerificationPage from './pages/DocumentVerificationPage/DocumentVerificationPage';
import AdmissionPipelinePage from './pages/AdmissionPipelinePage/AdmissionPipelinePage';
import PetitionFormPage from './pages/PetitionFormPage/PetitionFormPage';
import PetitionTrackingPage from './pages/PetitionTrackingPage/PetitionTrackingPage';

/* ============================================================
   APP — Root Router
   ============================================================ */

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<LoginPage />} />

          {/* Protected Routes — Student */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/registration"
            element={
              <ProtectedRoute>
                <RegistrationPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/petitions/new"
            element={
              <ProtectedRoute>
                <PetitionFormPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/apply/documents"
            element={
              <ProtectedRoute>
                <DocumentVerificationPage />
              </ProtectedRoute>
            }
          />

          {/* Protected Routes — Admin */}
          <Route
            path="/admin/settings/registration-rules"
            element={
              <ProtectedRoute roles={['admin']}>
                <InstitutionalRulesetPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/users"
            element={
              <ProtectedRoute roles={['admin']}>
                <UserManagementPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/admissions"
            element={
              <ProtectedRoute roles={['admin', 'officer']}>
                <AdmissionPipelinePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/petitions"
            element={
              <ProtectedRoute roles={['admin', 'officer']}>
                <PetitionTrackingPage />
              </ProtectedRoute>
            }
          />

          {/* Default redirect */}
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
