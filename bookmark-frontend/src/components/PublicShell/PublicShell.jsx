import { useNavigate } from 'react-router-dom';
import BookmarkLogo from '../BookmarkLogo/BookmarkLogo';
import w from '../../pages/_shared/workflow.module.css';

/* ============================================================
   PUBLIC SHELL — Top navbar layout for public-facing pages
   (Admissions Portal, Application Status). No sidebar.
   ============================================================ */

export default function PublicShell({ children, active }) {
  const navigate = useNavigate();
  const links = [
    { label: 'Programs', path: '/admissions' },
    { label: 'How to Apply', path: '/admissions' },
    { label: 'Track Application', path: '/admissions/status' },
  ];

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-bg-warm)' }}>
      <header style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '14px 32px', background: '#fff', borderBottom: '1px solid var(--color-border-light)',
        position: 'sticky', top: 0, zIndex: 10,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer' }} onClick={() => navigate('/admissions')}>
          <BookmarkLogo size="small" />
          <span style={{ fontFamily: 'var(--font-brand)', fontSize: '1.4rem', fontWeight: 700 }}>Bookmark</span>
        </div>
        <nav style={{ display: 'flex', gap: 24 }}>
          {links.map((l) => (
            <button key={l.label} onClick={() => navigate(l.path)}
              style={{ background: 'none', border: 'none', cursor: 'pointer', fontFamily: 'inherit', fontWeight: 600,
                       fontSize: '0.9rem', color: active === l.label ? 'var(--color-lime-dark)' : 'var(--color-text-secondary)' }}>
              {l.label}
            </button>
          ))}
        </nav>
        <div style={{ display: 'flex', gap: 10 }}>
          <button className={`${w.btn} ${w.btnOutline} ${w.btnSm}`} onClick={() => navigate('/login')}>Log In</button>
          <button className={`${w.btn} ${w.btnPrimary} ${w.btnSm}`} onClick={() => navigate('/admissions')}>Apply Now</button>
        </div>
      </header>
      <main style={{ padding: '32px', maxWidth: 1200, margin: '0 auto' }}>{children}</main>
    </div>
  );
}
