// Sidebar nav configs for each app context
// Icon keys are resolved to SVG paths inside AppShell

import { ROLES } from './roles';

export const registrationNav = [
  { icon: 'dashboard', label: 'Dashboard', path: '/dashboard' },
  { icon: 'program', label: 'Program', path: '/program' },
  {
    icon: 'registration',
    label: 'Registration',
    path: '/registration',
    active: true,
    children: [
      { label: 'Registrees', path: '/registration/registrees' },
    ],
  },
  { icon: 'notifications', label: 'Notifications', path: '/notifications' },
  { icon: 'faculty', label: 'Faculty', path: '/faculty' },
  { icon: 'profile', label: 'Profile', path: '/profile' },
  { icon: 'students', label: 'Students', path: '/students' },
];

export const adminSettingsNav = [
  { icon: 'dashboard', label: 'Dashboard', path: '/dashboard' },
  { icon: 'students', label: 'Student Lifecycle', path: '/admin/students' },
  { icon: 'program', label: 'Course Management', path: '/admin/courses' },
  { icon: 'registration', label: 'Registration', path: '/admin/registration' },
  { icon: 'admission', label: 'Admissions', path: '/admin/admissions' },
  { icon: 'settings', label: 'Settings', path: '/admin/settings/registration-rules', active: true },
];

export const adminUsersNav = [
  { icon: 'dashboard', label: 'Dashboard', path: '/dashboard' },
  {
    icon: 'admin',
    label: 'Admin Control',
    path: '/admin/users',
    active: true,
    children: [
      { label: 'Bookmark', path: '/admin/bookmark' },
      { label: 'Users', path: '/admin/users', active: true },
      { label: 'Managers', path: '/admin/managers' },
    ],
  },
  { icon: 'profile', label: 'Profile', path: '/profile' },
  { icon: 'management', label: 'Management', path: '/admin/management' },
  { icon: 'settings', label: 'Settings', path: '/admin/settings' },
];

export const admissionsNav = [
  { icon: 'dashboard', label: 'Dashboard', path: '/dashboard' },
  { icon: 'students', label: 'Students', path: '/admin/students' },
  { icon: 'faculty', label: 'Faculty', path: '/admin/faculty' },
  { icon: 'admission', label: 'Admissions', path: '/admin/admissions', active: true },
  { icon: 'genders', label: 'Genders', path: '/admin/genders' },
  { icon: 'reports', label: 'Reports', path: '/admin/reports' },
  { icon: 'contacts', label: 'Contacts', path: '/admin/contacts' },
  { icon: 'management', label: 'Management', path: '/admin/management' },
  { icon: 'settings', label: 'Settings', path: '/admin/settings' },
];

export const petitionsStudentNav = [
  { icon: 'dashboard', label: 'Dashboard', path: '/dashboard' },
  { icon: 'grades', label: 'Grades', path: '/grades' },
  { icon: 'registration', label: 'Enrollment', path: '/enrollment' },
  { icon: 'petition', label: 'Petitions', path: '/petitions/new', active: true },
  { icon: 'chat', label: 'Assistant', path: '/student/assistant' },
  { icon: 'advising', label: 'Advising', path: '/advising' },
  { icon: 'handbook', label: 'Handbook', path: '/handbook' },
];

// Student nav for the AI Assistant (chatbot) view.
export const chatbotStudentNav = [
  { icon: 'dashboard', label: 'Dashboard', path: '/student/dashboard' },
  { icon: 'grades', label: 'Grades', path: '/grades' },
  { icon: 'registration', label: 'Enrollment', path: '/enrollment' },
  { icon: 'petition', label: 'Petitions', path: '/petitions/new' },
  { icon: 'chat', label: 'Assistant', path: '/student/assistant', active: true },
  { icon: 'handbook', label: 'Handbook', path: '/handbook' },
];

export const petitionsAdminNav = [
  { icon: 'dashboard', label: 'Dashboard', path: '/dashboard' },
  { icon: 'petition', label: 'Petitions', path: '/admin/petitions', active: true },
  { icon: 'academic', label: 'Academic', path: '/admin/academic' },
  { icon: 'appeals', label: 'Appeals', path: '/admin/appeals' },
  { icon: 'documents', label: 'Documents', path: '/admin/documents' },
  { icon: 'settings', label: 'Settings', path: '/admin/settings' },
];

export const studentNav = [
  { icon: 'dashboard', label: 'Dashboard', path: '/student/dashboard' },
  { icon: 'grades', label: 'Grades', path: '/student/grades' },
  { icon: 'registration', label: 'Enrollment', path: '/registration' },
  { icon: 'petition', label: 'Petitions', path: '/student/petitions' },
  { icon: 'chat', label: 'Assistant', path: '/student/assistant' },
  { icon: 'handbook', label: 'Handbook', path: '/handbook' },
];

