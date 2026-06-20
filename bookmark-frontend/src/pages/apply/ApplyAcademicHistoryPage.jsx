import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import Stepper from '../../components/Stepper/Stepper';
import { useApplication } from '../../context/ApplicationContext';
import styles from './apply.module.css';
import logoUrl from '../../assets/logos/bookark_logo.svg';

const STEPS = [
  { label: 'PERSONAL INFO', status: 'completed' },
  { label: 'ACADEMIC HISTORY', status: 'active' },
  { label: 'DOCUMENT UPLOAD', status: 'future' },
  { label: 'REVIEW & SUBMIT', status: 'future' },
];

const PROGRAMS = [
  'Computer Science',
  'Business Administration',
  'Engineering',
  'Medicine',
  'Law',
  'Education',
  'Arts & Humanities',
  'Social Sciences',
  'Mathematics',
  'Natural Sciences',
];

const YEARS = Array.from({ length: 30 }, (_, i) => String(new Date().getFullYear() - i));

export default function ApplyAcademicHistoryPage() {
  const navigate = useNavigate();
  const { state, setAcademicHistory } = useApplication();
  const [form, setForm] = useState({ ...state.academicHistory });
  const [errors, setErrors] = useState({});

  const set = (key, val) => setForm((f) => ({ ...f, [key]: val }));

  const validate = () => {
    const e = {};
    if (!form.previous_school.trim()) e.previous_school = 'Previous school is required';
    if (!form.degree_program) e.degree_program = 'Please select a program';
    if (!form.graduation_year) e.graduation_year = 'Please select graduation year';
    return e;
  };

  const handleNext = () => {
    const e = validate();
    if (Object.keys(e).length) { setErrors(e); return; }
    setAcademicHistory(form);
    navigate('/apply/documents');
  };

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
          <Link to="/admissions/status" className={styles.navLink}>Track Application</Link>
          <Link to="/login" className={styles.navLink}>Sign In</Link>
        </nav>
      </header>

      <Stepper steps={STEPS} />

      <div className={styles.content}>
        <h2 className={styles.stepTitle}>Academic History</h2>
        <p className={styles.stepSub}>Tell us about your previous education and the program you're applying for.</p>

        <div className={styles.formCard}>
          <div className={styles.grid2}>
            <div className={styles.fieldGroupFull}>
              <label className={styles.label}>Previous School / Institution *</label>
              <input
                className={styles.input}
                style={errors.previous_school ? { borderColor: '#dc2626' } : {}}
                value={form.previous_school}
                onChange={(e) => { set('previous_school', e.target.value); setErrors((err) => ({ ...err, previous_school: '' })); }}
                placeholder="e.g. Cairo University"
              />
              {errors.previous_school && <span style={{ color: '#dc2626', fontSize: 12 }}>{errors.previous_school}</span>}
            </div>

            <div className={styles.fieldGroup}>
              <label className={styles.label}>Desired Program *</label>
              <select
                className={styles.select}
                style={errors.degree_program ? { borderColor: '#dc2626' } : {}}
                value={form.degree_program}
                onChange={(e) => { set('degree_program', e.target.value); setErrors((err) => ({ ...err, degree_program: '' })); }}
              >
                <option value="">Select a program…</option>
                {PROGRAMS.map((p) => <option key={p}>{p}</option>)}
              </select>
              {errors.degree_program && <span style={{ color: '#dc2626', fontSize: 12 }}>{errors.degree_program}</span>}
            </div>

            <div className={styles.fieldGroup}>
              <label className={styles.label}>Graduation Year *</label>
              <select
                className={styles.select}
                style={errors.graduation_year ? { borderColor: '#dc2626' } : {}}
                value={form.graduation_year}
                onChange={(e) => { set('graduation_year', e.target.value); setErrors((err) => ({ ...err, graduation_year: '' })); }}
              >
                <option value="">Select year…</option>
                {YEARS.map((y) => <option key={y}>{y}</option>)}
              </select>
              {errors.graduation_year && <span style={{ color: '#dc2626', fontSize: 12 }}>{errors.graduation_year}</span>}
            </div>

            <div className={styles.fieldGroup}>
              <label className={styles.label}>Cumulative GPA</label>
              <input
                className={styles.input}
                type="number"
                step="0.01"
                min="0"
                max="4"
                value={form.gpa}
                onChange={(e) => set('gpa', e.target.value)}
                placeholder="e.g. 3.75"
              />
            </div>

            <div className={styles.fieldGroup}>
              <label className={styles.label}>Application Type</label>
              <select
                className={styles.select}
                value={form.application_type}
                onChange={(e) => set('application_type', e.target.value)}
              >
                <option value="regular">Regular</option>
                <option value="transfer">Transfer</option>
                <option value="graduate">Graduate</option>
                <option value="international">International</option>
              </select>
            </div>
          </div>

          <div className={styles.actions}>
            <button className={styles.btnBack} onClick={() => navigate('/apply/personal-info')}>
              ← Back
            </button>
            <button className={styles.btnPrimary} onClick={handleNext}>
              Continue to Document Upload →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
