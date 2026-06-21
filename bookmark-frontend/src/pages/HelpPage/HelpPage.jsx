import { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import { navForRole } from '../../config/navConfigs';
import { useAuth } from '../../context/AuthContext';
import w from '../_shared/workflow.module.css';

/* Help Center / Student Handbook — static guidance, reachable from every role. */

const TOPICS = [
  { title: 'Getting Started', body: 'Sign in with your institutional credentials. Your dashboard adapts to your role — student, faculty, registrar, admissions, or support.' },
  { title: 'Course Registration', body: 'Browse the catalog under Enrollment, check prerequisites and open seats, and register during your tier window. Full courses offer a waitlist with automatic promotion.' },
  { title: 'Petitions', body: 'Submit petitions (e.g. course overload) from Petitions → New. Track progress through Instructor → Advisor → Chair review tiers.' },
  { title: 'Grades & GPA', body: 'Your transcript, cumulative GPA, earned credits, and academic standing are on the Grades page.' },
  { title: 'Notifications', body: 'The Notifications hub centralizes petition, registration, and system alerts. Mark items read individually or all at once.' },
  { title: 'Support', body: 'Need help? Open a support ticket and a technician will respond in your ticket thread.' },
];

export default function HelpPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const navItems = useMemo(() => navForRole(user?.role), [user?.role]);

  return (
    <AppShell navItems={navItems} logoVariant="stacked" sidebarLabel="HELP CENTER">
      <PageHeader title="Help Center & Handbook" subtitle="Guidance for using the Bookmark Academic ERP" useBrandFont />

      <div className={`${w.statRow} ${w.cols2}`}>
        {TOPICS.map((t) => (
          <div key={t.title} className={`${w.card} ${w.cardAccent}`}>
            <h3 className={w.cardTitle}>{t.title}</h3>
            <p style={{ fontSize: '0.88rem', color: 'var(--color-text-secondary)', lineHeight: 1.6 }}>{t.body}</p>
          </div>
        ))}
      </div>

      <div style={{ display: 'flex', gap: 12, marginTop: 24, flexWrap: 'wrap' }}>
        <button className={`${w.btn} ${w.btnPrimary}`} onClick={() => navigate('/notifications')}>Open Notifications</button>
        <button className={`${w.btn} ${w.btnOutline}`} onClick={() => navigate('/settings')}>Account Settings</button>
      </div>
    </AppShell>
  );
}