export const facultyNav = [
  { icon: 'dashboard', label: 'Dashboard', path: '/faculty/dashboard' },
  { icon: 'program', label: 'My Courses', path: '/faculty/courses' },
  { icon: 'petition', label: 'Petition Queue', path: '/faculty/petitions' },
  { icon: 'profile', label: 'Profile', path: '/profile' },
];

export const advisorNav = [
  { icon: 'dashboard', label: 'Dashboard', path: '/faculty/dashboard' },
  { icon: 'advising', label: 'My Advisees', path: '/faculty/advisees' },
  { icon: 'petition', label: 'Petition Queue', path: '/faculty/petitions' },
  { icon: 'profile', label: 'Profile', path: '/profile' },
];

export const chairNav = [
  { icon: 'dashboard', label: 'Dashboard', path: '/faculty/dashboard' },
  { icon: 'appeals', label: 'Department Petitions', path: '/faculty/chair/petitions' },
  { icon: 'students', label: 'Department Students', path: '/faculty/chair/students' },
  { icon: 'petition', label: 'Petition Queue', path: '/faculty/petitions' },
];

export const registrarNav = [
  { icon: 'dashboard', label: 'Dashboard', path: '/registrar/dashboard' },
  { icon: 'management', label: 'Time Slots', path: '/registrar/timeslots' },
  { icon: 'program', label: 'Course Catalog', path: '/registrar/courses' },
  { icon: 'reports', label: 'Enrollment Monitor', path: '/registrar/enrollment' },
  { icon: 'settings', label: 'Ruleset', path: '/admin/settings/registration-rules' },
];

export const supportNav = [
  { icon: 'chat', label: 'Live Queue', path: '/support/chat-queue' },
  { icon: 'documents', label: 'Tickets', path: '/support/tickets' },
  { icon: 'profile', label: 'Profile', path: '/profile' },
];

export const admissionsOfficerNav = [
  { icon: 'dashboard', label: 'Dashboard', path: '/apps' },
  { icon: 'admission', label: 'Pipeline', path: '/admissions/officer' },
  { icon: 'documents', label: 'Documents', path: '/apply/documents' },
  { icon: 'reports', label: 'Reports', path: '/admin/reports' },
];

export const adminNav = [
  { icon: 'dashboard', label: 'Apps', path: '/apps' },
  { icon: 'admin', label: 'Users', path: '/admin/users' },
  { icon: 'reports', label: 'Audit Log', path: '/admin/audit-log' },
  { icon: 'settings', label: 'Settings', path: '/admin/settings' },
];

const ROLE_NAV = {
  [ROLES.STUDENT]: studentNav,
  [ROLES.INSTRUCTOR]: facultyNav,
  [ROLES.ACADEMIC_ADVISOR]: advisorNav,
  [ROLES.DEPARTMENT_CHAIR]: chairNav,
  [ROLES.REGISTRAR]: registrarNav,
  [ROLES.SUPPORT_TECHNICIAN]: supportNav,
  [ROLES.ADMISSION_OFFICER]: admissionsOfficerNav,
  [ROLES.SUPER_ADMIN]: adminNav,
};

const SHARED_NAV = [
  { icon: 'notifications', label: 'Notifications', path: '/notifications' },
  { icon: 'settings', label: 'Account Settings', path: '/settings' },
];

export function navForRole(role) {
  const base = ROLE_NAV[role] || studentNav;
  const paths = new Set(base.map((i) => i.path));
  const labels = new Set(base.map((i) => i.label));
  const extras = SHARED_NAV.filter((i) => !paths.has(i.path) && !labels.has(i.label));
  return [...base, ...extras];
}

// Admin dashboard nav
export const adminDashboardNav = [
  { icon: 'dashboard', label: 'Command Center', path: '/admin' },
  { icon: 'students', label: 'User Management', path: '/admin/users' },
  { icon: 'admin', label: 'Roles & Permissions', path: '/admin/roles' },
  { icon: 'ai', label: 'AI Services', path: '/admin/ai' },
  { icon: 'documents', label: 'Knowledge Base', path: '/admin/knowledge-base' },
  { icon: 'reports', label: 'Analytics', path: '/admin/analytics' },
  { icon: 'security', label: 'Security Center', path: '/admin/security' },
  { icon: 'management', label: 'Content & Config', path: '/admin/content' },
  { icon: 'chat', label: 'Support', path: '/admin/support' },
  { icon: 'settings', label: 'System', path: '/admin/system' },
];
