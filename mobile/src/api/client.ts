import axios from 'axios';
import { BASE_URL, TIMEOUT } from './config';

let authToken: string | null = null;

export const setAuthToken = (token: string | null) => {
  authToken = token;
};

const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para adicionar o token se disponível
apiClient.interceptors.request.use((config) => {
  if (authToken) {
    config.headers.Authorization = `Token ${authToken}`;
  }
  return config;
});

export default apiClient;
