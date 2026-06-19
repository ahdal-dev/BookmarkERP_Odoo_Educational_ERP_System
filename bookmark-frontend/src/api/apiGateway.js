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

      // Don't redirect if already on login page
      if (window.location.pathname !== '/login') {
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

  /** Change the authenticated user's password */
  changePassword: async (currentPassword, newPassword) => {
    const response = await api.post('/api/v1/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
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

  /** Move an application to a new stage */
  updateStage: async (id, stage) => {
    const response = await api.patch(`/api/v1/admin/admissions/${id}/stage`, { stage });
    return response.data;
  },
};

/* ============================================================
   ADMISSION APPLICATION ENDPOINTS
   ============================================================ */

export const applicationAPI = {
  // TODO(backend): implement POST /api/v1/admission/documents (multipart)
  uploadDocument: async (formData) => {
    const response = await api.post('/api/v1/admission/documents', formData, {
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

  // TODO(backend): implement POST /api/v1/petitions
  submitPetition: async (data) => {
    const response = await api.post('/api/v1/petitions', data);
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
