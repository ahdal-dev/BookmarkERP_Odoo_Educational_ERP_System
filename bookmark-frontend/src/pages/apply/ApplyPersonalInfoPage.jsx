import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import Stepper from '../../components/Stepper/Stepper';
import { useApplication } from '../../context/ApplicationContext';
import styles from './apply.module.css';
import logoUrl from '../../assets/logos/bookark_logo.svg';

const STEPS = [
  { label: 'PERSONAL INFO', status: 'active' },
  { label: 'ACADEMIC HISTORY', status: 'future' },
  { label: 'DOCUMENT UPLOAD', status: 'future' },
  { label: 'REVIEW & SUBMIT', status: 'future' },
];

export default function ApplyPersonalInfoPage() {
  const navigate = useNavigate();
  const { state, setPersonalInfo } = useApplication();
  const [form, setForm] = useState({ ...state.personalInfo });
  const [errors, setErrors] = useState({});

  const set = (key, val) => setForm((f) => ({ ...f, [key]: val }));

  const validate = () => {
    const e = {};
    if (!form.name.trim()) e.name = 'Full name is required';
    if (!form.email.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) e.email = 'Valid email is required';
    if (!form.phone.trim()) e.phone = 'Phone number is required';
    if (!form.national_id.trim()) e.national_id = 'National ID is required';
    return e;
  };

  const handleNext = () => {
    const e = validate();
    if (Object.keys(e).length) { setErrors(e); return; }
    setPersonalInfo(form);
    navigate('/apply/academic-history');
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
        <h2 className={styles.stepTitle}>Personal Information</h2>
        <p className={styles.stepSub}>Start your application by providing your personal details.</p>

        <div className={styles.formCard}>
          <div className={styles.grid2}>
            <div className={styles.fieldGroup}>
              <label className={styles.label}>Full Name *</label>
              <input
                className={styles.input}
                style={errors.name ? { borderColor: '#dc2626' } : {}}
                value={form.name}
                onChange={(e) => { set('name', e.target.value); setErrors((err) => ({ ...err, name: '' })); }}
                placeholder="e.g. Ahmed Mohamed"
              />
              {errors.name && <span style={{ color: '#dc2626', fontSize: 12 }}>{errors.name}</span>}
            </div>

            <div className={styles.fieldGroup}>
              <label className={styles.label}>National ID *</label>
              <input
                className={styles.input}
                style={errors.national_id ? { borderColor: '#dc2626' } : {}}
                value={form.national_id}
                onChange={(e) => { set('national_id', e.target.value); setErrors((err) => ({ ...err, national_id: '' })); }}
                placeholder="14-digit national ID"
                maxLength={14}
              />
              {errors.national_id && <span style={{ color: '#dc2626', fontSize: 12 }}>{errors.national_id}</span>}
            </div>

            <div className={styles.fieldGroup}>
              <label className={styles.label}>Email Address *</label>
              <input
                className={styles.input}
                type="email"
                style={errors.email ? { borderColor: '#dc2626' } : {}}
                value={form.email}
                onChange={(e) => { set('email', e.target.value); setErrors((err) => ({ ...err, email: '' })); }}
                placeholder="you@email.com"
              />
              {errors.email && <span style={{ color: '#dc2626', fontSize: 12 }}>{errors.email}</span>}
            </div>

            <div className={styles.fieldGroup}>
              <label className={styles.label}>Phone Number *</label>
              <input
                className={styles.input}
                type="tel"
                style={errors.phone ? { borderColor: '#dc2626' } : {}}
                value={form.phone}
                onChange={(e) => { set('phone', e.target.value); setErrors((err) => ({ ...err, phone: '' })); }}
                placeholder="+20 1xx xxx xxxx"
              />
              {errors.phone && <span style={{ color: '#dc2626', fontSize: 12 }}>{errors.phone}</span>}
            </div>

            <div className={styles.fieldGroup}>
              <label className={styles.label}>Date of Birth</label>
              <input
                className={styles.input}
                type="date"
                value={form.date_of_birth}
                onChange={(e) => set('date_of_birth', e.target.value)}
              />
            </div>

            <div className={styles.fieldGroup}>
              <label className={styles.label}>Nationality</label>
              <select className={styles.select} value={form.nationality} onChange={(e) => set('nationality', e.target.value)}>
                <option>Egyptian</option>
                <option>Saudi</option>
                <option>Emirati</option>
                <option>Jordanian</option>
                <option>Lebanese</option>
                <option>Other</option>
              </select>
            </div>
          </div>

          <div className={styles.actions}>
            <Link to="/admissions" className={styles.btnBack}>← Back to Programs</Link>
            <button className={styles.btnPrimary} onClick={handleNext}>
              Continue to Academic History →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
