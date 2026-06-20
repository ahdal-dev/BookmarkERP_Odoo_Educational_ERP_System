import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute/ProtectedRoute';
import RoleProtectedRoute from './components/RoleProtectedRoute/RoleProtectedRoute';
import RoleRouter from './components/RoleRouter/RoleRouter';
import { ROLES } from './config/roles';

import LoginPage from './pages/LoginPage/LoginPage';
import LandingPage from './pages/LandingPage/LandingPage';
import ChangePasswordPage from './pages/ChangePasswordPage/ChangePasswordPage';
import UnauthorizedPage from './pages/UnauthorizedPage/UnauthorizedPage';
import NotificationsPage from './pages/notifications/NotificationsPage';
import SettingsPage from './pages/settings/SettingsPage';
import HelpPage from './pages/HelpPage/HelpPage';

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

// Role landing pages
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
// Admissions
import AdmissionsPortalPage from './pages/admissions/AdmissionsPortalPage';
import ApplicationReviewPage from './pages/admissions/ApplicationReviewPage';
import OfficerDocumentsPage from './pages/admissions/OfficerDocumentsPage';
// Apply workflow
import ApplyPersonalInfoPage from './pages/apply/ApplyPersonalInfoPage';
import ApplyAcademicHistoryPage from './pages/apply/ApplyAcademicHistoryPage';
import ApplyReviewPage from './pages/apply/ApplyReviewPage';
import { ApplicationProvider } from './context/ApplicationContext';
// Admin legacy
import AuditLogPage from './pages/admin/AuditLogPage';
import SystemSettingsPage from './pages/admin/SystemSettingsPage';
// Security hardening
import DataRetentionPage from './pages/admin/security/DataRetentionPage';
import BackupsPage from './pages/admin/security/BackupsPage';
import ServiceAccountsPage from './pages/admin/security/ServiceAccountsPage';
import MFASecurityPage from './pages/settings/MFASecurityPage';

const FACULTY_ROLES = [ROLES.INSTRUCTOR, ROLES.ACADEMIC_ADVISOR, ROLES.DEPARTMENT_CHAIR];

