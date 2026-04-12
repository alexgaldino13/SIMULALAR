import apiClient from './client';

export const authService = {
  login: async (username: any, password: any) => {
    try {
      const response = await apiClient.post('/api-token-auth/', {
        username,
        password,
      });
      return response.data; // { token: '...' }
    } catch (error: any) {
      console.error('Erro no login:', error.response?.data || error.message);
      throw error;
    }
  },

  register: async (userData: any) => {
    try {
      const response = await apiClient.post('/api/v1/register/', userData);
      return response.data; // { token: '...', user_id: ... }
    } catch (error: any) {
      console.error('Erro no cadastro:', error.response?.data || error.message);
      throw error;
    }
  },

  getDashboardData: async () => {
    const response = await apiClient.get('/api/v1/dashboard/');
    return response.data;
  },

  saveSimulation: async (simulationData: any) => {
    const response = await apiClient.post('/api/v1/simulation/save/', simulationData);
    return response.data;
  },

  deleteSimulation: async (id: number) => {
    await apiClient.delete(`/api/v1/simulation/${id}/delete/`);
  }
};
