import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import FrontendUI from '../FrontendUI';
import { techStackApi } from '../../api/techStackApi';

// Mock the API
jest.mock('../../api/techStackApi');

describe('FrontendUI Component', () => {
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

    beforeEach(() => {
        // Reset all mocks before each test
        jest.clearAllMocks();
    });

    it('renders the initial state correctly', () => {
        render(<FrontendUI />);
        
        // Check for main elements
        expect(screen.getByText('Get the perfect')).toBeInTheDocument();
        expect(screen.getByText('Tech Stack')).toBeInTheDocument();
        expect(screen.getByPlaceholderText(' ')).toBeInTheDocument();
        expect(screen.getByText('Get Recommendations')).toBeInTheDocument();
    });

    it('handles user input correctly', async () => {
        render(<FrontendUI />);
        
        const textarea = screen.getByPlaceholderText(' ');
        await userEvent.type(textarea, 'I need a web application');
        
        expect(textarea).toHaveValue('I need a web application');
    });

    it('shows loading state when submitting', async () => {
        // Mock the API call to delay
        (techStackApi.getRecommendation as jest.Mock).mockImplementation(
            () => new Promise(resolve => setTimeout(() => resolve(mockRecommendation), 100))
        );

        render(<FrontendUI />);
        
        const textarea = screen.getByPlaceholderText(' ');
        const submitButton = screen.getByText('Get Recommendations');
        
        await userEvent.type(textarea, 'Test project');
        fireEvent.click(submitButton);
        
        // Check loading state
        expect(screen.getByText('Analyzing...')).toBeInTheDocument();
        expect(submitButton).toBeDisabled();
    });

    it('displays recommendations after successful API call', async () => {
        (techStackApi.getRecommendation as jest.Mock).mockResolvedValue(mockRecommendation);

        render(<FrontendUI />);
        
        const textarea = screen.getByPlaceholderText(' ');
        const submitButton = screen.getByText('Get Recommendations');
        
        await userEvent.type(textarea, 'Test project');
        fireEvent.click(submitButton);
        
        // Wait for recommendations to appear
        await waitFor(() => {
            expect(screen.getByText('Recommended Stack')).toBeInTheDocument();
        });
        
        // Check if all recommendation elements are displayed
        mockRecommendation.primary_stack.forEach(tech => {
            expect(screen.getByText(tech)).toBeInTheDocument();
        });
        
        mockRecommendation.alternatives.forEach(tech => {
            expect(screen.getByText(tech)).toBeInTheDocument();
        });
        
        expect(screen.getByText(mockRecommendation.explanation)).toBeInTheDocument();
    });

    it('handles API errors correctly', async () => {
        (techStackApi.getRecommendation as jest.Mock).mockRejectedValue(
            new Error('API Error')
        );

        render(<FrontendUI />);
        
        const textarea = screen.getByPlaceholderText(' ');
        const submitButton = screen.getByText('Get Recommendations');
        
        await userEvent.type(textarea, 'Test project');
        fireEvent.click(submitButton);
        
        // Wait for error message
        await waitFor(() => {
            expect(screen.getByText('Failed to get recommendations. Please try again.')).toBeInTheDocument();
        });
    });

    it('resets the form correctly', async () => {
        (techStackApi.getRecommendation as jest.Mock).mockResolvedValue(mockRecommendation);

        render(<FrontendUI />);
        
        // Fill and submit the form
        const textarea = screen.getByPlaceholderText(' ');
        const submitButton = screen.getByText('Get Recommendations');
        
        await userEvent.type(textarea, 'Test project');
        fireEvent.click(submitButton);
        
        // Wait for recommendations
        await waitFor(() => {
            expect(screen.getByText('Recommended Stack')).toBeInTheDocument();
        });
        
        // Click reset button
        const resetButton = screen.getByText('Try Another Project');
        fireEvent.click(resetButton);
        
        // Check if form is reset
        expect(textarea).toHaveValue('');
        expect(screen.queryByText('Recommended Stack')).not.toBeInTheDocument();
    });

    it('handles keyboard shortcuts correctly', async () => {
        (techStackApi.getRecommendation as jest.Mock).mockResolvedValue(mockRecommendation);

        render(<FrontendUI />);
        
        const textarea = screen.getByPlaceholderText(' ');
        await userEvent.type(textarea, 'Test project');
        
        // Simulate Cmd+Enter
        fireEvent.keyDown(textarea, { key: 'Enter', metaKey: true });
        
        // Wait for recommendations
        await waitFor(() => {
            expect(screen.getByText('Recommended Stack')).toBeInTheDocument();
        });
    });
}); 