import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { authAPI } from '../../api/apiGateway';
import styles from './MFASecurityPage.module.css';

/**
 * MFA setup + management. Two entry modes:
 *  - account:  authenticated user manages MFA from settings.
 *  - enforced: redirected here from login with a one-time setup token because
 *              their privileged role requires MFA before first session.
 */
export default function MFASecurityPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const setupToken = location.state?.token;
  const enforced = Boolean(location.state?.setup);

  const [status, setStatus] = useState(null);
  const [step, setStep] = useState('idle'); // idle | enrolling | codes
  const [enrol, setEnrol] = useState(null); // { otpauth_uri, qr_png_base64, secret }
  const [code, setCode] = useState('');
  const [codes, setCodes] = useState([]);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  // Guard: account-mode requires a session.
  useEffect(() => {
    if (!enforced && !isAuthenticated) {
      navigate('/login', { replace: true });
    }
  }, [enforced, isAuthenticated, navigate]);

  // Load current status in account mode.
  useEffect(() => {
    if (enforced) return;
    authAPI.mfaStatus().then(setStatus).catch(() => setStatus(null));
  }, [enforced]);

  const beginSetup = async () => {
    setBusy(true); setError('');
    try {
      const data = await authAPI.mfaSetup(setupToken);
      setEnrol(data);
      setStep('enrolling');
    } catch (e) {
      setError(e.response?.data?.detail || 'Could not start MFA setup');
    } finally {
      setBusy(false);
    }
  };

  const confirmSetup = async () => {
    if (!code.trim()) return;
    setBusy(true); setError('');
    try {
      const data = await authAPI.mfaVerifySetup(code.trim(), setupToken);
      setCodes(data.backup_codes || []);
      setStep('codes');
    } catch (e) {
      setError(e.response?.data?.detail || 'Invalid code');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <div className={styles.topBorder} />
        <div className={styles.body}>
          <h1 className={styles.title}>Multi-Factor Authentication</h1>
          <p className={styles.sub}>
            {enforced
              ? 'Your role requires MFA. Set it up to continue.'
              : 'Add a one-time code from your authenticator app for extra security.'}
          </p>

          {error && <div className={styles.error}>{error}</div>}

          {/* ---- account mode: status + disable ---- */}
          {!enforced && step === 'idle' && (
            <>
              <div className={styles.statusRow}>
                <span>Status</span>
                <span className={status?.mfa_enabled ? styles.on : styles.off}>
                  {status?.mfa_enabled ? 'Enabled' : 'Disabled'}
                </span>
              </div>
              {status?.mfa_enabled
                ? <DisableForm onDone={() => authAPI.mfaStatus().then(setStatus)} />
                : <button className={styles.primaryBtn} onClick={beginSetup} disabled={busy}>
                    {busy ? 'Please wait…' : 'Enable MFA'}
                  </button>}
              <button className={styles.linkBtn} onClick={() => navigate('/settings')}>← Back to settings</button>
            </>
          )}

          {/* ---- enforced mode landing ---- */}
          {enforced && step === 'idle' && (
            <button className={styles.primaryBtn} onClick={beginSetup} disabled={busy}>
              {busy ? 'Please wait…' : 'Start MFA setup'}
            </button>
          )}

          {/* ---- enrolling: QR + verify ---- */}
          {step === 'enrolling' && enrol && (
            <>
              <img className={styles.qr} src={`data:image/png;base64,${enrol.qr_png_base64}`} alt="MFA QR code" />
              <p className={styles.secretHint}>
                Or enter this secret manually: <code className={styles.code}>{enrol.secret}</code>
              </p>
              <input
                className={styles.codeInput}
                value={code}
                onChange={(e) => setCode(e.target.value)}
                placeholder="000000"
                inputMode="numeric"
                maxLength={6}
                autoFocus
              />
              <button className={styles.primaryBtn} onClick={confirmSetup} disabled={busy || !code.trim()}>
                {busy ? 'Verifying…' : 'Verify & enable'}
              </button>
            </>
          )}

          {/* ---- backup codes ---- */}
          {step === 'codes' && (
            <>
              <p className={styles.sub}>Save these one-time backup codes somewhere safe:</p>
              <div className={styles.codesGrid}>
                {codes.map((c) => <span key={c} className={styles.backupCode}>{c}</span>)}
              </div>
              {enforced
                ? <button className={styles.primaryBtn} onClick={() => navigate('/login', { replace: true })}>
                    Continue to login
                  </button>
                : <button className={styles.primaryBtn} onClick={() => { setStep('idle'); authAPI.mfaStatus().then(setStatus); }}>
                    Done
                  </button>}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function DisableForm({ onDone }) {
  const [pw, setPw] = useState('');
  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const disable = async () => {
    setBusy(true); setError('');
    try {
      await authAPI.mfaDisable(pw, code.trim());
      onDone();
    } catch (e) {
      setError(e.response?.data?.detail || 'Could not disable MFA');
      setBusy(false);
    }
  };

  return (
    <div className={styles.disableBox}>
      {error && <div className={styles.error}>{error}</div>}
      <input className={styles.input} type="password" placeholder="Current password"
             value={pw} onChange={(e) => setPw(e.target.value)} />
      <input className={styles.input} placeholder="Authenticator code"
             value={code} onChange={(e) => setCode(e.target.value)} />
      <button className={styles.dangerBtn} onClick={disable} disabled={busy || !pw || !code}>
        {busy ? 'Disabling…' : 'Disable MFA'}
      </button>
    </div>
  );
}
