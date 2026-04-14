import axios from 'axios';

const API_URL = 'http://localhost:8001';

const api = axios.create({
  baseURL: API_URL,
});

// Automatically attach token to every request if it exists
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth
export const login = async (username, password) => {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);
  formData.append('grant_type', 'password');

  const response = await api.post('/auth/login', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  });
  return response.data;
};

// Vault
export const getEntries = async () => {
  const response = await api.get('/vault');
  return response.data;
};

export const createEntry = async (entry) => {
  const response = await api.post('/vault', entry);
  return response.data;
};

export const updateEntry = async (id, entry) => {
  const response = await api.put(`/vault/${id}`, entry);
  return response.data;
};

export const deleteEntry = async (id) => {
  const response = await api.delete(`/vault/${id}`);
  return response.data;
};