import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import BookmarkLogo from '../../components/BookmarkLogo/BookmarkLogo';
import { SplatterDot } from '../../styles/brand';
import { useAuth } from '../../context/AuthContext';
import { authAPI } from '../../api/apiGateway';
import w from '../_shared/workflow.module.css';

/* Change Password — reachable from the Login page ("Change Password" link)
   and from Settings → Account & Security. Self-contained branded card. */

export default function ChangePasswordPage() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const [current, setCurrent] = useState('');
  const [next, setNext] = useState('');
  const [confirm, setConfirm] = useState('');
  const [done, setDone] = useState(false);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (next.length < 8) { setError('New password must be at least 8 characters.'); return; }
    if (next !== confirm) { setError('New password and confirmation do not match.'); return; }

    // Changing a password requires an authenticated session.
    if (!isAuthenticated) {
      setError('Please log in first to change your password.');
      return;
    }

    setSubmitting(true);
    try {
      await authAPI.changePassword(current, next);
      setDone(true);
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || 'Could not change password. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-bg-warm)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24, position: 'relative', overflow: 'hidden' }}>
      <SplatterDot color="#e8613a" size={36} bottom="12%" left="10%" delay="0.8s" $animate />
      <SplatterDot color="#f5c842" size={12} top="14%" right="14%" delay="0.5s" />

      <div className={w.card} style={{ width: '100%', maxWidth: 440 }}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10, marginBottom: 20 }}>
          <BookmarkLogo size="small" />
          <h2 style={{ fontFamily: 'var(--font-brand)', fontSize: '1.5rem' }}>Change Password</h2>
          <p className={w.cardSub} style={{ textAlign: 'center', marginBottom: 0 }}>
            Choose a strong password you don't use elsewhere.
          </p>
        </div>

        {done ? (
          <div style={{ textAlign: 'center' }}>
            <div className={`${w.alert} ${w.alertGreen}`}>✓ Your password has been updated.</div>
            <button
              className={`${w.btn} ${w.btnPrimary} ${w.btnFull}`}
              onClick={() => navigate(isAuthenticated ? '/settings' : '/login')}
            >
              {isAuthenticated ? 'Back to Settings' : 'Back to Login'}
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            {error && <div className={`${w.alert} ${w.alertCoral}`}>{error}</div>}
            <div className={w.field}>
              <span className={w.fieldLabel}>Current Password</span>
              <input className={w.input} type="password" value={current} onChange={(e) => setCurrent(e.target.value)} autoComplete="current-password" required />
            </div>
            <div className={w.field}>
              <span className={w.fieldLabel}>New Password</span>
              <input className={w.input} type="password" value={next} onChange={(e) => setNext(e.target.value)} autoComplete="new-password" required />
            </div>
            <div className={w.field}>
              <span className={w.fieldLabel}>Confirm New Password</span>
              <input className={w.input} type="password" value={confirm} onChange={(e) => setConfirm(e.target.value)} autoComplete="new-password" required />
            </div>
            <div style={{ display: 'flex', gap: 10, marginTop: 8 }}>
              <button type="button" className={`${w.btn} ${w.btnOutline} ${w.btnFull}`} onClick={() => navigate(isAuthenticated ? '/settings' : '/login')}>Cancel</button>
              <button type="submit" className={`${w.btn} ${w.btnPrimary} ${w.btnFull}`} disabled={submitting}>
                {submitting ? 'Updating…' : 'Update Password'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
