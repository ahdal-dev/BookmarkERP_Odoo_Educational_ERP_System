import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Stepper from '../../components/Stepper/Stepper';
import FileDropzone from '../../components/FileDropzone/FileDropzone';
import StatusPill from '../../components/StatusPill/StatusPill';
import { SplatterDot } from '../../styles/brand';
import { applicationAPI } from '../../api/apiGateway';
import styles from './DocumentVerificationPage.module.css';
import logoUrl from '../../assets/logos/bookark_logo.svg';

/* ============================================================
   DOCUMENT VERIFICATION PAGE — Step 3 of admission wizard
   Light top nav, stepper, upload + OCR results, no sidebar.
   ============================================================ */

const STEPS = [
  { label: 'PERSONAL INFO', status: 'completed' },
  { label: 'ACADEMIC HISTORY', status: 'completed' },
  { label: 'DOCUMENT UPLOAD', status: 'active' },
  { label: 'REVIEW & SUBMIT', status: 'future' },
];

export default function DocumentVerificationPage() {
  const navigate = useNavigate();
  const [files, setFiles] = useState([]);
  const [ocrData, setOcrData] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [ocrError, setOcrError] = useState('');

  const handleFileSelect = async (newFiles) => {
    setFiles(newFiles);
    if (!newFiles?.length) return;
    setIsProcessing(true);
    setOcrError('');
    try {
      const form = new FormData();
      form.append('file', newFiles[0].file || newFiles[0]);
      const result = await applicationAPI.uploadDocument(form);
      // Normalize known fields with snake_case / camelCase fallbacks.
      setOcrData({
        fullName: result.full_name || result.fullName || result.name || '—',
        cumulativeGpa: result.gpa || result.cumulative_gpa || result.cumulativeGpa || '—',
        institution: result.institution || result.previous_school || '—',
        degreeProgram: result.degree || result.degree_program || result.degreeProgram || '—',
        raw: result,
      });
    } catch (err) {
      setOcrError(err?.response?.data?.detail || 'Could not extract document data. Please try another file.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className={styles.page}>
      {/* Top Nav */}
      <header className={styles.topNav}>
        <div className={styles.navLeft}>
          <div className={styles.logoWrap}>
            <img src={logoUrl} alt="Bookmark" className={styles.logoImg} />
          </div>
          <span className={styles.brandName}>Bookmark</span>
        </div>
        <nav className={styles.navLinks}>
          <a href="/dashboard" className={styles.navLink}>Dashboard</a>
          <a href="/profile" className={styles.navLink}>My Profile</a>
          <a href="/apply/documents" className={`${styles.navLink} ${styles.navLinkActive}`}>Documents</a>
          <a href="/support" className={styles.navLink}>Support</a>
        </nav>
        <div className={styles.navRight}>
          <div className={styles.avatar}>A</div>
        </div>
        <SplatterDot color="#e8613a" size={14} top="8px" right="120px" delay="0.3s" />
        <SplatterDot color="#f5c842" size={9} top="20px" right="100px" delay="0.5s" />
      </header>

      {/* Stepper */}
      <Stepper steps={STEPS} />

      {/* Main Content */}
      <div className={styles.content}>
        {/* Left Column: Upload & Preview */}
        <div className={styles.leftCol}>
          <span className={styles.sectionLabel}>Upload & Preview</span>
          <h2 className={styles.sectionTitle}>Document Verification</h2>
          <p className={styles.sectionSub}>Upload your official transcript for instant validation.</p>

          {files.length > 0 ? (
            <div className={styles.previewPanel}>
              <div className={styles.previewDoc}>
                <div className={styles.docPlaceholder}>
                  <span className={styles.docTitle}>Official Transcript</span>
                  {isProcessing && (
                    <div className={styles.ocrOverlay}>
                      <div className={styles.spinner} />
                      <span>Extracting data...</span>
                    </div>
                  )}
                </div>
              </div>
              <div className={styles.formatNote}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-lime)" strokeWidth="2" strokeLinecap="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4m0-4h.01"/></svg>
                <span>Supported formats: PDF, JPEG, PNG. Max file size 10MB.</span>
              </div>
            </div>
          ) : (
            <FileDropzone
              onFileSelect={handleFileSelect}
              acceptedFormats="PDF, JPEG, PNG"
              maxSize="10MB"
              files={files}
            />
          )}
        </div>

        {/* Right Column: Extracted Results */}
        <div className={styles.rightCol}>
          <span className={styles.sectionLabel}>Extracted Results</span>
          <div className={styles.extractedHeader}>
            <h2 className={styles.sectionTitle}>Extracted Information</h2>
            {ocrData && <StatusPill status="OCR Verified" variant="green" />}
          </div>

          {ocrError && <div style={{ background: '#fdecea', color: '#842029', border: '1px solid #f5c6cb', borderRadius: 10, padding: 12, marginBottom: 12, fontSize: '0.85rem' }}>{ocrError}</div>}

          {ocrData ? (
            <div className={styles.fieldGrid}>
              <div className={styles.fieldCard}>
                <span className={styles.fieldLabel}>FULL NAME:</span>
                <span className={styles.fieldValue}>{ocrData.fullName}</span>
              </div>
              <div className={styles.fieldCard}>
                <span className={styles.fieldLabel}>CUMULATIVE GPA:</span>
                <span className={styles.fieldValue}>{ocrData.cumulativeGpa}</span>
              </div>
              <div className={styles.fieldCard}>
                <span className={styles.fieldLabel}>CUMULATIVE GPA:</span>
                <div className={styles.fieldValueRow}>
                  <span className={styles.fieldValue}>{ocrData.cumulativeGpa}</span>
                  {ocrData.gpaDistinction && (
                    <StatusPill status={ocrData.gpaDistinction} variant="green" />
                  )}
                </div>
              </div>
              <div className={styles.fieldCard}>
                <span className={styles.fieldLabel}>INSTITUTION:</span>
                <span className={styles.fieldValue}>{ocrData.institution}</span>
              </div>
              <div className={styles.fieldCard}>
                <span className={styles.fieldLabel}>DEGREE PROGRAM:</span>
                <span className={styles.fieldValue}>{ocrData.degreeProgram}</span>
              </div>
            </div>
          ) : (
            <div className={styles.placeholder}>
              Upload a document to extract information.
            </div>
          )}

          <button className={styles.proceedBtn} disabled={!ocrData} onClick={() => navigate('/admissions/status')}>
            Confirm & Proceed →
          </button>
          <a href="/admissions" className={styles.backLink}>← Back to Admissions</a>
        </div>
      </div>

      {/* Need Assistance Card */}
      <div className={styles.assistCard}>
        <div>
          <h3 className={styles.assistTitle}>Need Assistance?</h3>
          <p className={styles.assistText}>
            Need assistance to help with your documents and application process?
            Our admissions advisors will help you.
          </p>
          <a href="/support" className={styles.assistLink}>TALK TO AN ADVISOR</a>
        </div>
        <SplatterDot color="#f5c842" size={40} top="10px" right="20px" delay="0.3s" />
      </div>
    </div>
  );
}
