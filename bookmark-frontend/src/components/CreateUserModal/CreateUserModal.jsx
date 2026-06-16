import { useState } from 'react';
import styles from './CreateUserModal.module.css';

/* ============================================================
   CREATE USER MODAL — Form to add a new user
   ============================================================ */

export default function CreateUserModal({ isOpen, onClose }) {
  const [form, setForm] = useState({ name: '', email: '', role: 'Student', active: true });

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    // TODO(backend): implement POST /api/v1/admin/users
    console.log('Create user:', form);
    onClose();
  };

  return (
    <>
      <div className={styles.overlay} onClick={onClose} />
      <div className={styles.modal}>
        <div className={styles.topBorder} />
        <div className={styles.content}>
          <div className={styles.header}>
            <h2 className={styles.title}>Create New User</h2>
            <button className={styles.closeBtn} onClick={onClose} aria-label="Close">×</button>
          </div>

          <form onSubmit={handleSubmit} className={styles.form}>
            <div className={styles.field}>
              <label className={styles.label}>Full Name</label>
              <input
                type="text"
                className={styles.input}
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="e.g. Dr. Sarah Chen"
                required
              />
            </div>

            <div className={styles.field}>
              <label className={styles.label}>Email Address</label>
              <input
                type="email"
                className={styles.input}
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                placeholder="e.g. sarah@university.edu"
                required
              />
            </div>

            <div className={styles.field}>
              <label className={styles.label}>Assigned Role</label>
              <select
                className={styles.select}
                value={form.role}
                onChange={(e) => setForm({ ...form, role: e.target.value })}
              >
                <option>Student</option>
                <option>Instructor</option>
                <option>Admin</option>
                <option>Registrar</option>
              </select>
            </div>

            <div className={styles.actions}>
              <button type="button" className={styles.cancelBtn} onClick={onClose}>Cancel</button>
              <button type="submit" className={styles.submitBtn}>Create User</button>
            </div>
          </form>
        </div>
      </div>
    </>
  );
}
