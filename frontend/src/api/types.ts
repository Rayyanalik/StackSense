export interface ProjectDescription {
    description: string;
    requirements: string[];
    constraints: string[];
}

export interface TechStackRecommendation {
    primary_stack: string[];
    alternatives: string[];
    explanation: string;
    confidence: number;
    similar_projects: {
        name: string;
        description: string;
        technologies: string[];
        metadata: Record<string, any>;
    }[];
} 