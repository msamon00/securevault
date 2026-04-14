export default function EntryCard({ entry, onEdit, onDelete }) {
  return (
    <div style={styles.card}>
      <div style={styles.header}>
        <h3 style={styles.title}>{entry.title}</h3>
        <div style={styles.actions}>
          <button style={styles.editBtn} onClick={() => onEdit(entry)}>Edit</button>
          <button style={styles.deleteBtn} onClick={() => onDelete(entry.id)}>Delete</button>
        </div>
      </div>
      {entry.url && (
        <a href={entry.url} target="_blank" rel="noreferrer" style={styles.url}>
          {entry.url}
        </a>
      )}
      <div style={styles.field}>
        <span style={styles.label}>Username</span>
        <span style={styles.value}>{entry.username || '—'}</span>
      </div>
      <div style={styles.field}>
        <span style={styles.label}>Password</span>
        <span style={styles.value}>••••••••</span>
      </div>
      {entry.notes && (
        <div style={styles.field}>
          <span style={styles.label}>Notes</span>
          <span style={styles.value}>{entry.notes}</span>
        </div>
      )}
    </div>
  );
}

const styles = {
  card: {
    backgroundColor: '#1a1d27',
    borderRadius: '10px',
    padding: '1.25rem',
    border: '1px solid #2a2d3e',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '0.75rem',
  },
  title: {
    color: '#ffffff',
    margin: 0,
    fontSize: '1.1rem',
  },
  actions: {
    display: 'flex',
    gap: '0.5rem',
  },
  editBtn: {
    backgroundColor: '#2a2d3e',
    color: '#a0a4c0',
    border: 'none',
    borderRadius: '4px',
    padding: '0.3rem 0.75rem',
    cursor: 'pointer',
    fontSize: '0.85rem',
  },
  deleteBtn: {
    backgroundColor: '#3d1a1a',
    color: '#ff6b6b',
    border: 'none',
    borderRadius: '4px',
    padding: '0.3rem 0.75rem',
    cursor: 'pointer',
    fontSize: '0.85rem',
  },
  url: {
    color: '#4f6ef7',
    fontSize: '0.85rem',
    display: 'block',
    marginBottom: '0.75rem',
    textDecoration: 'none',
  },
  field: {
    display: 'flex',
    gap: '1rem',
    marginTop: '0.4rem',
  },
  label: {
    color: '#8b8fa8',
    fontSize: '0.85rem',
    minWidth: '70px',
  },
  value: {
    color: '#c8cad8',
    fontSize: '0.85rem',
  },
};