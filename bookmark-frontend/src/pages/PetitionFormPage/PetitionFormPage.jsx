import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AppShell from '../../components/AppShell/AppShell';
import FileDropzone from '../../components/FileDropzone/FileDropzone';
import StatusPill from '../../components/StatusPill/StatusPill';
import { SplatterDot } from '../../styles/brand';
import { petitionsStudentNav } from '../../config/navConfigs';
import { petitionsAPI } from '../../api/apiGateway';
import useAsync from '../../hooks/useAsync';
import styles from './PetitionFormPage.module.css';

/* ============================================================
   STUDENT PETITION FORM — New petition submission (live)
   ============================================================ */

const STATE_LABEL = { submitted: 'Pending', under_review: 'Pending', approved: 'Approved', rejected: 'Denied' };

export default function PetitionFormPage() {
  const navigate = useNavigate();
  const { data: typesData } = useAsync(() => petitionsAPI.getTypes(), []);
  const { data: mine, reload: reloadMine } = useAsync(() => petitionsAPI.getMyPetitions(), []);
  const types = typesData?.types || [];
  const recent = (mine?.petitions || []).slice(0, 5);

  const [petitionType, setPetitionType] = useState('');
  const [subject, setSubject] = useState('');
  const [justification, setJustification] = useState('');
  const [files, setFiles] = useState([]);
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (justification.trim().length < 10) { setError('Please provide a more detailed justification (min 10 characters).'); return; }
    setSubmitting(true);
    try {
      await petitionsAPI.submitPetition({
        petition_type_id: Number(petitionType),
        subject: subject.trim() || (types.find((t) => t.id === Number(petitionType))?.name || 'Petition'),
        description: justification.trim(),
      });
      setDone(true);
      setSubject(''); setJustification(''); setFiles([]); setPetitionType('');
      reloadMine();
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || 'Could not submit petition.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AppShell navItems={petitionsStudentNav} logoVariant="stacked">
      <div className={styles.layout}>
        <div className={styles.main}>
          <div className={styles.breadcrumb}>ACADEMIC / PETITIONS / NEW SUBMISSION</div>

          <div className={styles.formCard}>
            <h2 className={styles.formTitle}>Student Petition Form</h2>
            <p className={styles.formSub}>Petitions are reviewed by the Instructor → Advisor → Chair tiers.</p>

            {done && <div style={{ background: '#eaf7e6', color: '#2e6b16', border: '1px solid #bfe6b0', borderRadius: 12, padding: 14, marginBottom: 16, fontWeight: 600 }}>
              ✓ Petition submitted. <span style={{ textDecoration: 'underline', cursor: 'pointer' }} onClick={() => navigate('/student/petitions')}>Track it here →</span>
            </div>}
            {error && <div style={{ background: '#fdecea', color: '#842029', border: '1px solid #f5c6cb', borderRadius: 12, padding: 14, marginBottom: 16, fontWeight: 600 }}>{error}</div>}

            <form onSubmit={handleSubmit} className={styles.form}>
              <div className={styles.formColumns}>
                <div className={styles.formLeft}>
                  <div className={styles.field}>
                    <label className={styles.fieldLabel}>PETITION TYPE</label>
                    <select className={styles.select} value={petitionType} onChange={(e) => setPetitionType(e.target.value)} required>
                      <option value="">Select a type...</option>
                      {types.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
                    </select>
                  </div>
                  <div className={styles.field}>
                    <label className={styles.fieldLabel}>SUBJECT</label>
                    <input className={styles.select} value={subject} onChange={(e) => setSubject(e.target.value)} placeholder="Short summary of your request" />
                  </div>
                  <div className={styles.field}>
                    <label className={styles.fieldLabel}>DETAILED JUSTIFICATION</label>
                    <textarea className={styles.textarea} value={justification} onChange={(e) => setJustification(e.target.value)} placeholder="Provide a detailed explanation and justification..." rows={8} required />
                  </div>
                </div>

                <div className={styles.formRight}>
                  <label className={styles.fieldLabel}>SUPPORTING DOCUMENTS</label>
                  <FileDropzone onFileSelect={setFiles} acceptedFormats="PDF, JPEG, PNG" maxSize="10MB" files={files} />
                  <SplatterDot color="#e8613a" size={10} top="5px" right="-5px" delay="0.3s" />
                </div>
              </div>

              <div className={styles.submitSection}>
                <button type="submit" className={styles.submitBtn} disabled={submitting || !petitionType}>
                  {submitting ? 'Submitting…' : 'Submit for Review →'}
                </button>
              </div>
            </form>
          </div>

          <div className={styles.guidanceCard}>
            <div>
              <h3 className={styles.guidanceLabel}>Need guidance?</h3>
              <h2 className={styles.guidanceTitle}>Confused about the process?</h2>
              <p className={styles.guidanceText}>Learn about the petition process, requirements, and expected timelines.</p>
              <a href="/handbook" className={styles.guidanceLink}>Open Handbook →</a>
            </div>
            <SplatterDot color="#e8613a" size={30} top="10px" right="20px" delay="0.3s" />
          </div>
        </div>

        <aside className={styles.aside}>
          <div className={styles.recentCard}>
            <h3 className={styles.recentTitle}>Recent Petitions</h3>
            {recent.length === 0 ? <p style={{ fontSize: '0.82rem', color: 'var(--color-text-muted)' }}>No petitions yet.</p> : recent.map((p) => (
              <div key={p.id} className={styles.recentItem}>
                <StatusPill status={STATE_LABEL[p.state] || p.state} />
                <div className={styles.recentText}>
                  <span className={styles.recentName}>{p.subject || p.ref}</span>
                  <span className={styles.recentDate}>{p.date}</span>
                </div>
              </div>
            ))}
          </div>
        </aside>
      </div>
    </AppShell>
  );
}
