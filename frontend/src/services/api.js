import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL;

const api = axios.create({
  // Default to same-origin requests so the SPA works on Render without extra env config
  baseURL: API_URL || '/',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const createSession = async (title, language = 'python') => {
  const response = await api.post('/api/sessions', {
    title,
    language,
  });
  return response.data;
};

export const getSession = async (sessionCode) => {
  const response = await api.get(`/api/sessions/${sessionCode}`);
  return response.data;
};

export default api;

