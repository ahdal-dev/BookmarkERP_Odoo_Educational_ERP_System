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

// Admin Dashboard
import CommandCenterPage from './pages/admin/CommandCenterPage/CommandCenterPage';
import RolesPage from './pages/admin/RolesPage/RolesPage';
import AIServicesPage from './pages/admin/AIServicesPage/AIServicesPage';
import KnowledgeBasePage from './pages/admin/KnowledgeBasePage/KnowledgeBasePage';
import AnalyticsPage from './pages/admin/AnalyticsPage/AnalyticsPage';
import SecurityPage from './pages/admin/SecurityPage/SecurityPage';
import SystemPage from './pages/admin/SystemPage/SystemPage';
import ContentPage from './pages/admin/ContentPage/ContentPage';
import SupportPage from './pages/admin/SupportPage/SupportPage';
import UserDetailPage from './pages/admin/UserDetailPage/UserDetailPage';

// Role landing pages (scaffolded — see docs/User_stories/Missing_Views_ToDo.md)
import StudentDashboardPage from './pages/student/StudentDashboardPage';
import FacultyDashboardPage from './pages/faculty/FacultyDashboardPage';
import SupportChatQueuePage from './pages/support/SupportChatQueuePage';
import ApplicationStatusPage from './pages/admissions/ApplicationStatusPage';
import ChatbotPage from './pages/ChatbotPage/ChatbotPage';
import RoleProtectedRoute from './components/RoleProtectedRoute/RoleProtectedRoute';
import { ROLES } from './config/roles';

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<LoginPage />} />

          {/* Protected Routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />

          {/* Admin Dashboard */}
          <Route
            path="/admin"
            element={
              <RoleProtectedRoute allowedRoles={[ROLES.SUPER_ADMIN]}>
                <CommandCenterPage />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/admin/roles"
            element={
              <RoleProtectedRoute allowedRoles={[ROLES.SUPER_ADMIN]}>
                <RolesPage />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/admin/ai"
            element={
              <RoleProtectedRoute allowedRoles={[ROLES.SUPER_ADMIN]}>
                <AIServicesPage />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/admin/knowledge-base"
            element={
              <RoleProtectedRoute allowedRoles={[ROLES.SUPER_ADMIN]}>
                <KnowledgeBasePage />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/admin/analytics"
            element={
              <RoleProtectedRoute allowedRoles={[ROLES.SUPER_ADMIN]}>
                <AnalyticsPage />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/admin/security"
            element={
              <RoleProtectedRoute allowedRoles={[ROLES.SUPER_ADMIN]}>
                <SecurityPage />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/admin/system"
            element={
              <RoleProtectedRoute allowedRoles={[ROLES.SUPER_ADMIN]}>
                <SystemPage />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/admin/content"
            element={
              <RoleProtectedRoute allowedRoles={[ROLES.SUPER_ADMIN]}>
                <ContentPage />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/admin/support"
            element={
              <RoleProtectedRoute allowedRoles={[ROLES.SUPER_ADMIN]}>
                <SupportPage />
              </RoleProtectedRoute>
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
              <RoleProtectedRoute allowedRoles={[ROLES.SUPER_ADMIN]}>
                <UserManagementPage />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/admin/users/:id"
            element={
              <RoleProtectedRoute allowedRoles={[ROLES.SUPER_ADMIN]}>
                <UserDetailPage />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/admin/admissions"
            element={
              <ProtectedRoute roles={['admin', 'officer', 'super_admin']}>
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
          <Route
            path="/student/assistant"
            element={
              <RoleProtectedRoute allowedRoles={[ROLES.STUDENT]}>
                <ChatbotPage />
              </RoleProtectedRoute>
            }
          />

          {/* Faculty space */}
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

          {/* Catch-all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
