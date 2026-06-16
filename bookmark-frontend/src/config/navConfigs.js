/* ============================================================
   NAV CONFIGS — Sidebar navigation arrays for each app context
   ============================================================ */

// Icons are rendered inline as SVG strings in AppShell;
// here we use icon identifiers that AppShell maps to SVG components.

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
  { icon: 'advising', label: 'Advising', path: '/advising' },
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
