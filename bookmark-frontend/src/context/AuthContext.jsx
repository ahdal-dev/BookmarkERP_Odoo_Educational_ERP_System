import { createContext, useContext, useReducer, useEffect, useCallback } from 'react';
import { authAPI } from '../api/apiGateway';

/* ============================================================
   AUTH CONTEXT — State management for authentication
   ============================================================ */

const AuthContext = createContext(null);

// --- State Shape ---
const initialState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
};

// --- Reducer ---
function authReducer(state, action) {
  switch (action.type) {
    case 'AUTH_START':
      return { ...state, isLoading: true, error: null };
    case 'AUTH_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      };
    case 'AUTH_FAILURE':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload,
      };
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      };
    case 'CLEAR_ERROR':
      return { ...state, error: null };
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    default:
      return state;
  }
}

// --- Provider ---
export function AuthProvider({ children }) {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Check for existing session on mount
  useEffect(() => {
    const token = localStorage.getItem('bookmark_token');
    const userStr = localStorage.getItem('bookmark_user');

    if (token && userStr) {
      try {
        const user = JSON.parse(userStr);
        dispatch({
          type: 'AUTH_SUCCESS',
          payload: { user, token },
        });
      } catch {
        localStorage.removeItem('bookmark_token');
        localStorage.removeItem('bookmark_user');
        dispatch({ type: 'SET_LOADING', payload: false });
      }
    } else {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  }, []);

  // Finalize a session from a full token response (used by normal login and by
  // the MFA challenge once it returns access_token).
  const completeLogin = useCallback((data, loginId) => {
    const user = {
      id: data.user_id,
      name: data.user_name || loginId,
      email: data.email || loginId,
      role: data.role || 'student',
      roles: data.roles || {},
    };
    localStorage.setItem('bookmark_token', data.access_token);
    localStorage.setItem('bookmark_user', JSON.stringify(user));
    dispatch({ type: 'AUTH_SUCCESS', payload: { user, token: data.access_token } });
    return { success: true, user };
  }, []);

  // --- Login ---
  const login = useCallback(async (loginId, password) => {
    dispatch({ type: 'AUTH_START' });
    try {
      const data = await authAPI.login(loginId, password);

      // Strong-auth interstitials — do NOT store a token; let the page branch.
      if (data.mfa_required) {
        dispatch({ type: 'SET_LOADING', payload: false });
        return { mfaRequired: true, mfaToken: data.mfa_token };
      }
      if (data.mfa_setup_required) {
        dispatch({ type: 'SET_LOADING', payload: false });
        return { mfaSetupRequired: true, mfaToken: data.mfa_token, role: data.role };
      }
      if (data.password_expired) {
        dispatch({ type: 'SET_LOADING', payload: false });
        return { passwordExpired: true, resetToken: data.reset_token };
      }

      if (data.access_token) {
        return completeLogin(data, loginId);
      }

      throw new Error(data.message || 'Authentication failed');
    } catch (error) {
      const message =
        error.response?.data?.detail ||
        error.message ||
        'Invalid credentials. Please try again.';
      dispatch({ type: 'AUTH_FAILURE', payload: message });
      return { success: false, error: message };
    }
  }, [completeLogin]);

  // --- Complete an MFA challenge (modal calls authAPI.mfaVerify, passes result here) ---
  const completeMfaLogin = useCallback((data) => {
    if (!data?.access_token) {
      return { success: false, error: 'MFA verification failed' };
    }
    return completeLogin(data, data.user_name);
  }, [completeLogin]);

  // --- Logout ---
  const logout = useCallback(async () => {
    try {
      await authAPI.logout();
    } catch {
      // Logout even if API call fails
    }
    localStorage.removeItem('bookmark_token');
    localStorage.removeItem('bookmark_user');
    dispatch({ type: 'LOGOUT' });
  }, []);

  // --- Clear Error ---
  const clearError = useCallback(() => {
    dispatch({ type: 'CLEAR_ERROR' });
  }, []);

  const value = {
    ...state,
    login,
    completeMfaLogin,
    logout,
    clearError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// --- Hook ---
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default AuthContext;
