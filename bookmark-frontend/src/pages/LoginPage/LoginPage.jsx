import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import BookmarkLogo from '../../components/BookmarkLogo/BookmarkLogo';
import { SplatterDot } from '../../styles/brand';
import styles from './LoginPage.module.css';

export default function LoginPage() {
  const [loginId, setLoginId] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { login, error, clearError } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!loginId.trim() || !password.trim()) return;

    setIsSubmitting(true);
    const result = await login(loginId.trim(), password);
    setIsSubmitting(false);

    if (result.success) {
      navigate('/dashboard', { replace: true });
    }
  };

  return (
    <div className={styles.container}>
      {/* ===== LEFT PANEL — Dark Brand ===== */}
      <div className={styles.leftPanel}>
        <div className={styles.leftContent}>
          {/* Logo */}
          <BookmarkLogo size="large" />

          {/* Wordmark */}
          <div className={styles.wordmark}>
            <h1 className={styles.brandName}>Bookmark</h1>
            <p className={styles.brandSub}>ACADEMIC ERP SUITE</p>
          </div>
        </div>

        {/* Decorative splatters on left panel */}
        <SplatterDot color="#e8613a" size={40} bottom="15%" left="8%" delay="0.8s" $animate />
        <SplatterDot color="#e8613a" size={18} bottom="12%" left="14%" delay="1s" />
        <SplatterDot color="#f5c842" size={12} bottom="20%" left="5%" delay="0.9s" />
        <SplatterDot color="#f5c842" size={8} top="12%" right="15%" delay="0.6s" $animate />
      </div>

      {/* ===== RIGHT PANEL — Login Form ===== */}
      <div className={styles.rightPanel}>
        {/* Floating splatters on right panel */}
        <SplatterDot color="#f5c842" size={14} top="8%" right="12%" delay="0.4s" $animate />
        <SplatterDot color="#e8613a" size={8} top="15%" right="8%" delay="0.6s" />
        <SplatterDot color="#f5c842" size={10} bottom="15%" left="10%" delay="0.7s" $animate />

        <div className={styles.formWrapper}>
          {/* Login Card */}
          <div className={styles.loginCard}>
            {/* Lime green top border */}
            <div className={styles.cardTopBorder} />

            <div className={styles.cardContent}>
              {/* Header */}
              <div className={styles.cardHeader}>
                <h2 className={styles.welcomeTitle}>Welcome back</h2>
                <p className={styles.welcomeSub}>
                  Please enter your credentials to access the portal.
                </p>
              </div>

              {/* Error Message */}
              {error && (
                <div className={styles.errorBanner}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
                    <path d="M12 8v4M12 16h.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                  </svg>
                  <span>{error}</span>
                  <button onClick={clearError} className={styles.errorClose} aria-label="Dismiss error">×</button>
                </div>
              )}

              {/* Form */}
              <form onSubmit={handleSubmit} className={styles.form}>
                {/* Email / Student ID */}
                <div className={styles.fieldGroup}>
                  <label htmlFor="login-id" className={styles.fieldLabel}>
                    EMAIL/STUDENT ID
                  </label>
                  <div className={styles.inputWrap}>
                    <span className={styles.inputPrefix}>@</span>
                    <input
                      id="login-id"
                      type="text"
                      value={loginId}
                      onChange={(e) => { setLoginId(e.target.value); clearError(); }}
                      placeholder="e.g. STU-2024-001"
                      className={styles.input}
                      autoComplete="username"
                      autoFocus
                      required
                    />
                  </div>
                </div>

                {/* Password */}
                <div className={styles.fieldGroup}>
                  <div className={styles.fieldLabelRow}>
                    <label htmlFor="login-password" className={styles.fieldLabel}>
                      PASSWORD
                    </label>
                    <a href="#" className={styles.forgotLink}>Forgot Password?</a>
                  </div>
                  <div className={styles.inputWrap}>
                    <span className={styles.inputPrefix}>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                        <rect x="3" y="11" width="18" height="11" rx="2" stroke="currentColor" strokeWidth="2" />
                        <path d="M7 11V7a5 5 0 0110 0v4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                      </svg>
                    </span>
                    <input
                      id="login-password"
                      type={showPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => { setPassword(e.target.value); clearError(); }}
                      placeholder="••••••••••"
                      className={styles.input}
                      autoComplete="current-password"
                      required
                    />
                    <button
                      type="button"
                      className={styles.togglePassword}
                      onClick={() => setShowPassword(!showPassword)}
                      aria-label={showPassword ? 'Hide password' : 'Show password'}
                    >
                      {showPassword ? (
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                          <path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                          <line x1="1" y1="1" x2="23" y2="23" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                        </svg>
                      ) : (
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                          <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="2"/>
                        </svg>
                      )}
                    </button>
                  </div>
                </div>

                {/* Submit Button */}
                <button
                  type="submit"
                  className={styles.submitBtn}
                  disabled={isSubmitting || !loginId.trim() || !password.trim()}
                >
                  {isSubmitting ? (
                    <span className={styles.btnSpinner} />
                  ) : (
                    <>Log in <span className={styles.btnArrow}>→</span></>
                  )}
                </button>
              </form>

              {/* Footer */}
              <div className={styles.cardFooter}>
                <p className={styles.applyText}>
                  Not yet a student?{' '}
                  <Link to="/admissions" className={styles.applyLink}>Apply Now</Link>
                </p>

                <div className={styles.secureBadge}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
                    <polyline points="9,12 11,14 15,10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                  <span>SECURE AES-256 ENCRYPTED PORTAL</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
