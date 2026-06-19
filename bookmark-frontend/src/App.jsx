import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute/ProtectedRoute';
import RoleProtectedRoute from './components/RoleProtectedRoute/RoleProtectedRoute';
import RoleRouter from './components/RoleRouter/RoleRouter';
import { ROLES } from './config/roles';

import LoginPage from './pages/LoginPage/LoginPage';
import ChangePasswordPage from './pages/ChangePasswordPage/ChangePasswordPage';
import UnauthorizedPage from './pages/UnauthorizedPage/UnauthorizedPage';
import NotificationsPage from './pages/notifications/NotificationsPage';
import SettingsPage from './pages/settings/SettingsPage';

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
import ChatbotPage from './pages/ChatbotPage/ChatbotPage';

// Student
import GradesPage from './pages/student/GradesPage';
import PetitionListPage from './pages/student/PetitionListPage';
// Faculty / Advisor / Chair
import ClassRosterPage from './pages/faculty/ClassRosterPage';
import FacultyPetitionQueuePage from './pages/faculty/FacultyPetitionQueuePage';
import PetitionReviewPage from './pages/faculty/PetitionReviewPage';
import AdviseeListPage from './pages/faculty/AdviseeListPage';
import AdviseeProfilePage from './pages/faculty/AdviseeProfilePage';
import ChairPetitionQueuePage from './pages/faculty/ChairPetitionQueuePage';
import PetitionOverridePage from './pages/faculty/PetitionOverridePage';
import DepartmentStudentRecordsPage from './pages/faculty/DepartmentStudentRecordsPage';
// Registrar
import RegistrarDashboardPage from './pages/registrar/RegistrarDashboardPage';
import TimeSlotConfiguratorPage from './pages/registrar/TimeSlotConfiguratorPage';
import CourseCatalogManagerPage from './pages/registrar/CourseCatalogManagerPage';
import EnrollmentMonitorPage from './pages/registrar/EnrollmentMonitorPage';
// Support
import ChatSessionPage from './pages/support/ChatSessionPage';
import TicketListPage from './pages/support/TicketListPage';
// Admissions (public + officer)
import AdmissionsPortalPage from './pages/admissions/AdmissionsPortalPage';
import ApplicationReviewPage from './pages/admissions/ApplicationReviewPage';
// Admin
import AuditLogPage from './pages/admin/AuditLogPage';
import SystemSettingsPage from './pages/admin/SystemSettingsPage';

