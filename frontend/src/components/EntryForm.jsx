import { useState, useEffect } from 'react';

export default function EntryForm({ entry, onSave, onCancel }) {
  const [form, setForm] = useState({
    title: '',
    username: '',
    password: '',
    url: '',
    notes: '',
  });

  useEffect(() => {
    if (entry) setForm(entry);
  }, [entry]);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(form);
  };

  return (
    <div style={styles.overlay}>
      <div style={styles.modal}>
        <h2 style={styles.title}>{entry ? 'Edit Entry' : 'New Entry'}</h2>
        <form onSubmit={handleSubmit} style={styles.form}>
          {['title', 'username', 'password', 'url', 'notes'].map((field) => (
            <div key={field} style={styles.fieldGroup}>
              <label style={styles.label}>{field.charAt(0).toUpperCase() + field.slice(1)}</label>
              <input
                style={styles.input}
                type={field === 'password' ? 'password' : 'text'}
                name={field}
                value={form[field] || ''}
                onChange={handleChange}
                required={field === 'title'}
              />
            </div>
          ))}
          <div style={styles.buttons}>
            <button type="button" style={styles.cancelBtn} onClick={onCancel}>Cancel</button>
            <button type="submit" style={styles.saveBtn}>Save Entry</button>
          </div>
        </form>
      </div>
    </div>
  );
}

const styles = {
  overlay: {
    position: 'fixed',
    inset: 0,
    backgroundColor: 'rgba(0,0,0,0.7)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 100,
  },
  modal: {
    backgroundColor: '#1a1d27',
    borderRadius: '12px',
    padding: '2rem',
    width: '100%',
    maxWidth: '460px',
    boxShadow: '0 4px 24px rgba(0,0,0,0.5)',
  },
  title: {
    color: '#ffffff',
    marginTop: 0,
    marginBottom: '1.5rem',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
  },
  fieldGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.3rem',
  },
  label: {
    color: '#8b8fa8',
    fontSize: '0.85rem',
  },
  input: {
    backgroundColor: '#252836',
    border: '1px solid #333650',
    borderRadius: '6px',
    padding: '0.65rem 0.9rem',
    color: '#ffffff',
    fontSize: '0.95rem',
    outline: 'none',
  },
  buttons: {
    display: 'flex',
    justifyContent: 'flex-end',
    gap: '0.75rem',
    marginTop: '0.5rem',
  },
  cancelBtn: {
    backgroundColor: '#2a2d3e',
    color: '#a0a4c0',
    border: 'none',
    borderRadius: '6px',
    padding: '0.65rem 1.25rem',
    cursor: 'pointer',
  },
  saveBtn: {
    backgroundColor: '#4f6ef7',
    color: '#ffffff',
    border: 'none',
    borderRadius: '6px',
    padding: '0.65rem 1.25rem',
    cursor: 'pointer',
    fontWeight: '600',
  },
};