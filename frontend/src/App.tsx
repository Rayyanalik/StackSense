import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { FrontendUI } from './components/FrontendUI';
import ErrorBoundary from './components/ErrorBoundary';

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={
          <ErrorBoundary>
            <FrontendUI />
          </ErrorBoundary>
        } />
      </Routes>
    </Router>
  );
};

export default App; 