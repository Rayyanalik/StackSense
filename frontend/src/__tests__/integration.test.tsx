import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import App from '../App';
import { API_BASE_URL } from '../api/techStackApi';

// Define types for MSW
type RequestHandler = (req: any, res: any, ctx: any) => any;

// Mock API responses
const server = setupServer(
  rest.post(`${API_BASE_URL}/recommend`, ((req, res, ctx) => {
    return res(
      ctx.json({
        primary_tech_stack: ['React', 'Node.js', 'MongoDB'],
        alternatives: ['Vue.js', 'Express', 'PostgreSQL'],
        explanation: 'Based on your requirements, we recommend...',
        confidence_level: 0.85,
        similar_projects: [
          {
            name: 'Project 1',
            description: 'A similar project',
            technologies: ['React', 'Node.js'],
            metadata: { stars: 1000 }
          }
        ]
      })
    );
  }) as RequestHandler),
  rest.get(`${API_BASE_URL}/technologies`, ((req, res, ctx) => {
    return res(
      ctx.json(['React', 'Node.js', 'MongoDB', 'Vue.js', 'Express', 'PostgreSQL'])
    );
  }) as RequestHandler)
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('Frontend Integration Tests', () => {
  test('complete user flow for tech stack recommendation', async () => {
    render(<App />);
    
    // Check initial state
    expect(screen.getByText(/Get the perfect Tech Stack/i)).toBeInTheDocument();
    
    // Fill in project description
    const descriptionInput = screen.getByLabelText(/project description/i);
    await userEvent.type(descriptionInput, 'I want to build a modern web application');
    
    // Add requirements
    const addRequirementButton = screen.getByText(/add requirement/i);
    fireEvent.click(addRequirementButton);
    const requirementInput = screen.getByLabelText(/requirement 1/i);
    await userEvent.type(requirementInput, 'Scalability');
    
    // Add constraints
    const addConstraintButton = screen.getByText(/add constraint/i);
    fireEvent.click(addConstraintButton);
    const constraintInput = screen.getByLabelText(/constraint 1/i);
    await userEvent.type(constraintInput, 'Must use open-source technologies');
    
    // Submit form
    const submitButton = screen.getByRole('button', { name: /get recommendation/i });
    fireEvent.click(submitButton);
    
    // Check loading state
    expect(screen.getByText(/analyzing your project/i)).toBeInTheDocument();
    
    // Wait for recommendation
    await waitFor(() => {
      expect(screen.getByText(/recommended tech stack/i)).toBeInTheDocument();
    });
    
    // Verify recommendation display
    expect(screen.getByText('React')).toBeInTheDocument();
    expect(screen.getByText('Node.js')).toBeInTheDocument();
    expect(screen.getByText('MongoDB')).toBeInTheDocument();
    
    // Check alternatives
    expect(screen.getByText('Vue.js')).toBeInTheDocument();
    expect(screen.getByText('Express')).toBeInTheDocument();
    expect(screen.getByText('PostgreSQL')).toBeInTheDocument();
    
    // Verify similar projects
    expect(screen.getByText('Project 1')).toBeInTheDocument();
    expect(screen.getByText('A similar project')).toBeInTheDocument();
  });
  
  test('error handling in user flow', async () => {
    // Mock API error
    server.use(
      rest.post(`${API_BASE_URL}/recommend`, ((req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ error: 'Internal server error' }));
      }) as RequestHandler)
    );
    
    render(<App />);
    
    // Fill in and submit form
    const descriptionInput = screen.getByLabelText(/project description/i);
    await userEvent.type(descriptionInput, 'Test project');
    
    const submitButton = screen.getByRole('button', { name: /get recommendation/i });
    fireEvent.click(submitButton);
    
    // Check error message
    await waitFor(() => {
      expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
    });
  });
  
  test('rate limiting handling', async () => {
    // Mock rate limit response
    server.use(
      rest.post(`${API_BASE_URL}/recommend`, ((req, res, ctx) => {
        return res(
          ctx.status(429),
          ctx.json({ error: 'Too many requests. Please try again later.' })
        );
      }) as RequestHandler)
    );
    
    render(<App />);
    
    // Fill in and submit form
    const descriptionInput = screen.getByLabelText(/project description/i);
    await userEvent.type(descriptionInput, 'Test project');
    
    const submitButton = screen.getByRole('button', { name: /get recommendation/i });
    fireEvent.click(submitButton);
    
    // Check rate limit message
    await waitFor(() => {
      expect(screen.getByText(/too many requests/i)).toBeInTheDocument();
    });
  });
  
  test('form validation', async () => {
    render(<App />);
    
    // Try to submit without description
    const submitButton = screen.getByRole('button', { name: /get recommendation/i });
    fireEvent.click(submitButton);
    
    // Check validation message
    expect(screen.getByText(/description is required/i)).toBeInTheDocument();
    
    // Add too many requirements
    const addRequirementButton = screen.getByText(/add requirement/i);
    for (let i = 0; i < 6; i++) {
      fireEvent.click(addRequirementButton);
    }
    
    // Check requirement limit message
    expect(screen.getByText(/maximum 5 requirements allowed/i)).toBeInTheDocument();
  });
  
  test('copy to clipboard functionality', async () => {
    // Mock clipboard API
    Object.assign(navigator, {
      clipboard: {
        writeText: jest.fn().mockImplementation(() => Promise.resolve()),
      },
    });
    
    render(<App />);
    
    // Get recommendation first
    const descriptionInput = screen.getByLabelText(/project description/i);
    await userEvent.type(descriptionInput, 'Test project');
    
    const submitButton = screen.getByRole('button', { name: /get recommendation/i });
    fireEvent.click(submitButton);
    
    // Wait for recommendation
    await waitFor(() => {
      expect(screen.getByText(/recommended tech stack/i)).toBeInTheDocument();
    });
    
    // Click copy button
    const copyButton = screen.getByRole('button', { name: /copy/i });
    fireEvent.click(copyButton);
    
    // Verify clipboard was called
    expect(navigator.clipboard.writeText).toHaveBeenCalled();
    
    // Check success message
    expect(screen.getByText(/copied to clipboard/i)).toBeInTheDocument();
  });
}); 