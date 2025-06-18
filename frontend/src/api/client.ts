import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface TechStack {
  name: string;
  description: string;
  frontend?: string[];
  backend?: string[];
  database?: string[];
  deployment?: string[];
  languages?: string[];
  frameworks?: string[];
  data_processing?: string[];
  visualization?: string[];
  services?: string[];
  use_cases: string[];
  similarity_score: number;
}

export const getRecommendations = async (description: string): Promise<TechStack[]> => {
  try {
    const response = await apiClient.post<TechStack[]>('/recommend', { description });
    return response.data;
  } catch (error) {
    console.error('Error getting recommendations:', error);
    throw error;
  }
};

export const checkHealth = async (): Promise<{ status: string }> => {
  try {
    const response = await apiClient.get<{ status: string }>('/health');
    return response.data;
  } catch (error) {
    console.error('Error checking health:', error);
    throw error;
  }
}; 