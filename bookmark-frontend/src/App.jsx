import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute/ProtectedRoute';
import RoleProtectedRoute from './components/RoleProtectedRoute/RoleProtectedRoute';
import RoleRouter from './components/RoleRouter/RoleRouter';
import { ROLES } from './config/roles';

import LoginPage from './pages/LoginPage/LoginPage';
import UnauthorizedPage from './pages/UnauthorizedPage/UnauthorizedPage';

// App Launcher (existing component, now mounted at /apps)
import DashboardPage from './pages/DashboardPage/DashboardPage';
import RegistrationPage from './pages/RegistrationPage/RegistrationPage';
import InstitutionalRulesetPage from './pages/InstitutionalRulesetPage/InstitutionalRulesetPage';
import UserManagementPage from './pages/UserManagementPage/UserManagementPage';
import DocumentVerificationPage from './pages/DocumentVerificationPage/DocumentVerificationPage';
import AdmissionPipelinePage from './pages/AdmissionPipelinePage/AdmissionPipelinePage';
import PetitionFormPage from './pages/PetitionFormPage/PetitionFormPage';
import PetitionTrackingPage from './pages/PetitionTrackingPage/PetitionTrackingPage';

// Role landing pages (scaffolded — see docs/User_stories/Missing_Views_ToDo.md)
import StudentDashboardPage from './pages/student/StudentDashboardPage';
import FacultyDashboardPage from './pages/faculty/FacultyDashboardPage';
import SupportChatQueuePage from './pages/support/SupportChatQueuePage';
import ApplicationStatusPage from './pages/admissions/ApplicationStatusPage';

/* ============================================================
   APP — Root Router (role-aware)
   "/" dispatches each authenticated user to their landing view
   via RoleRouter; RoleProtectedRoute guards every role space.
   ============================================================ */

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/unauthorized" element={<UnauthorizedPage />} />
          <Route path="/admissions/status" element={<ApplicationStatusPage />} />

          {/* Post-login dispatcher */}
          <Route path="/" element={<RoleRouter />} />

          {/* App Launcher — Super Admin / Registrar / Admission Officer */}
          <Route
            path="/apps"
            element={
              <RoleProtectedRoute
                allowedRoles={[ROLES.SUPER_ADMIN, ROLES.REGISTRAR, ROLES.ADMISSION_OFFICER]}
              >
                <DashboardPage />
              </RoleProtectedRoute>
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

          {/* Student space */}
          <Route
            path="/student/dashboard"
            element={
              <RoleProtectedRoute allowedRoles={[ROLES.STUDENT]}>
                <StudentDashboardPage />
              </RoleProtectedRoute>
            }
          />

          {/* Faculty space — Instructor / Advisor / Chair share the shell */}
          <Route
            path="/faculty/dashboard"
            element={
              <RoleProtectedRoute
                allowedRoles={[ROLES.INSTRUCTOR, ROLES.ACADEMIC_ADVISOR, ROLES.DEPARTMENT_CHAIR]}
              >
                <FacultyDashboardPage />
              </RoleProtectedRoute>
            }
          />

          {/* Support */}
          <Route
            path="/support/chat-queue"
            element={
              <RoleProtectedRoute allowedRoles={[ROLES.SUPPORT_TECHNICIAN]}>
                <SupportChatQueuePage />
              </RoleProtectedRoute>
            }
          />

          {/* Catch-all -> dispatcher (sends to login or the user's landing) */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