const FACULTY_ROLES = [ROLES.INSTRUCTOR, ROLES.ACADEMIC_ADVISOR, ROLES.DEPARTMENT_CHAIR];

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
          <Route path="/change-password" element={<ChangePasswordPage />} />
          <Route path="/unauthorized" element={<UnauthorizedPage />} />
          <Route path="/admissions" element={<AdmissionsPortalPage />} />
          <Route path="/admissions/status" element={<ApplicationStatusPage />} />

          {/* Post-login dispatcher */}
          <Route path="/" element={<RoleRouter />} />

          {/* Cross-role pages — available to every authenticated user */}
          <Route
            path="/notifications"
            element={
              <ProtectedRoute>
                <NotificationsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <ProtectedRoute>
                <SettingsPage />
              </ProtectedRoute>
            }
          />

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
          <Route
            path="/student/assistant"
            element={
              <RoleProtectedRoute allowedRoles={[ROLES.STUDENT]}>
                <ChatbotPage />
              </RoleProtectedRoute>
            }
          />
          <Route path="/student/grades" element={<RoleProtectedRoute allowedRoles={[ROLES.STUDENT]}><GradesPage /></RoleProtectedRoute>} />
          <Route path="/student/petitions" element={<RoleProtectedRoute allowedRoles={[ROLES.STUDENT]}><PetitionListPage /></RoleProtectedRoute>} />

          {/* Faculty (Instructor / Advisor / Chair) */}
          <Route path="/faculty/courses" element={<RoleProtectedRoute allowedRoles={FACULTY_ROLES}><ClassRosterPage /></RoleProtectedRoute>} />
          <Route path="/faculty/courses/:courseId" element={<RoleProtectedRoute allowedRoles={FACULTY_ROLES}><ClassRosterPage /></RoleProtectedRoute>} />
          <Route path="/faculty/petitions" element={<RoleProtectedRoute allowedRoles={FACULTY_ROLES}><FacultyPetitionQueuePage /></RoleProtectedRoute>} />
          <Route path="/faculty/petitions/:id" element={<RoleProtectedRoute allowedRoles={FACULTY_ROLES}><PetitionReviewPage /></RoleProtectedRoute>} />
          {/* Advisor */}
          <Route path="/faculty/advisees" element={<RoleProtectedRoute allowedRoles={[ROLES.ACADEMIC_ADVISOR, ROLES.DEPARTMENT_CHAIR]}><AdviseeListPage /></RoleProtectedRoute>} />
          <Route path="/faculty/advisees/:studentId" element={<RoleProtectedRoute allowedRoles={[ROLES.ACADEMIC_ADVISOR, ROLES.DEPARTMENT_CHAIR]}><AdviseeProfilePage /></RoleProtectedRoute>} />
          {/* Chair */}
          <Route path="/faculty/chair/petitions" element={<RoleProtectedRoute allowedRoles={[ROLES.DEPARTMENT_CHAIR]}><ChairPetitionQueuePage /></RoleProtectedRoute>} />
          <Route path="/faculty/chair/petitions/:id" element={<RoleProtectedRoute allowedRoles={[ROLES.DEPARTMENT_CHAIR]}><PetitionOverridePage /></RoleProtectedRoute>} />
          <Route path="/faculty/chair/students" element={<RoleProtectedRoute allowedRoles={[ROLES.DEPARTMENT_CHAIR]}><DepartmentStudentRecordsPage /></RoleProtectedRoute>} />

          {/* Registrar */}
          <Route path="/registrar/dashboard" element={<RoleProtectedRoute allowedRoles={[ROLES.REGISTRAR]}><RegistrarDashboardPage /></RoleProtectedRoute>} />
          <Route path="/registrar/timeslots" element={<RoleProtectedRoute allowedRoles={[ROLES.REGISTRAR]}><TimeSlotConfiguratorPage /></RoleProtectedRoute>} />
          <Route path="/registrar/courses" element={<RoleProtectedRoute allowedRoles={[ROLES.REGISTRAR]}><CourseCatalogManagerPage /></RoleProtectedRoute>} />
          <Route path="/registrar/enrollment" element={<RoleProtectedRoute allowedRoles={[ROLES.REGISTRAR]}><EnrollmentMonitorPage /></RoleProtectedRoute>} />

          {/* Support */}
          <Route path="/support/chat/:sessionId" element={<RoleProtectedRoute allowedRoles={[ROLES.SUPPORT_TECHNICIAN]}><ChatSessionPage /></RoleProtectedRoute>} />
          <Route path="/support/tickets" element={<RoleProtectedRoute allowedRoles={[ROLES.SUPPORT_TECHNICIAN]}><TicketListPage /></RoleProtectedRoute>} />

          {/* Admissions Officer */}
          <Route path="/admissions/officer" element={<RoleProtectedRoute allowedRoles={[ROLES.ADMISSION_OFFICER, ROLES.SUPER_ADMIN]}><AdmissionPipelinePage /></RoleProtectedRoute>} />
          <Route path="/admissions/officer/application/:id" element={<RoleProtectedRoute allowedRoles={[ROLES.ADMISSION_OFFICER, ROLES.SUPER_ADMIN]}><ApplicationReviewPage /></RoleProtectedRoute>} />

          {/* Admin */}
          <Route path="/admin/audit-log" element={<ProtectedRoute roles={['admin']}><AuditLogPage /></ProtectedRoute>} />
          <Route path="/admin/settings" element={<ProtectedRoute roles={['admin']}><SystemSettingsPage /></ProtectedRoute>} />

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
