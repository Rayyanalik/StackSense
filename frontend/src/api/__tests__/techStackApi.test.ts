import { techStackApi } from '../techStackApi';
import { ProjectDescription } from '../types';

// Mock fetch
global.fetch = jest.fn();

describe('techStackApi', () => {
    const mockRecommendation = {
        primary_stack: ['React', 'Node.js', 'MongoDB'],
        alternatives: ['Vue.js', 'Express', 'PostgreSQL'],
        explanation: 'This stack is recommended for web applications',
        confidence: 0.85,
        similar_projects: [
            {
                name: 'Sample Project',
                description: 'A sample project',
                technologies: ['React', 'Node.js'],
                metadata: {}
            }
        ]
    };

    const validDescription: ProjectDescription = {
        description: 'Test project description',
        requirements: ['web application', 'real-time updates'],
        constraints: ['budget-friendly', 'quick to deploy']
    };

    beforeEach(() => {
        // Reset all mocks before each test
        jest.clearAllMocks();
    });

    it('successfully fetches recommendations', async () => {
        // Mock successful response
        (global.fetch as jest.Mock).mockResolvedValueOnce({
            ok: true,
            json: async () => mockRecommendation
        });

        const result = await techStackApi.getRecommendation(validDescription);
        
        expect(result).toEqual(mockRecommendation);
        expect(global.fetch).toHaveBeenCalledWith(
            expect.stringContaining('/api/recommend'),
            expect.objectContaining({
                method: 'POST',
                headers: expect.objectContaining({
                    'Content-Type': 'application/json'
                }),
                body: JSON.stringify(validDescription)
            })
        );
    });

    it('handles API errors correctly', async () => {
        // Mock error response
        (global.fetch as jest.Mock).mockResolvedValueOnce({
            ok: false,
            status: 500,
            statusText: 'Internal Server Error'
        });

        await expect(techStackApi.getRecommendation(validDescription))
            .rejects
            .toThrow('Failed to get recommendation: 500 Internal Server Error');
    });

    it('handles network errors correctly', async () => {
        // Mock network error
        (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

        await expect(techStackApi.getRecommendation(validDescription))
            .rejects
            .toThrow('Network error');
    });

    it('handles invalid JSON response', async () => {
        // Mock invalid JSON response
        (global.fetch as jest.Mock).mockResolvedValueOnce({
            ok: true,
            json: async () => { throw new Error('Invalid JSON') }
        });

        await expect(techStackApi.getRecommendation(validDescription))
            .rejects
            .toThrow('Invalid JSON');
    });

    it('validates input before sending request', async () => {
        // Test empty description
        const emptyDescription: ProjectDescription = {
            description: '',
            requirements: [],
            constraints: []
        };
        await expect(techStackApi.getRecommendation(emptyDescription))
            .rejects
            .toThrow('Project description is required');

        // Test description that is too short
        const shortDescription: ProjectDescription = {
            description: 'test',
            requirements: [],
            constraints: []
        };
        await expect(techStackApi.getRecommendation(shortDescription))
            .rejects
            .toThrow('Project description must be at least 10 characters long');

        // Verify fetch was not called
        expect(global.fetch).not.toHaveBeenCalled();
    });

    it('handles rate limiting correctly', async () => {
        // Mock rate limit response
        (global.fetch as jest.Mock).mockResolvedValueOnce({
            ok: false,
            status: 429,
            statusText: 'Too Many Requests'
        });

        await expect(techStackApi.getRecommendation(validDescription))
            .rejects
            .toThrow('Rate limit exceeded. Please try again later.');
    });

    it('handles timeout correctly', async () => {
        // Mock timeout
        (global.fetch as jest.Mock).mockImplementationOnce(() => 
            new Promise((_, reject) => 
                setTimeout(() => reject(new Error('Timeout')), 10000)
            )
        );

        await expect(techStackApi.getRecommendation(validDescription))
            .rejects
            .toThrow('Request timed out');
    });
}); 