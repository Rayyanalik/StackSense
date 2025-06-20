import axios from 'axios';

export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1/tech-stack';

export interface ProjectDescription {
    description: string;
    requirements?: string[];
    constraints?: Record<string, any>;
}

export interface SimilarProject {
    name: string;
    description: string;
    technologies: string[];
    metadata: Record<string, any>;
}

export interface TechStackRecommendation {
    primary_tech_stack: any[];
    alternatives: any;
    explanation: string;
    detailed_explanation?: string;
    confidence_level: number;
    similar_projects: SimilarProject[];
}


export interface HealthStatus {
    status: 'healthy' | 'degraded' | 'unhealthy';
    components: {
        api: {
            status: string;
            message: string;
        };
        model: {
            status: string;
            message: string;
            embedding_shape?: number[];
        };
        index: {
            status: string;
            message: string;
            dimension?: number;
        };
        system: {
            status: string;
            message: string;
            metrics?: {
                cpu_percent: number;
                memory_percent: number;
                disk_percent: number;
            };
        };
    };
}

class TechStackApi {
    private api = axios.create({
        baseURL: API_BASE_URL,
        headers: {
            'Content-Type': 'application/json',
        },
    });

    async getRecommendation(project: ProjectDescription, signal?: AbortSignal): Promise<TechStackRecommendation> {
        try {
            const response = await this.api.post<TechStackRecommendation>('/recommend', project, { signal });
            return response.data;
        } catch (error) {
            console.error('Error getting recommendation:', error);
            throw error;
        }
    }

    async checkHealth(): Promise<HealthStatus> {
        try {
            const response = await this.api.get<HealthStatus>('/health');
            return response.data;
        } catch (error) {
            console.error('Error checking health:', error);
            throw error;
        }
    }
}

export const techStackApi = new TechStackApi();