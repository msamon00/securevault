import { useState, useEffect } from 'react';
import { getEntries, createEntry, updateEntry, deleteEntry } from '../services/api';
import EntryCard from '../components/EntryCard';
import EntryForm from '../components/EntryForm';

export default function Vault({ onLogout }) {
  const [entries, setEntries] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editingEntry, setEditingEntry] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchEntries();
  }, []);

  const fetchEntries = async () => {
    try {
      const data = await getEntries();
      setEntries(data);
    } catch {
      setError('Failed to load entries.');
    }
  };

  const handleSave = async (form) => {
    try {
      if (editingEntry) {
        await updateEntry(editingEntry.id, form);
      } else {
        await createEntry(form);
      }
      setShowForm(false);
      setEditingEntry(null);
      fetchEntries();
    } catch {
      setError('Failed to save entry.');
    }
  };

  const handleEdit = (entry) => {
    setEditingEntry(entry);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this entry?')) return;
    try {
      await deleteEntry(id);
      fetchEntries();
    } catch {
      setError('Failed to delete entry.');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    onLogout();
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>🔐 SecureVault</h1>
        <div style={styles.headerActions}>
          <button style={styles.addBtn} onClick={() => { setEditingEntry(null); setShowForm(true); }}>
            + New Entry
          </button>
          <button style={styles.logoutBtn} onClick={handleLogout}>Logout</button>
        </div>
      </div>

      {error && <div style={styles.error}>{error}</div>}

      {entries.length === 0 ? (
        <div style={styles.empty}>
          <p>Your vault is empty. Add your first entry.</p>
        </div>
      ) : (
        <div style={styles.grid}>
          {entries.map((entry) => (
            <EntryCard
              key={entry.id}
              entry={entry}
              onEdit={handleEdit}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}

      {showForm && (
        <EntryForm
          entry={editingEntry}
          onSave={handleSave}
          onCancel={() => { setShowForm(false); setEditingEntry(null); }}
        />
      )}
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    backgroundColor: '#0f1117',
    padding: '2rem',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '2rem',
  },
  title: {
    color: '#ffffff',
    margin: 0,
  },
  headerActions: {
    display: 'flex',
    gap: '0.75rem',
  },
  addBtn: {
    backgroundColor: '#4f6ef7',
    color: '#ffffff',
    border: 'none',
    borderRadius: '6px',
    padding: '0.6rem 1.25rem',
    cursor: 'pointer',
    fontWeight: '600',
  },
  logoutBtn: {
    backgroundColor: '#2a2d3e',
    color: '#a0a4c0',
    border: 'none',
    borderRadius: '6px',
    padding: '0.6rem 1.25rem',
    cursor: 'pointer',
  },
  error: {
    backgroundColor: '#3d1a1a',
    color: '#ff6b6b',
    padding: '0.75rem',
    borderRadius: '6px',
    marginBottom: '1rem',
  },
  empty: {
    color: '#8b8fa8',
    textAlign: 'center',
    marginTop: '4rem',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
    gap: '1rem',
  },
};