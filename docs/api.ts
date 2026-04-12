import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_URL = 'http://10.0.2.2:8000'; // IP padrão do emulador Android para acessar o localhost do PC

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para adicionar o token de autenticação em todas as chamadas
api.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem('@ImobCalc:token');
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

export const authService = {
  login: (credentials: any) => api.post('/api/auth/login/', credentials),
  getProfile: () => api.get('/api/usuario/perfil/'),
};

export const simulationService = {
  calculate: (data: any) => api.post('/api/wizard/calcular/', data),
  save: (data: any) => api.post('/api/simulacoes/salvar/', data),
};

export default api;