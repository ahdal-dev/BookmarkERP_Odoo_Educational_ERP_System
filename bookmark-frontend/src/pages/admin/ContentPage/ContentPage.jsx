import { useState } from 'react';
import AppShell from '../../../components/AppShell/AppShell';
import TopBar from '../../../components/TopBar/TopBar';
import StatusPill from '../../../components/StatusPill/StatusPill';
import ToggleSwitch from '../../../components/ToggleSwitch/ToggleSwitch';
import { adminDashboardNav } from '../../../config/navConfigs';
import {
  mockAnnouncements,
  mockEmailTemplates,
  mockPrograms,
  openTicketCount,
} from '../../../mocks/adminMocks';
import styles from './ContentPage.module.css';

const TABS = ['Announcements', 'Email Templates', 'Academic Programs'];

const navWithActive = adminDashboardNav.map((n) =>
  n.path === '/admin/content' ? { ...n, active: true } : n
);

const STATUS_VARIANT = {
  Published: 'green',
  Scheduled: 'yellow',
  Draft: 'black',
  Active: 'green',
  'Under Review': 'yellow',
};

const PRIORITY_COLOR = { High: '#e8613a', Medium: '#f5c842', Low: '#b5b3ab' };

export default function ContentPage() {
  const [activeTab, setActiveTab] = useState('Announcements');
  const [announcements, setAnnouncements] = useState(mockAnnouncements);
  const [templates, setTemplates] = useState(mockEmailTemplates);
  const [showNewAnnouncement, setShowNewAnnouncement] = useState(false);
  const [showNewTemplate, setShowNewTemplate] = useState(false);
  const [editingAnn, setEditingAnn] = useState(null);
  const [editingTemplate, setEditingTemplate] = useState(null);
  const [previewTemplate, setPreviewTemplate] = useState(null);
  const [showAddProgram, setShowAddProgram] = useState(false);
  const [searchQ, setSearchQ] = useState('');

  const filteredAnn = announcements.filter((a) =>
    a.title.toLowerCase().includes(searchQ.toLowerCase())
  );

  const toggleTemplate = (id) => {
    setTemplates((prev) =>
      prev.map((t) => (t.id === id ? { ...t, active: !t.active } : t))
    );
  };

  const deleteAnn = (id) => setAnnouncements((prev) => prev.filter((a) => a.id !== id));

  const togglePin = (id) =>
    setAnnouncements((prev) =>
      prev.map((a) => (a.id === id ? { ...a, pinned: !a.pinned } : a))
    );

  return (
    <AppShell
      navItems={navWithActive}
      logoVariant="icon-text"
      sidebarLabel="ADMIN PANEL"
      topBar={<TopBar searchPlaceholder="Search content, templates..." notificationCount={openTicketCount} />}
    >
      <div className={styles.breadcrumb}>ADMIN CONTROL / CONTENT & CONFIG</div>

      <div className={styles.pageHeader}>
        <div>
          <h1 className={styles.title}>Content & Configuration</h1>
          <p className={styles.subtitle}>Manage announcements, email templates, and academic programs.</p>
        </div>
        {activeTab === 'Announcements' && (
          <button className={styles.primaryBtn} onClick={() => setShowNewAnnouncement(true)}>
            + New Announcement
          </button>
        )}
        {activeTab === 'Email Templates' && (
          <button className={styles.primaryBtn} onClick={() => setShowNewTemplate(true)}>
            + New Template
          </button>
        )}
      </div>

      {/* Tabs */}
      <div className={styles.tabs}>
        {TABS.map((t) => (
          <button
            key={t}
            className={`${styles.tab} ${activeTab === t ? styles.tabActive : ''}`}
            onClick={() => setActiveTab(t)}
          >
            {t}
          </button>
        ))}
      </div>

      {/* ── Announcements Tab ── */}
      {activeTab === 'Announcements' && (
        <div className={styles.card}>
          <div className={styles.toolbar}>
            <input
              className={styles.searchInput}
              placeholder="Search announcements..."
              value={searchQ}
              onChange={(e) => setSearchQ(e.target.value)}
            />
            <span className={styles.countLabel}>{filteredAnn.length} announcements</span>
          </div>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Title</th>
                <th>Audience</th>
                <th>Status</th>
                <th>Date</th>
                <th>Pinned</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredAnn.map((ann) => (
                <tr key={ann.id}>
                  <td className={styles.titleCell}>{ann.title}</td>
                  <td className={styles.muted}>{ann.audience}</td>
                  <td>
                    <StatusPill status={ann.status} variant={STATUS_VARIANT[ann.status] || 'black'} />
                  </td>
                  <td className={styles.muted}>{ann.date}</td>
                  <td>
                    <ToggleSwitch
                      checked={ann.pinned}
                      onChange={() => togglePin(ann.id)}
                      label=""
                    />
                  </td>
                  <td>
                    <div className={styles.rowActions}>
                      <button className={styles.editBtn} onClick={() => setEditingAnn(ann)}>Edit</button>
                      <button className={styles.deleteBtn} onClick={() => deleteAnn(ann.id)}>Delete</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* ── Email Templates Tab ── */}
      {activeTab === 'Email Templates' && (
        <div className={styles.card}>
          <div className={styles.templateGrid}>
            {templates.map((tpl) => (
              <div key={tpl.id} className={styles.templateCard}>
                <div className={styles.templateTop}>
                  <div>
                    <div className={styles.templateName}>{tpl.name}</div>
                    <div className={styles.templateTrigger}>Trigger: {tpl.trigger}</div>
                    <div className={styles.templateDate}>Last edited: {tpl.lastEdited}</div>
                  </div>
                  <ToggleSwitch
                    checked={tpl.active}
                    onChange={() => toggleTemplate(tpl.id)}
                    label=""
                  />
                </div>
                <div className={styles.templateActions}>
                  <button className={styles.editBtn} onClick={() => setEditingTemplate(tpl)}>Edit Template</button>
                  <button className={styles.previewBtn} onClick={() => setPreviewTemplate(tpl)}>Preview</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Academic Programs Tab ── */}
      {activeTab === 'Academic Programs' && (
        <div className={styles.card}>
          <div className={styles.toolbar}>
            <span className={styles.countLabel}>{mockPrograms.length} programs</span>
            <button className={styles.primaryBtn} onClick={() => setShowAddProgram(true)}>+ Add Program</button>
          </div>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Code</th>
                <th>Program Name</th>
                <th>Department</th>
                <th>Credits</th>
                <th>Enrolled</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {mockPrograms.map((prog) => (
                <tr key={prog.id}>
                  <td className={styles.codeCell}>{prog.code}</td>
                  <td className={styles.titleCell}>{prog.name}</td>
                  <td className={styles.muted}>{prog.department}</td>
                  <td className={styles.muted}>{prog.credits}</td>
                  <td className={styles.muted}>{prog.enrolled}</td>
                  <td>
                    <StatusPill status={prog.status} variant={STATUS_VARIANT[prog.status] || 'black'} />
                  </td>
                  <td>
                    <div className={styles.rowActions}>
                      <button className={styles.editBtn}>Edit</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* ── New Announcement Modal ── */}
      {showNewAnnouncement && (
        <div className={styles.modalOverlay} onClick={() => setShowNewAnnouncement(false)}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <span className={styles.modalTitle}>New Announcement</span>
              <button className={styles.modalClose} onClick={() => setShowNewAnnouncement(false)}>✕</button>
            </div>
            <div className={styles.modalBody}>
              <div className={styles.field}>
                <label className={styles.fieldLabel}>Title</label>
                <input className={styles.fieldInput} placeholder="Announcement title..." />
              </div>
              <div className={styles.field}>
                <label className={styles.fieldLabel}>Audience</label>
                <select className={styles.fieldInput}>
                  <option>All Users</option>
                  <option>All Students</option>
                  <option>Faculty</option>
                  <option>Prospective Students</option>
                  <option>Registrar Staff</option>
                </select>
              </div>
              <div className={styles.field}>
                <label className={styles.fieldLabel}>Status</label>
                <select className={styles.fieldInput}>
                  <option>Draft</option>
                  <option>Scheduled</option>
                  <option>Published</option>
                </select>
              </div>
              <div className={styles.field}>
                <label className={styles.fieldLabel}>Content</label>
                <textarea className={styles.fieldTextarea} rows={4} placeholder="Write your announcement..." />
              </div>
            </div>
            <div className={styles.modalFooter}>
              <button className={styles.cancelBtn} onClick={() => setShowNewAnnouncement(false)}>Discard</button>
              <button className={styles.saveBtn} onClick={() => setShowNewAnnouncement(false)}>Publish</button>
            </div>
          </div>
        </div>
      )}

      {/* ── Edit Announcement Modal ── */}
      {editingAnn && (
        <div className={styles.modalOverlay} onClick={() => setEditingAnn(null)}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <span className={styles.modalTitle}>Edit Announcement</span>
              <button className={styles.modalClose} onClick={() => setEditingAnn(null)}>✕</button>
            </div>
            <div className={styles.modalBody}>
              <div className={styles.field}>
                <label className={styles.fieldLabel}>Title</label>
                <input className={styles.fieldInput} defaultValue={editingAnn.title} />
              </div>
              <div className={styles.field}>
                <label className={styles.fieldLabel}>Audience</label>
                <select className={styles.fieldInput} defaultValue={editingAnn.audience}>
                  <option>All Users</option>
                  <option>All Students</option>
                  <option>Faculty</option>
                  <option>Prospective Students</option>
                  <option>Registrar Staff</option>
                </select>
              </div>
              <div className={styles.field}>
                <label className={styles.fieldLabel}>Status</label>
                <select className={styles.fieldInput} defaultValue={editingAnn.status}>
                  <option>Draft</option>
                  <option>Scheduled</option>
                  <option>Published</option>
                </select>
              </div>
            </div>
            <div className={styles.modalFooter}>
              <button className={styles.cancelBtn} onClick={() => setEditingAnn(null)}>Discard</button>
              <button className={styles.saveBtn} onClick={() => setEditingAnn(null)}>Save Changes</button>
            </div>
          </div>
        </div>
      )}

      {/* ── Edit Template Modal ── */}
      {editingTemplate && (
        <div className={styles.modalOverlay} onClick={() => setEditingTemplate(null)}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <span className={styles.modalTitle}>Edit Template — {editingTemplate.name}</span>
              <button className={styles.modalClose} onClick={() => setEditingTemplate(null)}>✕</button>
            </div>
            <div className={styles.modalBody}>
              <div className={styles.field}>
                <label className={styles.fieldLabel}>Template Name</label>
                <input className={styles.fieldInput} defaultValue={editingTemplate.name} />
              </div>
              <div className={styles.field}>
                <label className={styles.fieldLabel}>Trigger Event</label>
                <input className={styles.fieldInput} defaultValue={editingTemplate.trigger} />
              </div>
              <div className={styles.field}>
                <label className={styles.fieldLabel}>Subject Line</label>
                <input className={styles.fieldInput} placeholder="Email subject..." />
              </div>
              <div className={styles.field}>
                <label className={styles.fieldLabel}>Body</label>
                <textarea className={styles.fieldTextarea} rows={4} placeholder="Email HTML or plain text..." />
              </div>
            </div>
            <div className={styles.modalFooter}>
              <button className={styles.cancelBtn} onClick={() => setEditingTemplate(null)}>Discard</button>
              <button className={styles.saveBtn} onClick={() => setEditingTemplate(null)}>Save Template</button>
            </div>
          </div>
        </div>
      )}

      {/* ── Preview Template Modal ── */}
      {previewTemplate && (
        <div className={styles.modalOverlay} onClick={() => setPreviewTemplate(null)}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <span className={styles.modalTitle}>Preview — {previewTemplate.name}</span>
              <button className={styles.modalClose} onClick={() => setPreviewTemplate(null)}>✕</button>
            </div>
            <div className={styles.modalBody}>
              <div className={styles.previewMeta}>
                <span className={styles.fieldLabel}>Trigger:</span>
                <span className={styles.previewValue}>{previewTemplate.trigger}</span>
              </div>
              <div className={styles.previewMeta}>
                <span className={styles.fieldLabel}>Last Edited:</span>
                <span className={styles.previewValue}>{previewTemplate.lastEdited}</span>
              </div>
              <div className={styles.previewBox}>
                <p className={styles.previewSubject}><strong>Subject:</strong> [Auto-generated from trigger]</p>
                <p className={styles.previewBodyText}>Dear [Student Name],</p>
                <p className={styles.previewBodyText}>This is a placeholder preview of the <strong>{previewTemplate.name}</strong> email template. The full rendered body with merge fields will appear here in production.</p>
                <p className={styles.previewBodyText}>Regards,<br/>Bookmark Academic ERP Team</p>
              </div>
            </div>
            <div className={styles.modalFooter}>
              <button className={styles.cancelBtn} onClick={() => setPreviewTemplate(null)}>Close</button>
              <button className={styles.saveBtn} onClick={() => { setEditingTemplate(previewTemplate); setPreviewTemplate(null); }}>Edit Template</button>
            </div>
          </div>
        </div>
      )}

      {/* ── Add Program Modal ── */}
      {showAddProgram && (
        <div className={styles.modalOverlay} onClick={() => setShowAddProgram(false)}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <span className={styles.modalTitle}>Add Academic Program</span>
              <button className={styles.modalClose} onClick={() => setShowAddProgram(false)}>✕</button>
            </div>
            <div className={styles.modalBody}>
              <div className={styles.field}>
                <label className={styles.fieldLabel}>Program Code</label>
                <input className={styles.fieldInput} placeholder="e.g. CS-401" />
              </div>
              <div className={styles.field}>
                <label className={styles.fieldLabel}>Program Name</label>
                <input className={styles.fieldInput} placeholder="e.g. Advanced Software Engineering" />
              </div>
              <div className={styles.field}>
                <label className={styles.fieldLabel}>Department</label>
                <select className={styles.fieldInput}>
                  <option>Computer Science</option>
                  <option>Information Systems</option>
                  <option>Business Administration</option>
                  <option>Engineering</option>
                </select>
              </div>
              <div className={styles.field}>
                <label className={styles.fieldLabel}>Credit Hours</label>
                <input className={styles.fieldInput} type="number" placeholder="e.g. 135" />
              </div>
              <div className={styles.field}>
                <label className={styles.fieldLabel}>Status</label>
                <select className={styles.fieldInput}>
                  <option>Active</option>
                  <option>Under Review</option>
                </select>
              </div>
            </div>
            <div className={styles.modalFooter}>
              <button className={styles.cancelBtn} onClick={() => setShowAddProgram(false)}>Discard</button>
              <button className={styles.saveBtn} onClick={() => setShowAddProgram(false)}>Add Program</button>
            </div>
          </div>
        </div>
      )}

      {/* ── New Template Modal ── */}
      {showNewTemplate && (
        <div className={styles.modalOverlay} onClick={() => setShowNewTemplate(false)}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <span className={styles.modalTitle}>New Email Template</span>
              <button className={styles.modalClose} onClick={() => setShowNewTemplate(false)}>✕</button>
            </div>
            <div className={styles.modalBody}>
              <div className={styles.field}>
                <label className={styles.fieldLabel}>Template Name</label>
                <input className={styles.fieldInput} placeholder="e.g. Welcome Email" />
              </div>
              <div className={styles.field}>
                <label className={styles.fieldLabel}>Trigger Event</label>
                <select className={styles.fieldInput}>
                  <option>User Created</option>
                  <option>Application Submit</option>
                  <option>Manual / Auth Event</option>
                  <option>Course Enrolment</option>
                  <option>Officer Action</option>
                </select>
              </div>
              <div className={styles.field}>
                <label className={styles.fieldLabel}>Subject Line</label>
                <input className={styles.fieldInput} placeholder="Email subject..." />
              </div>
              <div className={styles.field}>
                <label className={styles.fieldLabel}>Body</label>
                <textarea className={styles.fieldTextarea} rows={5} placeholder="Email HTML or plain text..." />
              </div>
            </div>
            <div className={styles.modalFooter}>
              <button className={styles.cancelBtn} onClick={() => setShowNewTemplate(false)}>Discard</button>
              <button className={styles.saveBtn} onClick={() => setShowNewTemplate(false)}>Save Template</button>
            </div>
          </div>
        </div>
      )}
    </AppShell>
  );
}
