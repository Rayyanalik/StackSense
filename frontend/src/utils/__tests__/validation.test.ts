import { validateProjectDescription } from '../validation';

describe('validateProjectDescription', () => {
    it('validates a correct project description', () => {
        const validDescription = {
            description: 'A web application with real-time updates',
            requirements: ['user authentication', 'database storage'],
            constraints: ['budget-friendly', 'quick to deploy']
        };

        const result = validateProjectDescription(validDescription);
        expect(result.isValid).toBe(true);
        expect(result.errors).toHaveLength(0);
    });

    it('validates empty description', () => {
        const emptyDescription = {
            description: '',
            requirements: [],
            constraints: []
        };

        const result = validateProjectDescription(emptyDescription);
        expect(result.isValid).toBe(false);
        expect(result.errors).toContain('Project description is required');
    });

    it('validates description length', () => {
        const shortDescription = {
            description: 'test',
            requirements: [],
            constraints: []
        };

        const result = validateProjectDescription(shortDescription);
        expect(result.isValid).toBe(false);
        expect(result.errors).toContain('Project description must be at least 10 characters long');
    });

    it('validates description with special characters', () => {
        const descriptionWithSpecialChars = {
            description: 'A web app with <script>alert("xss")</script>',
            requirements: [],
            constraints: []
        };

        const result = validateProjectDescription(descriptionWithSpecialChars);
        expect(result.isValid).toBe(false);
        expect(result.errors).toContain('Project description contains invalid characters');
    });

    it('validates requirements array', () => {
        const descriptionWithInvalidRequirements = {
            description: 'A web application with real-time updates',
            requirements: ['', '   '],
            constraints: []
        };

        const result = validateProjectDescription(descriptionWithInvalidRequirements);
        expect(result.isValid).toBe(false);
        expect(result.errors).toContain('Requirements cannot be empty strings');
    });

    it('validates constraints array', () => {
        const descriptionWithInvalidConstraints = {
            description: 'A web application with real-time updates',
            requirements: [],
            constraints: ['', '   ']
        };

        const result = validateProjectDescription(descriptionWithInvalidConstraints);
        expect(result.isValid).toBe(false);
        expect(result.errors).toContain('Constraints cannot be empty strings');
    });

    it('validates maximum length of arrays', () => {
        const descriptionWithLongArrays = {
            description: 'A web application with real-time updates',
            requirements: Array(11).fill('requirement'),
            constraints: Array(11).fill('constraint')
        };

        const result = validateProjectDescription(descriptionWithLongArrays);
        expect(result.isValid).toBe(false);
        expect(result.errors).toContain('Maximum 10 requirements allowed');
        expect(result.errors).toContain('Maximum 10 constraints allowed');
    });

    it('validates description maximum length', () => {
        const longDescription = {
            description: 'A'.repeat(1001),
            requirements: [],
            constraints: []
        };

        const result = validateProjectDescription(longDescription);
        expect(result.isValid).toBe(false);
        expect(result.errors).toContain('Project description must not exceed 1000 characters');
    });

    it('validates individual requirement and constraint lengths', () => {
        const descriptionWithLongItems = {
            description: 'A web application with real-time updates',
            requirements: ['A'.repeat(101)],
            constraints: ['A'.repeat(101)]
        };

        const result = validateProjectDescription(descriptionWithLongItems);
        expect(result.isValid).toBe(false);
        expect(result.errors).toContain('Each requirement must not exceed 100 characters');
        expect(result.errors).toContain('Each constraint must not exceed 100 characters');
    });
}); 