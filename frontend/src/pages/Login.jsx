import { useState } from 'react';
import { login } from '../services/api';

export default function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const data = await login(username, password);
      localStorage.setItem('token', data.access_token);
      onLogin();
    } catch (err) {
      setError('Invalid username or password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>🔐 SecureVault</h1>
        <p style={styles.subtitle}>Enter your master password to unlock your vault</p>
        {error && <div style={styles.error}>{error}</div>}
        <form onSubmit={handleSubmit} style={styles.form}>
          <input
            style={styles.input}
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            autoComplete="username"
          />
          <input
            style={styles.input}
            type="password"
            placeholder="Master Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="current-password"
          />
          <button style={styles.button} type="submit" disabled={loading}>
            {loading ? 'Unlocking...' : 'Unlock Vault'}
          </button>
        </form>
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#0f1117',
  },
  card: {
    backgroundColor: '#1a1d27',
    padding: '2.5rem',
    borderRadius: '12px',
    width: '100%',
    maxWidth: '400px',
    boxShadow: '0 4px 24px rgba(0,0,0,0.4)',
  },
  title: {
    color: '#ffffff',
    margin: '0 0 0.5rem',
    fontSize: '1.8rem',
    textAlign: 'center',
  },
  subtitle: {
    color: '#8b8fa8',
    textAlign: 'center',
    marginBottom: '1.5rem',
    fontSize: '0.9rem',
  },
  error: {
    backgroundColor: '#3d1a1a',
    color: '#ff6b6b',
    padding: '0.75rem',
    borderRadius: '6px',
    marginBottom: '1rem',
    fontSize: '0.9rem',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
  },
  input: {
    backgroundColor: '#252836',
    border: '1px solid #333650',
    borderRadius: '6px',
    padding: '0.75rem 1rem',
    color: '#ffffff',
    fontSize: '1rem',
    outline: 'none',
  },
  button: {
    backgroundColor: '#4f6ef7',
    color: '#ffffff',
    border: 'none',
    borderRadius: '6px',
    padding: '0.75rem',
    fontSize: '1rem',
    cursor: 'pointer',
    fontWeight: '600',
  },
};