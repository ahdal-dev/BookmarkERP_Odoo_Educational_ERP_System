import { useState } from 'react';
import { authAPI } from '../../api/apiGateway';
import styles from './MfaChallengeModal.module.css';

/**
 * Login MFA challenge. Collects a 6-digit TOTP code (or a backup code) and
 * exchanges the short-lived mfaToken for a full session via authAPI.mfaVerify.
 */
export default function MfaChallengeModal({ mfaToken, onSuccess, onCancel }) {
  const [code, setCode] = useState('');
  const [useBackup, setUseBackup] = useState(false);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    if (!code.trim()) return;
    setBusy(true);
    setError('');
    try {
      const data = await authAPI.mfaVerify(mfaToken, code.trim());
      onSuccess(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid code. Please try again.');
      setBusy(false);
    }
  };

  return (
    <div className={styles.overlay} role="dialog" aria-modal="true">
      <div className={styles.modal}>
        <h2 className={styles.title}>Two-factor verification</h2>
        <p className={styles.sub}>
          {useBackup
            ? 'Enter one of your saved backup codes.'
            : 'Enter the 6-digit code from your authenticator app.'}
        </p>

        {error && <div className={styles.error}>{error}</div>}

        <form onSubmit={submit}>
          <input
            className={styles.codeInput}
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder={useBackup ? 'XXXX-XXXX' : '000000'}
            inputMode={useBackup ? 'text' : 'numeric'}
            maxLength={useBackup ? 9 : 6}
            autoFocus
            autoComplete="one-time-code"
          />
          <button type="submit" className={styles.verifyBtn} disabled={busy || !code.trim()}>
            {busy ? 'Verifying…' : 'Verify'}
          </button>
        </form>

        <div className={styles.actions}>
          <button
            type="button"
            className={styles.linkBtn}
            onClick={() => { setUseBackup(!useBackup); setCode(''); setError(''); }}
          >
            {useBackup ? 'Use authenticator code' : 'Use a backup code'}
          </button>
          <button type="button" className={styles.linkBtn} onClick={onCancel}>
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
