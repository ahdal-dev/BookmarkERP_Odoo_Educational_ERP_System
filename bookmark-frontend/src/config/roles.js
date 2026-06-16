// src/config/roles.js
// Single source of truth for roles + landing routes.
// Mirrors the FastAPI UserRole enum (api_gateway/fastapi_app/main.py)
// and the Odoo security groups (edu_mang_auth/security/security.xml).

export const ROLES = {
  PROSPECTIVE_STUDENT: 'prospective_student',
  ADMISSION_OFFICER: 'admission_officer',
  STUDENT: 'student',
  INSTRUCTOR: 'instructor',
  ACADEMIC_ADVISOR: 'academic_advisor',
  DEPARTMENT_CHAIR: 'department_chair',
  REGISTRAR: 'registrar',
  SUPPORT_TECHNICIAN: 'support_technician',
  SUPER_ADMIN: 'super_admin',
};

// Where each role lands immediately after login.
export const ROLE_LANDING = {
  [ROLES.SUPER_ADMIN]: '/apps',
  [ROLES.REGISTRAR]: '/apps',
  [ROLES.ADMISSION_OFFICER]: '/apps',
  [ROLES.STUDENT]: '/student/dashboard',
  [ROLES.INSTRUCTOR]: '/faculty/dashboard',
  [ROLES.ACADEMIC_ADVISOR]: '/faculty/dashboard',
  [ROLES.DEPARTMENT_CHAIR]: '/faculty/dashboard',
  [ROLES.SUPPORT_TECHNICIAN]: '/support/chat-queue',
  [ROLES.PROSPECTIVE_STUDENT]: '/admissions/status',
};

// Fallback if the JWT carries an unknown / missing role.
export const DEFAULT_LANDING = '/unauthorized';

export function landingFor(role) {
  return ROLE_LANDING[role] || DEFAULT_LANDING;
}
