import { useState } from 'react';
import AppShell from '../../components/AppShell/AppShell';
import FileDropzone from '../../components/FileDropzone/FileDropzone';
import StatusPill from '../../components/StatusPill/StatusPill';
import { SplatterDot } from '../../styles/brand';
import { petitionsStudentNav } from '../../config/navConfigs';
import { mockPetitionTypes, mockStatusHistory, mockRecentPetitions } from '../../mocks/petitionsMocks';
import styles from './PetitionFormPage.module.css';

/* ============================================================
   STUDENT PETITION FORM — New petition submission
   ============================================================ */

export default function PetitionFormPage() {
  const [petitionType, setPetitionType] = useState('');
  const [justification, setJustification] = useState('');
  const [files, setFiles] = useState([]);

  const handleSubmit = (e) => {
    e.preventDefault();
    // TODO(backend): implement POST /api/v1/petitions
    console.log('Submit petition:', { petitionType, justification, files });
  };

  return (
    <AppShell navItems={petitionsStudentNav} logoVariant="stacked">
      <div className={styles.layout}>
        {/* Main Content */}
        <div className={styles.main}>
          {/* Breadcrumb */}
          <div className={styles.breadcrumb}>ACADEMIC / PETITIONS / NEW SUBMISSION</div>

          {/* Form Card */}
          <div className={styles.formCard}>
            <h2 className={styles.formTitle}>Student Petition Form</h2>
            <p className={styles.formSub}>
              Petitions are reviewed within 5 business days by the academic dean's office.
            </p>

            <form onSubmit={handleSubmit} className={styles.form}>
              <div className={styles.formColumns}>
                {/* Left: Type + Justification */}
                <div className={styles.formLeft}>
                  <div className={styles.field}>
                    <label className={styles.fieldLabel}>PETITION TYPE</label>
                    <select
                      className={styles.select}
                      value={petitionType}
                      onChange={(e) => setPetitionType(e.target.value)}
                      required
                    >
                      <option value="">Select a type...</option>
                      {mockPetitionTypes.map((t) => <option key={t} value={t}>{t}</option>)}
                    </select>
                  </div>

                  <div className={styles.field}>
                    <label className={styles.fieldLabel}>DETAILED JUSTIFICATION</label>
                    <textarea
                      className={styles.textarea}
                      value={justification}
                      onChange={(e) => setJustification(e.target.value)}
                      placeholder="Please provide a detailed explanation and justification for your petition..."
                      rows={8}
                      required
                    />
                  </div>
                </div>

                {/* Right: File Upload */}
                <div className={styles.formRight}>
                  <label className={styles.fieldLabel}>SUPPORTING DOCUMENTS</label>
                  <FileDropzone
                    onFileSelect={setFiles}
                    acceptedFormats="PDF, JPEG, PNG"
                    maxSize="10MB"
                    files={files}
                  />
                  <SplatterDot color="#e8613a" size={10} top="5px" right="-5px" delay="0.3s" />
                  <SplatterDot color="#f5c842" size={7} top="20px" right="-15px" delay="0.5s" />
                </div>
              </div>

              {/* Submit */}
              <div className={styles.submitSection}>
                <span className={styles.submitLabel}>SUBMIT BUTTON</span>
                <button type="submit" className={styles.submitBtn}>
                  Submit for Review →
                </button>
              </div>
            </form>
          </div>

          {/* Status History */}
          <div className={styles.historySection}>
            <div className={styles.historyHeader}>
              <div>
                <h3 className={styles.historyTitle}>Status History</h3>
                <span className={styles.historySub}>Full archival record</span>
              </div>
              <button className={styles.filterBtn}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>
                Filter
              </button>
            </div>

            <div className={styles.historyList}>
              {mockStatusHistory.map((item) => (
                <div key={item.id} className={styles.historyRow}>
                  <StatusPill status={item.status} />
                  <span className={styles.historyName}>{item.name}</span>
                  <span className={styles.historyDate}>{item.date}</span>
                  <span className={styles.historyDesc}>{item.description}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Need Guidance Card */}
          <div className={styles.guidanceCard}>
            <div>
              <h3 className={styles.guidanceLabel}>Need guidance?</h3>
              <h2 className={styles.guidanceTitle}>Confused about the process?</h2>
              <p className={styles.guidanceText}>
                Learn about the petition process, requirements, and expected timelines.
              </p>
              <a href="/handbook" className={styles.guidanceLink}>Open Handbook →</a>
            </div>
            <SplatterDot color="#e8613a" size={30} top="10px" right="20px" delay="0.3s" />
          </div>
        </div>

        {/* Right Sidebar: Recent Petitions */}
        <aside className={styles.aside}>
          <div className={styles.recentCard}>
            <h3 className={styles.recentTitle}>Recent Petitions</h3>
            {mockRecentPetitions.map((p) => (
              <div key={p.id} className={styles.recentItem}>
                <StatusPill status={p.status} />
                <div className={styles.recentText}>
                  <span className={styles.recentName}>{p.title}</span>
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
