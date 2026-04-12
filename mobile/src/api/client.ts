import axios from 'axios';
import { BASE_URL, TIMEOUT } from './config';

const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para adicionar o token se disponível (exemplo futuro)
// apiClient.interceptors.request.use((config) => {
//   const token = localStorage.getItem('token'); // No mobile seria AsyncStorage
//   if (token) {
//     config.headers.Authorization = `Token ${token}`;
//   }
//   return config;
// });

export default apiClient;
