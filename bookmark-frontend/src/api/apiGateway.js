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

export default api;
