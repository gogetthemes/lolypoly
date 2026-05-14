import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor для обработки ошибок
client.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Accounts API
export const accountsAPI = {
  getList: () => client.get('/accounts'),
  getById: (id) => client.get(`/accounts/${id}`),
  create: (data) => client.post('/accounts', data),
  update: (id, data) => client.put(`/accounts/${id}`, data),
  delete: (id) => client.delete(`/accounts/${id}`),
  testConnection: (id) => client.post(`/accounts/${id}/test`),
};

// Strategies API
export const strategiesAPI = {
  getList: () => client.get('/strategies'),
  getById: (id) => client.get(`/strategies/${id}`),
  create: (data) => client.post('/strategies', data),
  update: (id, data) => client.put(`/strategies/${id}`, data),
  delete: (id) => client.delete(`/strategies/${id}`),
  toggle: (id) => client.post(`/strategies/${id}/toggle`),
};

// Trades API
export const tradesAPI = {
  getList: (filters) => client.get('/trades', { params: filters }),
  getStats: () => client.get('/trades/stats'),
  getAccountStats: (accountId) => client.get(`/trades/stats/${accountId}`),
  getPairStats: () => client.get('/trades/pairs'),
};

// Bot Status API
export const botAPI = {
  getStatus: () => client.get('/status'),
  start: () => client.post('/bot/start'),
  stop: () => client.post('/bot/stop'),
  restart: () => client.post('/bot/restart'),
  getSettings: () => client.get('/settings'),
  updateSettings: (data) => client.put('/settings', data),
};

export default client;
