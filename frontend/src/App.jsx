import { useState } from 'react';
import Login from './pages/Login';
import Vault from './pages/Vault';

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(
    !!localStorage.getItem('token')
  );

  return isAuthenticated ? (
    <Vault onLogout={() => setIsAuthenticated(false)} />
  ) : (
    <Login onLogin={() => setIsAuthenticated(true)} />
  );
}