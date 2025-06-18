import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ErrorBoundary from '../ErrorBoundary';

// Component that throws an error
const ThrowError = () => {
    throw new Error('Test error');
};

// Custom fallback component
const CustomFallback = () => (
    <div data-testid="custom-fallback">Custom Error Fallback</div>
);

describe('ErrorBoundary', () => {
    beforeEach(() => {
        // Suppress console.error for expected errors
        jest.spyOn(console, 'error').mockImplementation(() => {});
    });

    afterEach(() => {
        jest.restoreAllMocks();
    });

    it('renders children when there is no error', () => {
        render(
            <ErrorBoundary>
                <div data-testid="test-child">Test Child</div>
            </ErrorBoundary>
        );

        expect(screen.getByTestId('test-child')).toBeInTheDocument();
    });

    it('renders error UI when child component throws', () => {
        render(
            <ErrorBoundary>
                <ThrowError />
            </ErrorBoundary>
        );

        expect(screen.getByText('Oops! Something went wrong')).toBeInTheDocument();
        expect(screen.getByText('Test error')).toBeInTheDocument();
        expect(screen.getByText('Try Again')).toBeInTheDocument();
    });

    it('renders custom fallback when provided', () => {
        render(
            <ErrorBoundary fallback={<CustomFallback />}>
                <ThrowError />
            </ErrorBoundary>
        );

        expect(screen.getByTestId('custom-fallback')).toBeInTheDocument();
    });

    it('resets error state when Try Again is clicked', () => {
        const { rerender } = render(
            <ErrorBoundary>
                <ThrowError />
            </ErrorBoundary>
        );

        // Verify error state
        expect(screen.getByText('Oops! Something went wrong')).toBeInTheDocument();

        // Click Try Again
        fireEvent.click(screen.getByText('Try Again'));

        // Rerender with non-error component
        rerender(
            <ErrorBoundary>
                <div data-testid="test-child">Test Child</div>
            </ErrorBoundary>
        );

        // Verify error state is reset
        expect(screen.getByTestId('test-child')).toBeInTheDocument();
        expect(screen.queryByText('Oops! Something went wrong')).not.toBeInTheDocument();
    });

    it('shows error stack trace in development mode', () => {
        const originalNodeEnv = process.env.NODE_ENV;
        process.env.NODE_ENV = 'development';

        render(
            <ErrorBoundary>
                <ThrowError />
            </ErrorBoundary>
        );

        // Verify error stack trace is shown
        expect(screen.getByText(/at ThrowError/)).toBeInTheDocument();

        // Restore original NODE_ENV
        process.env.NODE_ENV = originalNodeEnv;
    });

    it('hides error stack trace in production mode', () => {
        const originalNodeEnv = process.env.NODE_ENV;
        process.env.NODE_ENV = 'production';

        render(
            <ErrorBoundary>
                <ThrowError />
            </ErrorBoundary>
        );

        // Verify error stack trace is not shown
        expect(screen.queryByText(/at ThrowError/)).not.toBeInTheDocument();

        // Restore original NODE_ENV
        process.env.NODE_ENV = originalNodeEnv;
    });

    it('logs error to console', () => {
        const consoleSpy = jest.spyOn(console, 'error');
        
        render(
            <ErrorBoundary>
                <ThrowError />
            </ErrorBoundary>
        );

        expect(consoleSpy).toHaveBeenCalledWith(
            'Uncaught error:',
            expect.any(Error),
            expect.any(Object)
        );
    });
}); 