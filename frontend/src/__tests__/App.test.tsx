import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import App from '../App';

// Mock the FrontendUI component
jest.mock('../components/FrontendUI', () => {
    return function MockFrontendUI() {
        return <div data-testid="frontend-ui">Mock Frontend UI</div>;
    };
});

// Mock the ErrorBoundary component
jest.mock('../components/ErrorBoundary', () => {
    return function MockErrorBoundary({ children }: { children: React.ReactNode }) {
        return <div data-testid="error-boundary">{children}</div>;
    };
});

describe('App', () => {
    it('renders without crashing', () => {
        render(
            <BrowserRouter>
                <App />
            </BrowserRouter>
        );

        expect(screen.getByTestId('error-boundary')).toBeInTheDocument();
        expect(screen.getByTestId('frontend-ui')).toBeInTheDocument();
    });

    it('renders the main heading', () => {
        render(
            <BrowserRouter>
                <App />
            </BrowserRouter>
        );

        expect(screen.getByText('Mock Frontend UI')).toBeInTheDocument();
    });

    it('wraps FrontendUI with ErrorBoundary', () => {
        render(
            <BrowserRouter>
                <App />
            </BrowserRouter>
        );

        const errorBoundary = screen.getByTestId('error-boundary');
        const frontendUI = screen.getByTestId('frontend-ui');

        expect(errorBoundary).toContainElement(frontendUI);
    });
}); 