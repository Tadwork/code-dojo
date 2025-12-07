import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
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