export default function App() {
  return (
    <AuthProvider>
      <ApplicationProvider>
      <BrowserRouter>
        <Routes>
          {/* Public */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/change-password" element={<ChangePasswordPage />} />
          <Route path="/unauthorized" element={<UnauthorizedPage />} />
          <Route path="/admissions" element={<AdmissionsPortalPage />} />
          <Route path="/admissions/status" element={<ApplicationStatusPage />} />

          {/* Public landing */}
          <Route path="/" element={<LandingPage />} />

          {/* Post-login dispatcher */}
          <Route path="/dashboard" element={<RoleRouter />} />

          {/* Cross-role pages */}
          <Route path="/notifications" element={<ProtectedRoute><NotificationsPage /></ProtectedRoute>} />
          <Route path="/settings" element={<ProtectedRoute><SettingsPage /></ProtectedRoute>} />
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
          <Route path="/profile" element={<ProtectedRoute><SettingsPage /></ProtectedRoute>} />
          <Route path="/help" element={<ProtectedRoute><HelpPage /></ProtectedRoute>} />
          <Route path="/handbook" element={<ProtectedRoute><HelpPage /></ProtectedRoute>} />
          <Route path="/dashboard" element={<Navigate to="/" replace />} />
          <Route path="/support" element={<Navigate to="/support/tickets" replace />} />
          <Route path="/apply/academic" element={<Navigate to="/admissions/status" replace />} />

          {/* App Launcher */}
          <Route
            path="/apps"
            element={
              <RoleProtectedRoute allowedRoles={[ROLES.SUPER_ADMIN]}>
                <DashboardPage />
              </RoleProtectedRoute>
            }
          />

          {/* Shared protected */}
          <Route path="/registration" element={<ProtectedRoute><RegistrationPage /></ProtectedRoute>} />
          <Route path="/petitions/new" element={<ProtectedRoute><PetitionFormPage /></ProtectedRoute>} />

          {/* Apply workflow — public, ApplicationProvider lives above BrowserRouter */}
          <Route path="/apply/personal-info" element={<ApplyPersonalInfoPage />} />
          <Route path="/apply/academic-history" element={<ApplyAcademicHistoryPage />} />
          <Route path="/apply/documents" element={<DocumentVerificationPage />} />
          <Route path="/apply/review" element={<ApplyReviewPage />} />

          {/* Admin Dashboard */}
          <Route path="/admin" element={<RoleProtectedRoute allowedRoles={[ROLES.SUPER_ADMIN]}><CommandCenterPage /></RoleProtectedRoute>} />
          <Route path="/admin/roles" element={<RoleProtectedRoute allowedRoles={[ROLES.SUPER_ADMIN]}><RolesPage /></RoleProtectedRoute>} />
          <Route path="/admin/ai" element={<RoleProtectedRoute allowedRoles={[ROLES.SUPER_ADMIN]}><AIServicesPage /></RoleProtectedRoute>} />
          <Route path="/admin/knowledge-base" element={<RoleProtectedRoute allowedRoles={[ROLES.SUPER_ADMIN]}><KnowledgeBasePage /></RoleProtectedRoute>} />
          <Route path="/admin/analytics" element={<RoleProtectedRoute allowedRoles={[ROLES.SUPER_ADMIN]}><AnalyticsPage /></RoleProtectedRoute>} />
          <Route path="/admin/security" element={<RoleProtectedRoute allowedRoles={[ROLES.SUPER_ADMIN]}><SecurityPage /></RoleProtectedRoute>} />
          <Route path="/admin/system" element={<RoleProtectedRoute allowedRoles={[ROLES.SUPER_ADMIN]}><SystemPage /></RoleProtectedRoute>} />
          <Route path="/admin/content" element={<RoleProtectedRoute allowedRoles={[ROLES.SUPER_ADMIN]}><ContentPage /></RoleProtectedRoute>} />
          <Route path="/admin/support" element={<RoleProtectedRoute allowedRoles={[ROLES.SUPER_ADMIN]}><SupportPage /></RoleProtectedRoute>} />
          <Route path="/admin/users" element={<RoleProtectedRoute allowedRoles={[ROLES.SUPER_ADMIN]}><UserManagementPage /></RoleProtectedRoute>} />
          <Route path="/admin/users/:id" element={<RoleProtectedRoute allowedRoles={[ROLES.SUPER_ADMIN]}><UserDetailPage /></RoleProtectedRoute>} />
          <Route path="/admin/admissions" element={<ProtectedRoute roles={['admin', 'officer', 'super_admin']}><AdmissionPipelinePage /></ProtectedRoute>} />
          <Route path="/admin/petitions" element={<ProtectedRoute roles={['admin', 'officer']}><PetitionTrackingPage /></ProtectedRoute>} />
          <Route path="/admin/settings/registration-rules" element={<RoleProtectedRoute allowedRoles={[ROLES.SUPER_ADMIN, ROLES.REGISTRAR]}><InstitutionalRulesetPage /></RoleProtectedRoute>} />
          <Route path="/admin/audit-log" element={<ProtectedRoute roles={['admin']}><AuditLogPage /></ProtectedRoute>} />
          <Route path="/admin/settings" element={<ProtectedRoute roles={['admin']}><SystemSettingsPage /></ProtectedRoute>} />

          {/* Security hardening — admin */}
          <Route path="/admin/data-retention" element={<RoleProtectedRoute allowedRoles={[ROLES.SUPER_ADMIN]}><DataRetentionPage /></RoleProtectedRoute>} />
          <Route path="/admin/backups" element={<RoleProtectedRoute allowedRoles={[ROLES.SUPER_ADMIN]}><BackupsPage /></RoleProtectedRoute>} />
          <Route path="/admin/service-accounts" element={<RoleProtectedRoute allowedRoles={[ROLES.SUPER_ADMIN]}><ServiceAccountsPage /></RoleProtectedRoute>} />
          {/* MFA setup — public route (also serves enforced first-login setup, which has no session yet) */}
          <Route path="/settings/security/mfa" element={<MFASecurityPage />} />

          {/* Student */}
          <Route path="/student/dashboard" element={<RoleProtectedRoute allowedRoles={[ROLES.STUDENT]}><StudentDashboardPage /></RoleProtectedRoute>} />
          <Route path="/student/assistant" element={<RoleProtectedRoute allowedRoles={[ROLES.STUDENT]}><ChatbotPage /></RoleProtectedRoute>} />
          <Route path="/student/grades" element={<RoleProtectedRoute allowedRoles={[ROLES.STUDENT]}><GradesPage /></RoleProtectedRoute>} />
          <Route path="/student/petitions" element={<RoleProtectedRoute allowedRoles={[ROLES.STUDENT]}><PetitionListPage /></RoleProtectedRoute>} />

          {/* Faculty */}
          <Route path="/faculty/dashboard" element={<RoleProtectedRoute allowedRoles={FACULTY_ROLES}><FacultyDashboardPage /></RoleProtectedRoute>} />
          <Route path="/faculty/courses" element={<RoleProtectedRoute allowedRoles={FACULTY_ROLES}><ClassRosterPage /></RoleProtectedRoute>} />
          <Route path="/faculty/courses/:courseId" element={<RoleProtectedRoute allowedRoles={FACULTY_ROLES}><ClassRosterPage /></RoleProtectedRoute>} />
          <Route path="/faculty/petitions" element={<RoleProtectedRoute allowedRoles={FACULTY_ROLES}><FacultyPetitionQueuePage /></RoleProtectedRoute>} />
          <Route path="/faculty/petitions/:id" element={<RoleProtectedRoute allowedRoles={FACULTY_ROLES}><PetitionReviewPage /></RoleProtectedRoute>} />
          <Route path="/faculty/advisees" element={<RoleProtectedRoute allowedRoles={[ROLES.ACADEMIC_ADVISOR, ROLES.DEPARTMENT_CHAIR]}><AdviseeListPage /></RoleProtectedRoute>} />
          <Route path="/faculty/advisees/:studentId" element={<RoleProtectedRoute allowedRoles={[ROLES.ACADEMIC_ADVISOR, ROLES.DEPARTMENT_CHAIR]}><AdviseeProfilePage /></RoleProtectedRoute>} />
          <Route path="/faculty/chair/petitions" element={<RoleProtectedRoute allowedRoles={[ROLES.DEPARTMENT_CHAIR]}><ChairPetitionQueuePage /></RoleProtectedRoute>} />
          <Route path="/faculty/chair/petitions/:id" element={<RoleProtectedRoute allowedRoles={[ROLES.DEPARTMENT_CHAIR]}><PetitionOverridePage /></RoleProtectedRoute>} />
          <Route path="/faculty/chair/students" element={<RoleProtectedRoute allowedRoles={[ROLES.DEPARTMENT_CHAIR]}><DepartmentStudentRecordsPage /></RoleProtectedRoute>} />

          {/* Registrar */}
          <Route path="/registrar/dashboard" element={<RoleProtectedRoute allowedRoles={[ROLES.REGISTRAR]}><RegistrarDashboardPage /></RoleProtectedRoute>} />
          <Route path="/registrar/timeslots" element={<RoleProtectedRoute allowedRoles={[ROLES.REGISTRAR]}><TimeSlotConfiguratorPage /></RoleProtectedRoute>} />
          <Route path="/registrar/courses" element={<RoleProtectedRoute allowedRoles={[ROLES.REGISTRAR]}><CourseCatalogManagerPage /></RoleProtectedRoute>} />
          <Route path="/registrar/enrollment" element={<RoleProtectedRoute allowedRoles={[ROLES.REGISTRAR]}><EnrollmentMonitorPage /></RoleProtectedRoute>} />

          {/* Support */}
          <Route path="/support/chat-queue" element={<RoleProtectedRoute allowedRoles={[ROLES.SUPPORT_TECHNICIAN]}><SupportChatQueuePage /></RoleProtectedRoute>} />
          <Route path="/support/chat/:sessionId" element={<RoleProtectedRoute allowedRoles={[ROLES.SUPPORT_TECHNICIAN]}><ChatSessionPage /></RoleProtectedRoute>} />
          <Route path="/support/tickets" element={<RoleProtectedRoute allowedRoles={[ROLES.SUPPORT_TECHNICIAN]}><TicketListPage /></RoleProtectedRoute>} />

          {/* Admissions Officer */}
          <Route path="/admissions/officer" element={<RoleProtectedRoute allowedRoles={[ROLES.ADMISSION_OFFICER, ROLES.SUPER_ADMIN]}><AdmissionPipelinePage /></RoleProtectedRoute>} />
          <Route path="/admissions/officer/application/:id" element={<RoleProtectedRoute allowedRoles={[ROLES.ADMISSION_OFFICER, ROLES.SUPER_ADMIN]}><ApplicationReviewPage /></RoleProtectedRoute>} />
          <Route path="/admissions/officer/documents" element={<RoleProtectedRoute allowedRoles={[ROLES.ADMISSION_OFFICER, ROLES.SUPER_ADMIN]}><OfficerDocumentsPage /></RoleProtectedRoute>} />

          {/* Catch-all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
      </ApplicationProvider>
    </AuthProvider>
  );
}
