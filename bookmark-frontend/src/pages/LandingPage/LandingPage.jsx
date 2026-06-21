import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { SplatterDot } from '../../styles/brand';
import BookmarkLogo from '../../components/BookmarkLogo/BookmarkLogo';
import styles from './LandingPage.module.css';

const DEMO_USERS = [
  { label: 'Super Admin', role: 'super_admin', name: 'Super Admin', email: 'admin@bookmark.edu', landing: '/admin' },
  { label: 'Registrar', role: 'registrar', name: 'Registrar Demo', email: 'registrar@bookmark.edu', landing: '/registrar/dashboard' },
  { label: 'Student', role: 'student', name: 'Student Demo', email: 'student@bookmark.edu', landing: '/student/dashboard' },
];

const FEATURES = [
  {
    icon: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/>
      </svg>
    ),
    title: 'Students',
    desc: 'Register for courses, track your GPA, submit petitions, and manage your academic journey from one dashboard.',
  },
  {
    icon: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8m-4-4v4"/>
      </svg>
    ),
    title: 'Faculty',
    desc: 'Manage class rosters, review petitions, advise students, and oversee departmental records with full visibility.',
  },
  {
    icon: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/>
      </svg>
    ),
    title: 'Admissions',
    desc: 'Process applications with an AI-powered OCR pipeline. Move candidates through the pipeline with a Kanban board.',
  },
  {
    icon: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="3"/><path d="M19.07 4.93l-1.41 1.41M6.34 17.66l-1.41 1.41M20 12h-2M6 12H4M17.66 17.66l-1.41-1.41M6.34 6.34L4.93 4.93M12 20v-2M12 6V4"/>
      </svg>
    ),
    title: 'Administration',
    desc: 'Monitor system health, manage user roles, review audit logs, and configure institutional rules in one command center.',
  },
];

export default function LandingPage() {
  const navigate = useNavigate();
  const [demoOpen, setDemoOpen] = useState(false);

  const demoLogin = (demo) => {
    const user = { id: 1, name: demo.name, email: demo.email, role: demo.role, roles: {} };
    localStorage.setItem('bookmark_token', 'demo_token');
    localStorage.setItem('bookmark_user', JSON.stringify(user));
    window.location.href = demo.landing;
  };

  return (
    <div className={styles.page}>
      {/* ═══════════════ HERO ═══════════════ */}
      <section className={styles.hero}>
        {/* Left — Dark brand panel */}
        <div className={styles.heroLeft}>
          {/* Drifting ambient glow */}
          <span className={styles.bgGlow} aria-hidden="true" />
          {/* Splatters */}
          <SplatterDot color="#e8613a" size={44} bottom="18%" left="6%" delay="0.6s" $animate />
          <SplatterDot color="#e8613a" size={20} bottom="14%" left="15%" delay="0.8s" />
          <SplatterDot color="#f5c842" size={14} bottom="24%" left="4%" delay="0.7s" />
          <SplatterDot color="#f5c842" size={10} top="10%" right="12%" delay="0.4s" $animate />
          <SplatterDot color="#4caf27" size={8} top="18%" right="20%" delay="0.9s" />
          <SplatterDot color="#e8613a" size={12} top="30%" left="8%" delay="1.1s" $animate />

          <div className={styles.heroLeftContent}>
            <div className={styles.logoBadge}>
              <BookmarkLogo size="large" />
            </div>

            <div className={styles.wordmark}>
              <h1 className={styles.brandName}>Bookmark</h1>
              <p className={styles.brandSub}>ACADEMIC ERP SUITE</p>
            </div>

            <h2 className={styles.headline}>
              <span className={styles.headlineWord} style={{ animationDelay: '0.15s' }}>Your entire</span>{' '}
              <span className={`${styles.headlineWord} ${styles.headlineAccent}`} style={{ animationDelay: '0.28s' }}>campus,</span>{' '}
              <span className={styles.headlineWord} style={{ animationDelay: '0.41s' }}>in one place.</span>
            </h2>

            <p className={styles.tagline}>
              Academic ERP that works for everyone — students, faculty, admissions, and administration.
            </p>

            <div className={styles.heroCtas}>
              <Link to="/login" className={styles.ctaPrimary}>Log In →</Link>
              <button className={styles.ctaSecondary} onClick={() => setDemoOpen((o) => !o)}>
                Try Demo ▾
              </button>
            </div>

            {demoOpen && (
              <div className={styles.demoPanel}>
                <p className={styles.demoPanelLabel}>Choose a role to explore</p>
                <div className={styles.demoBtns}>
                  {DEMO_USERS.map((d) => (
                    <button key={d.role} className={styles.demoBtn} onClick={() => demoLogin(d)}>
                      {d.label}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <p className={styles.applyNudge}>
              Prospective student?{' '}
              <Link to="/admissions" className={styles.applyLink}>Apply Now →</Link>
            </p>
          </div>
        </div>

        {/* Right — Feature cards */}
        <div className={styles.heroRight}>
          <SplatterDot color="#f5c842" size={16} top="8%" right="10%" delay="0.3s" $animate />
          <SplatterDot color="#e8613a" size={10} top="16%" right="6%" delay="0.5s" />

          <div className={styles.featureGrid}>
            {FEATURES.map((f, i) => (
              <div key={f.title} className={styles.featureCard} style={{ animationDelay: `${0.1 + i * 0.12}s` }}>
                <div className={styles.featureIcon}>{f.icon}</div>
                <h3 className={styles.featureTitle}>{f.title}</h3>
                <p className={styles.featureDesc}>{f.desc}</p>
              </div>
            ))}
          </div>

          <div className={styles.trustRow}>
            <span className={styles.trustBadge}>
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9,12 11,14 15,10" strokeWidth="2"/></svg>
              AES-256 Encrypted
            </span>
            <span className={styles.trustBadge}>
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
              99.8% Uptime
            </span>
            <span className={styles.trustBadge}>
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></svg>
              Multi-role Access
            </span>
          </div>
        </div>
      </section>
    </div>
  );
}
