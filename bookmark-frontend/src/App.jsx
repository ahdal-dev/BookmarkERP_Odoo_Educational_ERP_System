import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import RoleProtectedRoute from './components/RoleProtectedRoute/RoleProtectedRoute';
import RoleRouter from './components/RoleRouter/RoleRouter';
import { ROLES } from './config/roles';

import LoginPage from './pages/LoginPage/LoginPage';
import UnauthorizedPage from './pages/UnauthorizedPage/UnauthorizedPage';

// App Launcher (existing component, now mounted at /apps)
import DashboardPage from './pages/DashboardPage/DashboardPage';

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
