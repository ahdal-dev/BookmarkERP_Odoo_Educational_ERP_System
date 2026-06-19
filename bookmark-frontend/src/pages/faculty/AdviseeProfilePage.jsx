import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import AppShell from '../../components/AppShell/AppShell';
import PageHeader from '../../components/PageHeader/PageHeader';
import StatusPill from '../../components/StatusPill/StatusPill';
import SegmentedControl from '../../components/SegmentedControl/SegmentedControl';
import { advisorNav } from '../../config/navConfigs';
import { advisingAPI } from '../../api/apiGateway';
import useAsync from '../../hooks/useAsync';
import w from '../_shared/workflow.module.css';

/* Read-only advisee academic profile (live). */

const STANDING_LABEL = { good: 'Good Standing', deans_list: "Dean's List", probation: 'Probation', new: 'New' };
const CLASS_LABEL = { freshman: 'Freshman', sophomore: 'Sophomore', junior: 'Junior', senior: 'Senior' };
const GRADE_VARIANT = { A: 'green', 'A-': 'green', 'B+': 'yellow', B: 'yellow', 'B-': 'yellow', C: 'coral', F: 'coral' };

function initials(name = '') { return name.split(' ').map((p) => p[0]).slice(0, 2).join(''); }

export default function AdviseeProfilePage() {
  const { studentId } = useParams();
  const navigate = useNavigate();
  const { data, loading, error } = useAsync(() => advisingAPI.getAdviseeProfile(Number(studentId)), [studentId]);
  const s = data?.profile;
  const transcript = data?.transcript || [];
  const petitions = data?.petitions || [];
  const [tab, setTab] = useState('Academic Record');
  const [note, setNote] = useState('');
  const [noteSaved, setNoteSaved] = useState(false);

  if (loading) return <AppShell navItems={advisorNav} logoVariant="stacked" sidebarLabel="ACADEMIC ADVISOR"><div className={w.card}><div className={w.empty}>Loading profile…</div></div></AppShell>;
  if (error || !s) return <AppShell navItems={advisorNav} logoVariant="stacked" sidebarLabel="ACADEMIC ADVISOR"><div className={w.card}><div className={w.empty}><div className={w.emptyTitle}>Couldn't load profile</div><p>{error || 'Not found.'}</p><button className={`${w.btn} ${w.btnOutline} ${w.btnSm}`} onClick={() => navigate('/faculty/advisees')}>Back</button></div></div></AppShell>;

  return (
    <AppShell navItems={advisorNav} logoVariant="stacked" sidebarLabel="ACADEMIC ADVISOR">
      <div className={w.breadcrumb}>
        <span onClick={() => navigate('/faculty/advisees')} style={{ cursor: 'pointer' }}>My Advisees</span> › {s.name}
      </div>

      <div className={w.cardDark} style={{ display: 'flex', alignItems: 'center', gap: 20, marginBottom: 20 }}>
        <div style={{ width: 64, height: 64, borderRadius: '50%', background: 'rgba(255,255,255,0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, fontSize: '1.3rem' }}>{initials(s.name)}</div>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: '1.4rem', fontWeight: 800 }}>{s.name}</div>
          <div style={{ color: 'rgba(255,255,255,0.7)', fontSize: '0.85rem' }}>{s.email} · {CLASS_LABEL[s.class_year] || s.class_year}</div>
          <div style={{ marginTop: 8, display: 'flex', gap: 8 }}>
            <StatusPill status={STANDING_LABEL[s.standing] || s.standing} variant={s.standing === 'probation' ? 'coral' : 'green'} />
            {s.on_hold && <StatusPill status="On Hold" variant="coral" />}
          </div>
        </div>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--color-lime)' }}>{(s.gpa ?? 0).toFixed(2)}</div>
          <div style={{ fontSize: '0.72rem', color: 'rgba(255,255,255,0.6)' }}>Cumulative GPA · {s.earned_credits} cr</div>
        </div>
      </div>

      <div style={{ marginBottom: 16 }}>
        <SegmentedControl options={['Academic Record', 'Petitions', 'Notes']} value={tab} onChange={setTab} />
      </div>

      {tab === 'Academic Record' && (
        <div className={w.card}>
          <div className={w.sectionTitle}>Course History</div>
          {transcript.length === 0 ? <p style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>No graded courses yet.</p> : (
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
              <thead><tr style={{ textTransform: 'uppercase', fontSize: '0.66rem', color: 'var(--color-text-muted)', textAlign: 'left' }}>
                <th style={{ padding: 8 }}>Code</th><th style={{ padding: 8 }}>Course</th><th style={{ padding: 8 }}>Grade</th>
              </tr></thead>
              <tbody>{transcript.map((h, i) => (
                <tr key={i} style={{ borderTop: '1px solid var(--color-border-light)' }}>
                  <td style={{ padding: 8 }}><strong>{h.course_code}</strong></td><td style={{ padding: 8 }}>{h.course_name}</td>
                  <td style={{ padding: 8 }}><StatusPill status={h.grade} variant={GRADE_VARIANT[h.grade] || 'black'} /></td>
                </tr>
              ))}</tbody>
            </table>
          )}
        </div>
      )}

      {tab === 'Petitions' && (
        <div className={w.card}>
          {petitions.length === 0 ? <div className={w.empty}><p>No petitions on record.</p></div> : petitions.map((p) => (
            <div key={p.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 0', borderBottom: '1px solid var(--color-border-light)' }}>
              <span><strong>{p.name}</strong> — {p.subject}</span>
              <StatusPill status={p.state} variant={p.state === 'approved' ? 'green' : p.state === 'rejected' ? 'coral' : 'yellow'} />
            </div>
          ))}
        </div>
      )}

      {tab === 'Notes' && (
        <div className={w.card}>
          <div className={w.field}>
            <span className={w.fieldLabel}>Add a private advising note</span>
            <textarea className={w.textarea} value={note} onChange={(e) => { setNote(e.target.value); setNoteSaved(false); }} placeholder="Visible only to advisors and the chair..." />
          </div>
          <button className={`${w.btn} ${w.btnPrimary}`} disabled={!note.trim()} onClick={() => { setNoteSaved(true); setNote(''); }}>Save Note</button>
          {noteSaved && <span style={{ marginLeft: 12, color: 'var(--color-lime-dark)', fontWeight: 600, fontSize: '0.85rem' }}>✓ Note saved locally</span>}
        </div>
      )}

      <div className={w.readonlyBar}>🔒 Read-only profile. To make changes, contact the Registrar.</div>
    </AppShell>
  );
}
