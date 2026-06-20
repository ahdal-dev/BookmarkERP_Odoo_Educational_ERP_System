import axios from 'axios';

/* ============================================================
   API GATEWAY — Axios Client
   Configured for FastAPI API Gateway with JWT auth
   ============================================================ */

const API_BASE_URL = import.meta.env.VITE_API_GATEWAY_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// --- Request Interceptor: Attach JWT Bearer token ---
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('bookmark_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// --- Response Interceptor: Handle 401 → redirect to /login ---
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('bookmark_token');
      localStorage.removeItem('bookmark_user');

      // Public/guest flows (prospective-student application, admissions) must
      // surface errors inline instead of being yanked to the login page.
      const path = window.location.pathname;
      const isPublicFlow = path.startsWith('/apply') || path.startsWith('/admissions');

      // Don't redirect if already on login page or inside a public flow
      if (path !== '/login' && !isPublicFlow) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

/* ============================================================
   AUTH ENDPOINTS
   ============================================================ */

export const authAPI = {
  /**
   * Authenticate with Odoo via the API Gateway.
   * The gateway proxies to Odoo's /web/session/authenticate and returns a JWT.
   */
  login: async (login, password) => {
    const response = await api.post('/api/v1/auth/login', {
      login,
      password,
      db: import.meta.env.VITE_ODOO_DB || 'edu_demo_new',
    });
    return response.data;
  },

  /** Check current session validity */
  checkSession: async () => {
    const response = await api.get('/api/v1/auth/session');
    return response.data;
  },

  /** Logout and invalidate session */
  logout: async () => {
    const response = await api.post('/api/v1/auth/logout');
    localStorage.removeItem('bookmark_token');
    localStorage.removeItem('bookmark_user');
    return response.data;
  },

  /** Change the authenticated user's password. Pass an explicit token to use a
   *  short-lived reset token during the expiry-forced flow (no stored session). */
  changePassword: async (currentPassword, newPassword, token) => {
    const config = token ? { headers: { Authorization: `Bearer ${token}` } } : undefined;
    const response = await api.post('/api/v1/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    }, config);
    return response.data;
  },

  /* ---- Multi-Factor Authentication (TOTP) ---- */

  /** Current user's MFA status */
  mfaStatus: async () => {
    const response = await api.get('/api/v1/auth/mfa/status');
    return response.data;
  },

  /** Begin enrolment — returns { otpauth_uri, qr_png_base64, secret }.
   *  Pass an explicit token (the setup/mfa token from login) when the user
   *  isn't fully authenticated yet. */
  mfaSetup: async (token) => {
    const config = token ? { headers: { Authorization: `Bearer ${token}` } } : undefined;
    const response = await api.post('/api/v1/auth/mfa/setup', {}, config);
    return response.data;
  },

  /** Confirm enrolment — returns { backup_codes } */
  mfaVerifySetup: async (code, token) => {
    const config = token ? { headers: { Authorization: `Bearer ${token}` } } : undefined;
    const response = await api.post('/api/v1/auth/mfa/verify-setup', { code }, config);
    return response.data;
  },

  /** Complete the login challenge — returns full tokens */
  mfaVerify: async (mfaToken, code) => {
    const response = await api.post('/api/v1/auth/mfa/verify', {
      mfa_token: mfaToken,
      code,
    });
    return response.data;
  },

  /** Disable MFA (requires current password + a valid code) */
  mfaDisable: async (currentPassword, code) => {
    const response = await api.post('/api/v1/auth/mfa/disable', {
      current_password: currentPassword,
      code,
    });
    return response.data;
  },
};

/* ============================================================
   MODULE MANAGEMENT ENDPOINTS (Super-Admin)
   ============================================================ */

export const modulesAPI = {
  /** List available/installable Odoo modules */
  listModules: async () => {
    const response = await api.get('/api/v1/admin/modules');
    return response.data;
  },

  /** Install an Odoo module by technical name */
  installModule: async (moduleName) => {
    const response = await api.post('/api/v1/admin/modules/install', {
      module_name: moduleName,
    });
    return response.data;
  },
};

/* ============================================================
   GENERIC ODOO MODEL PROXY
   ============================================================ */

export const odooAPI = {
  /** Search and read records from any Odoo model */
  searchRead: async (model, domain = [], fields = [], limit = 80, offset = 0) => {
    const response = await api.post('/api/v1/odoo/search_read', {
      model,
      domain,
      fields,
      limit,
      offset,
    });
    return response.data;
  },

  /** Create a new record */
  create: async (model, values) => {
    const response = await api.post('/api/v1/odoo/create', {
      model,
      values,
    });
    return response.data;
  },
};

/* ============================================================
   REGISTRATION ENDPOINTS
   ============================================================ */

export const registrationAPI = {
  /** Course catalog (optionally only open-for-registration courses) */
  getCourses: async (params = {}) => {
    const response = await api.get('/api/v1/registration/courses', { params });
    return response.data;
  },

  /** Registration tiers / windows */
  getTiers: async () => {
    const response = await api.get('/api/v1/registration/tiers');
    return response.data;
  },

  /** The authenticated student's eligible registration window */
  getMyWindow: async () => {
    const response = await api.get('/api/v1/student/registration-window');
    return response.data;
  },
};

/* ============================================================
   STUDENT ENDPOINTS
   ============================================================ */

export const studentAPI = {
  /** Authenticated student's dashboard summary */
  getDashboard: async () => {
    const response = await api.get('/api/v1/student/dashboard');
    return response.data;
  },

  /** Authenticated student's grades + GPA grouped by term */
  getGrades: async () => {
    const response = await api.get('/api/v1/student/grades');
    return response.data;
  },
};

/* ============================================================
   FACULTY ENDPOINTS
   ============================================================ */

export const facultyAPI = {
  /** Faculty dashboard aggregates (courses + pending petitions) */
  getDashboard: async () => {
    const response = await api.get('/api/v1/faculty/dashboard');
    return response.data;
  },

  /** Role-filtered petition queue */
  getPetitionQueue: async (params = {}) => {
    const response = await api.get('/api/v1/faculty/petitions', { params });
    return response.data;
  },

  /** Enrolled students for a given course */
  getCourseRoster: async (courseId) => {
    const response = await api.get(`/api/v1/faculty/courses/${courseId}/roster`);
    return response.data;
  },
};

/* ============================================================
   REGISTRAR ENDPOINTS
   ============================================================ */

export const registrarAPI = {
  /** Live registrar dashboard aggregates */
  getDashboard: async () => {
    const response = await api.get('/api/v1/registrar/dashboard');
    return response.data;
  },

  /** Set a course's prerequisite course ids */
  setCoursePrerequisites: async (courseId, prerequisiteIds) => {
    const response = await api.patch(`/api/v1/registrar/courses/${courseId}/prerequisites`, {
      prerequisite_ids: prerequisiteIds,
    });
    return response.data;
  },

  /** Per-course enrollment monitor */
  getEnrollment: async () => {
    const response = await api.get('/api/v1/registrar/enrollment');
    return response.data;
  },

  /** Update a registration tier / window */
  updateTier: async (tierId, values) => {
    const response = await api.put(`/api/v1/registrar/registration-tiers/${tierId}`, values);
    return response.data;
  },
};

/* ============================================================
   ADVISING (Advisor / Chair) ENDPOINTS
   ============================================================ */

export const advisingAPI = {
  getAdvisees: async () => {
    const response = await api.get('/api/v1/faculty/advisees');
    return response.data;
  },
  getAdviseeProfile: async (userId) => {
    const response = await api.get(`/api/v1/faculty/advisees/${userId}`);
    return response.data;
  },
  getDepartmentStudents: async () => {
    const response = await api.get('/api/v1/faculty/department/students');
    return response.data;
  },
};

/* ============================================================
   SUPPORT (Tickets / Live Chat) ENDPOINTS
   ============================================================ */

export const supportAPI = {
  listTickets: async () => {
    const response = await api.get('/api/v1/support/tickets');
    return response.data;
  },
  createTicket: async (data) => {
    const response = await api.post('/api/v1/support/tickets', data);
    return response.data;
  },
  getTicket: async (id) => {
    const response = await api.get(`/api/v1/support/tickets/${id}`);
    return response.data;
  },
  postMessage: async (id, body) => {
    const response = await api.post(`/api/v1/support/tickets/${id}/messages`, { body });
    return response.data;
  },
  updateTicket: async (id, patch) => {
    const response = await api.patch(`/api/v1/support/tickets/${id}`, patch);
    return response.data;
  },
};

/* ============================================================
   AUDIT LOG ENDPOINTS
   ============================================================ */

export const auditAPI = {
  getLog: async (params = {}) => {
    const response = await api.get('/api/v1/admin/audit-log', { params });
    return response.data;
  },
};

/* ============================================================
   ADMIN ENDPOINTS
   ============================================================ */

export const adminAPI = {
  /** Dashboard KPIs */
  getStats: async () => {
    const response = await api.get('/api/v1/admin/stats');
    return response.data;
  },

  /** User growth + admission analytics */
  getAnalytics: async (period = 'monthly') => {
    const response = await api.get('/api/v1/admin/analytics', { params: { period } });
    return response.data;
  },

  /** Roles with user counts */
  getRolesSummary: async () => {
    const response = await api.get('/api/v1/admin/roles-summary');
    return response.data;
  },

  /** System / service health */
  getHealth: async () => {
    const response = await api.get('/api/v1/admin/health');
    return response.data;
  },

  /** AI services status */
  getAIServices: async () => {
    const response = await api.get('/api/v1/admin/ai/services');
    return response.data;
  },

  /** Feature flags */
  getFeatureFlags: async () => {
    const response = await api.get('/api/v1/admin/system/feature-flags');
    return response.data;
  },

  /** Toggle a feature flag */
  patchFeatureFlag: async (key, enabled) => {
    const response = await api.patch(`/api/v1/admin/system/feature-flags/${key}`, { enabled });
    return response.data;
  },

  /** Knowledge-base documents */
  getKBDocuments: async () => {
    const response = await api.get('/api/v1/admin/knowledge-base/documents');
    return response.data;
  },

  /** User directory */
  getUsers: async (params = {}) => {
    const response = await api.get('/api/v1/admin/users', { params });
    return response.data;
  },

  /** Single user */
  getUser: async (uid) => {
    const response = await api.get(`/api/v1/admin/users/${uid}`);
    return response.data;
  },

  /** Create a user */
  createUser: async (userData) => {
    const response = await api.post('/api/v1/admin/users', userData);
    return response.data;
  },

  /** Delete/deactivate a user */
  deleteUser: async (uid) => {
    const response = await api.delete(`/api/v1/admin/users/${uid}`);
    return response.data;
  },

  /** Read registration rules */
  getRules: async () => {
    const response = await api.get('/api/v1/admin/settings/registration-rules');
    return response.data;
  },

  /** Update registration rules */
  updateRules: async (rules) => {
    const response = await api.put('/api/v1/admin/settings/registration-rules', rules);
    return response.data;
  },

  /** Change admin password */
  changePassword: async (currentPassword, newPassword) => {
    const response = await api.post('/api/v1/admin/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
    return response.data;
  },

  /** Read / write global system settings */
  getSystemSettings: async () => {
    const response = await api.get('/api/v1/admin/system-settings');
    return response.data;
  },
  updateSystemSettings: async (settings) => {
    const response = await api.put('/api/v1/admin/system-settings', settings);
    return response.data;
  },

  /** Maintenance actions */
  clearCache: async () => {
    const response = await api.post('/api/v1/admin/maintenance/clear-cache');
    return response.data;
  },
  runTest: async (target) => {
    const response = await api.post(`/api/v1/admin/maintenance/test/${target}`);
    return response.data;
  },

  /* ---- Data retention policies ---- */
  getDataRetention: async () => {
    const response = await api.get('/api/v1/admin/data-retention');
    return response.data;
  },
  createDataRetention: async (policy) => {
    const response = await api.post('/api/v1/admin/data-retention', policy);
    return response.data;
  },
  updateDataRetention: async (id, policy) => {
    const response = await api.put(`/api/v1/admin/data-retention/${id}`, policy);
    return response.data;
  },
  deleteDataRetention: async (id) => {
    const response = await api.delete(`/api/v1/admin/data-retention/${id}`);
    return response.data;
  },
  runDataRetention: async () => {
    const response = await api.post('/api/v1/admin/data-retention/run');
    return response.data;
  },

  /* ---- Encrypted backups ---- */
  getBackups: async () => {
    const response = await api.get('/api/v1/admin/backups');
    return response.data;
  },
  createBackup: async () => {
    const response = await api.post('/api/v1/admin/backup');
    return response.data;
  },
  restoreBackup: async (filename, confirmToken) => {
    const response = await api.post('/api/v1/admin/restore', {
      filename,
      confirm_token: confirmToken,
    });
    return response.data;
  },

  /* ---- Service-account credential rotation ---- */
  getServiceAccounts: async () => {
    const response = await api.get('/api/v1/admin/service-accounts');
    return response.data;
  },
  createServiceAccount: async (data) => {
    const response = await api.post('/api/v1/admin/service-accounts', data);
    return response.data;
  },
  rotateServiceAccount: async (id) => {
    const response = await api.post(`/api/v1/admin/service-accounts/${id}/rotate`);
    return response.data;
  },
};

/* ============================================================
   ADMISSIONS ENDPOINTS
   ============================================================ */

export const admissionsAPI = {
  /** Admissions pipeline grouped by stage (Kanban) */
  getPipeline: async () => {
    const response = await api.get('/api/v1/admin/admissions/pipeline');
    return response.data;
  },

  /** Document submissions list for officer review */
  getDocuments: async () => {
    const response = await api.get('/api/v1/admin/admissions/documents');
    return response.data;
  },

  /** Move an application to a new stage */
  updateStage: async (id, stage) => {
    const response = await api.patch(`/api/v1/admin/admissions/${id}/stage`, { stage });
    return response.data;
  },

  /** Application review detail */
  getDetail: async (id) => {
    const response = await api.get(`/api/v1/admin/admissions/${id}`);
    return response.data;
  },

  /** Public status lookup by reference */
  getStatus: async (reference) => {
    const response = await api.get(`/api/v1/admissions/status/${reference}`);
    return response.data;
  },
};

/* ============================================================
   ADMISSION APPLICATION ENDPOINTS
   ============================================================ */

export const applicationAPI = {
  /** Extract fields from an uploaded document via OCR */
  uploadDocument: async (formData) => {
    const response = await api.post('/api/v1/extract-document', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  /** Full orchestrated submission: OCR + ERP record creation */
  submitApplication: async ({ file, email, phone, desired_program, application_type = 'regular' }) => {
    const form = new FormData();
    form.append('file', file);
    form.append('email', email);
    form.append('phone', phone);
    form.append('desired_program', desired_program);
    form.append('application_type', application_type);
    const response = await api.post('/api/v1/admissions/submit-with-document', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
};

/* ============================================================
   PETITIONS ENDPOINTS
   ============================================================ */

export const petitionsAPI = {
  /** All petitions (admin tracking board) */
  listPetitions: async (params = {}) => {
    const response = await api.get('/api/v1/admin/petitions', { params });
    return response.data;
  },

  /** Single petition detail (with decision trail) */
  getPetition: async (id) => {
    const response = await api.get(`/api/v1/admin/petitions/${id}`);
    return response.data;
  },

  /** Submit a new petition */
  submitPetition: async (data) => {
    const response = await api.post('/api/v1/petitions/new', data);
    return response.data;
  },

  /** Active petition types */
  getTypes: async () => {
    const response = await api.get('/api/v1/petitions/types');
    return response.data;
  },

  /** The caller's own petitions (student) */
  getMyPetitions: async () => {
    const response = await api.get('/api/v1/student/petitions');
    return response.data;
  },

  /** Faculty tier action (approve/reject/escalate) */
  facultyAction: async (id, action, reason) => {
    const response = await api.post(`/api/v1/faculty/petitions/${id}/action`, { action, reason });
    return response.data;
  },

  /** Chair override (approve/reject) */
  override: async (id, decision, reason) => {
    const response = await api.post(`/api/v1/faculty/petitions/${id}/override`, { decision, reason });
    return response.data;
  },
};

/* ============================================================
   CHATBOT (Academic Agent) ENDPOINTS
   ============================================================ */

export const chatbotAPI = {
  /**
   * Send a question to the Academic Agent via the gateway.
   * @param {string} question - the user's message
   * @param {Array<{role:string, content:string}>} history - prior turns
   * @returns {Promise<{answer:string, tool_used?:string, tool_ok?:boolean, queued?:boolean}>}
   */
  query: async (question, history = []) => {
    const response = await api.post('/api/v1/chatbot/query', { question, history });
    return response.data;
  },
};

export default api;
