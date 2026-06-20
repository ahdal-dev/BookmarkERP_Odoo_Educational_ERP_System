import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import Stepper from '../../components/Stepper/Stepper';
import { useApplication } from '../../context/ApplicationContext';
import { applicationAPI } from '../../api/apiGateway';
import styles from './apply.module.css';
import reviewStyles from './ApplyReviewPage.module.css';
import logoUrl from '../../assets/logos/bookark_logo.svg';

const STEPS = [
  { label: 'PERSONAL INFO', status: 'completed' },
  { label: 'ACADEMIC HISTORY', status: 'completed' },
  { label: 'DOCUMENT UPLOAD', status: 'completed' },
  { label: 'REVIEW & SUBMIT', status: 'active' },
];

function Row({ label, value }) {
  return (
    <div className={reviewStyles.row}>
      <span className={reviewStyles.rowLabel}>{label}</span>
      <span className={reviewStyles.rowValue}>{value || '—'}</span>
    </div>
  );
}

export default function ApplyReviewPage() {
  const navigate = useNavigate();
  const { state, reset } = useApplication();
  const { personalInfo: pi, academicHistory: ah, ocrData, documentFile, documentFilename } = state;

  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [referenceNumber, setReferenceNumber] = useState('');

  const canSubmit = documentFile && pi.email && pi.phone && ah.degree_program;

  const handleSubmit = async () => {
    if (!canSubmit) return;
    setSubmitting(true);
    setSubmitError('');
    try {
      const result = await applicationAPI.submitApplication({
        file: documentFile,
        email: pi.email,
        phone: pi.phone,
        desired_program: ah.degree_program,
        application_type: ah.application_type || 'regular',
      });
      const ref =
        result?.admission_result?.application_id
          ? `ADM-${result.admission_result.application_id}`
          : result?.reference || 'ADM-SUBMITTED';
      setReferenceNumber(ref);
      setSubmitted(true);
      reset();
    } catch (err) {
      const detail = err?.response?.data?.detail;
      if (err?.response?.status === 401 || err?.response?.status === 403) {
        setSubmitError('You need to be signed in to submit. Please log in and return to this page.');
      } else {
        setSubmitError(detail || 'Submission failed. Please check your connection and try again.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div className={styles.page}>
        <header className={styles.topNav}>
          <div className={styles.navLeft}>
            <div className={styles.logoWrap}>
              <img src={logoUrl} alt="Bookmark" className={styles.logoImg} />
            </div>
            <span className={styles.brandName}>Bookmark</span>
          </div>
        </header>
        <div className={styles.content}>
          <div className={reviewStyles.successCard}>
            <div className={reviewStyles.successIcon}>✓</div>
            <h2 className={reviewStyles.successTitle}>Application Submitted!</h2>
            <p className={reviewStyles.successSub}>
              Your application has been received. Use the reference below to track your status.
            </p>
            <div className={reviewStyles.refBox}>{referenceNumber}</div>
            <div className={reviewStyles.successActions}>
              <button className={styles.btnPrimary} onClick={() => navigate('/admissions/status')}>
                Track My Application →
              </button>
              <Link to="/admissions" className={styles.btnBack}>← Back to Programs</Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <header className={styles.topNav}>
        <div className={styles.navLeft}>
          <div className={styles.logoWrap}>
            <img src={logoUrl} alt="Bookmark" className={styles.logoImg} />
          </div>
          <span className={styles.brandName}>Bookmark</span>
        </div>
        <nav className={styles.navLinks}>
          <Link to="/admissions" className={styles.navLink}>Programs</Link>
          <Link to="/login" className={styles.navLink}>Sign In</Link>
        </nav>
      </header>

      <Stepper steps={STEPS} />

      <div className={styles.content}>
        <h2 className={styles.stepTitle}>Review & Submit</h2>
        <p className={styles.stepSub}>Check your information before submitting. You cannot edit after submission.</p>

        {submitError && (
          <div className={reviewStyles.errorBanner}>{submitError}</div>
        )}

        <div className={styles.formCard}>
          <h3 className={reviewStyles.sectionHead}>Personal Information</h3>
          <Row label="Full Name" value={pi.name} />
          <Row label="Email" value={pi.email} />
          <Row label="Phone" value={pi.phone} />
          <Row label="National ID" value={pi.national_id} />
          <Row label="Date of Birth" value={pi.date_of_birth} />
          <Row label="Nationality" value={pi.nationality} />

          <h3 className={reviewStyles.sectionHead} style={{ marginTop: 24 }}>Academic History</h3>
          <Row label="Previous School" value={ah.previous_school} />
          <Row label="Desired Program" value={ah.degree_program} />
          <Row label="Graduation Year" value={ah.graduation_year} />
          <Row label="GPA" value={ah.gpa} />
          <Row label="Application Type" value={ah.application_type} />

          <h3 className={reviewStyles.sectionHead} style={{ marginTop: 24 }}>Document</h3>
          {documentFilename ? (
            <div className={reviewStyles.docRow}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#16a34a" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
              <span>{documentFilename}</span>
            </div>
          ) : (
            <div className={reviewStyles.missingDoc}>
              No document uploaded.{' '}
              <Link to="/apply/documents" style={{ color: '#4caf27', fontWeight: 700 }}>Upload now</Link>
            </div>
          )}

          {ocrData && (
            <>
              <h3 className={reviewStyles.sectionHead} style={{ marginTop: 24 }}>OCR-Extracted Data</h3>
              <Row label="Extracted Name" value={ocrData.fullName} />
              <Row label="Extracted GPA" value={ocrData.cumulativeGpa} />
              <Row label="Institution" value={ocrData.institution} />
              <Row label="Degree" value={ocrData.degreeProgram} />
            </>
          )}

          {!canSubmit && (
            <div className={reviewStyles.warningBanner}>
              Please complete all steps before submitting: personal info, academic history, and document upload are required.
            </div>
          )}

          <div className={styles.actions}>
            <button className={styles.btnBack} onClick={() => navigate('/apply/documents')}>
              ← Back
            </button>
            <button
              className={styles.btnPrimary}
              onClick={handleSubmit}
              disabled={submitting || !canSubmit}
            >
              {submitting ? 'Submitting…' : 'Submit Application →'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
