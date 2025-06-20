import React, { useState, useEffect, useCallback, useReducer, useRef } from 'react';
import { Send, Loader2, Code, Lightbulb, Sparkles, Github } from 'lucide-react';
import AnimatedPlaceholder from './AnimatedPlaceholder';
import { techStackApi, ProjectDescription, TechStackRecommendation, SimilarProject } from '../api/techStackApi';
import { useInfiniteScroll } from '../hooks/useInfiniteScroll';

// --- State Management ---
interface State {
  loading: boolean;
  error: string | null;
  recommendation: TechStackRecommendation | null;
}

type Action =
  | { type: 'FETCH_START' }
  | { type: 'FETCH_SUCCESS'; payload: TechStackRecommendation }
  | { type: 'FETCH_ERROR'; payload: string }
  | { type: 'RESET' };

const initialState: State = {
  loading: false,
  error: null,
  recommendation: null,
};

const recommendationReducer = (state: State, action: Action): State => {
  switch (action.type) {
    case 'FETCH_START':
      return { ...initialState, loading: true };
    case 'FETCH_SUCCESS':
      return { ...state, loading: false, recommendation: action.payload };
    case 'FETCH_ERROR':
      return { ...state, loading: false, error: action.payload };
    case 'RESET':
      return initialState;
    default:
      throw new Error(`Unhandled action type`);
  }
};

// --- Interfaces & Components ---
interface Particle {
  id: number;
  x: number;
  y: number;
  size: number;
  duration: number;
  delay: number;
}

// --- Main Component ---
export const FrontendUI: React.FC = () => {
  const [description, setDescription] = useState('');
  const [state, dispatch] = useReducer(recommendationReducer, initialState);
  const { loading, error, recommendation } = state;
  const abortControllerRef = useRef<AbortController | null>(null);

  const [similarProjects, setSimilarProjects] = useState<SimilarProject[]>([]);
  const [particles, setParticles] = useState<Particle[]>([]);
  const [page, setPage] = useState(1);
  const [hasMoreProjects, setHasMoreProjects] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);

  useEffect(() => {
    // Generate floating particles on mount
    const newParticles: Particle[] = Array.from({ length: 50 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: Math.random() * 3 + 1,
      duration: Math.random() * 20 + 10,
      delay: Math.random() * 5,
    }));
    setParticles(newParticles);
  }, []);

  const handleDescriptionChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setDescription(e.target.value);
    // If a request is in-flight while the user is typing, abort it.
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
      // Reset the state from 'loading'
      dispatch({ type: 'RESET' });
    }
  };

  const handleSubmit = useCallback(async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!description.trim()) return;

    const controller = new AbortController();
    abortControllerRef.current = controller;

    dispatch({ type: 'FETCH_START' });

    try {
      const result = await techStackApi.getRecommendation(
        {
          description,
          requirements: [],
          constraints: {},
        },
        controller.signal // Pass the signal
      );
      dispatch({ type: 'FETCH_SUCCESS', payload: result });
    } catch (err: any) {
      // Don't show an error message if the request was intentionally aborted
      if (err.name === 'AbortError' || err.code === 'ERR_CANCELED') {
        console.log('Fetch successfully aborted.');
      } else {
        dispatch({ type: 'FETCH_ERROR', payload: err.message || 'An unknown error occurred.' });
      }
    } finally {
      // This request is done, so clear the controller ref.
      if (abortControllerRef.current === controller) {
        abortControllerRef.current = null;
      }
    }
  }, [description]);

  useEffect(() => {
    if (recommendation) {
      setSimilarProjects(recommendation.similar_projects.slice(0, 3));
      setHasMoreProjects(recommendation.similar_projects.length > 3);
      setPage(1); // Reset page for new recommendations
    }
  }, [recommendation]);

  const loadMoreProjects = useCallback(() => {
    if (!recommendation || loadingMore || !hasMoreProjects) return;
    setLoadingMore(true);
    const nextPage = page + 1;
    const newProjects = recommendation.similar_projects.slice(0, nextPage * 3);
    setSimilarProjects(newProjects);
    setPage(nextPage);
    if (newProjects.length >= recommendation.similar_projects.length) {
      setHasMoreProjects(false);
    }
    setLoadingMore(false);
  }, [recommendation, page, loadingMore, hasMoreProjects]);

  const lastProjectRef = useInfiniteScroll({
    onLoadMore: loadMoreProjects,
    hasMore: hasMoreProjects,
    loading: loadingMore,
  });

  const getAllTechnologies = (project: any) => {
    if (Array.isArray(project.technologies)) return project.technologies;
    return [
      ...(project.frontend || []),
      ...(project.backend || []),
      ...(project.database || []),
      ...(project.devops || []),
    ];
  };

  const renderRecommendation = () => {
    if (!recommendation) return null;

    const hasAlternatives = recommendation.alternatives && Object.keys(recommendation.alternatives).length > 0;
    const hasSimilarProjects = similarProjects && similarProjects.length > 0;
    const hasDetailedExplanation = recommendation.detailed_explanation;

    const detailCards = [];

    if (hasDetailedExplanation) {
      detailCards.push(
        <div key="justification" className="bg-gray-900/80 border border-gray-700/50 rounded-xl p-6 glass">
          <h3 className="text-xl font-semibold mb-4 text-white flex items-center">
            <Lightbulb className="h-5 w-5 mr-3 text-yellow-400" />
            Detailed Justification
          </h3>
          <p className="text-gray-400 whitespace-pre-line leading-relaxed">{recommendation.detailed_explanation}</p>
        </div>
      );
    }

    if (hasSimilarProjects) {
      detailCards.push(
        <div key="similar-projects" className="bg-gray-900/80 border border-gray-700/50 rounded-xl p-6 glass">
          <h3 className="text-xl font-semibold mb-4 text-white flex items-center">
            <Github className="h-5 w-5 mr-3 text-gray-400" />
            Similar Projects
          </h3>
          <div className="space-y-4">
            {similarProjects.map((project, index) => (
              <div key={index} ref={index === similarProjects.length - 1 ? lastProjectRef : null} className="border-b border-gray-700/50 pb-4 last:border-b-0">
                <h4 className="font-medium mb-2 text-white">{project.name}</h4>
                <p className="text-gray-400 text-sm mb-3">{project.description}</p>
                {project.metadata && project.metadata.url && (
                  <a href={project.metadata.url} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300 transition-colors duration-200 underline text-xs mb-3 inline-block">View on GitHub</a>
                )}
                <div className="flex flex-wrap gap-2">
                  {getAllTechnologies(project).map((tech: string, techIndex: number) => (
                    <span key={techIndex} className="px-2 py-1 bg-gray-800/60 text-gray-300 rounded-md text-xs border border-gray-700/50">{tech}</span>
                  ))}
                </div>
              </div>
            ))}
            {loadingMore && <div className="flex justify-center py-4"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" /></div>}
          </div>
        </div>
      );
    }

    if (hasAlternatives) {
      detailCards.push(
        <div key="alternatives" className="bg-gray-900/80 border border-gray-700/50 rounded-xl p-6 glass">
          <h3 className="text-xl font-semibold mb-4 text-white">Alternative Options</h3>
          <ul>
            {Object.entries(recommendation.alternatives).map(([category, techs]) => (
              <li key={category} className="mb-1">
                <span className="font-semibold capitalize">{category}:</span> {Array.isArray(techs) ? techs.map((t: any) => t.name).join(', ') : ''}
              </li>
            ))}
          </ul>
        </div>
      );
    }

    return (
      <div className="space-y-6">
        {/* Recommended Tech Stack Card (Always full width) */}
        <div className="bg-gray-900/80 border border-gray-700/50 rounded-xl p-6 glass">
            <h2 className="text-2xl font-bold mb-4 text-white">Recommended Tech Stack</h2>
            <div className="flex flex-wrap gap-2 mb-4">
                {recommendation.primary_tech_stack.map((tech: any, idx: number) => (
                    <div key={idx} className="bg-gray-800/60 border border-gray-700/50 rounded-lg px-3 py-1.5 text-sm">
                    <span className="font-semibold text-blue-300 capitalize">{tech.category}: </span>
                    <span className="text-gray-200">{tech.name}</span>
                    </div>
                ))}
            </div>
            <p className="text-gray-400 whitespace-pre-line">{recommendation.explanation}</p>
        </div>

        {/* Vertical layout for all additional cards */}
        {detailCards.length > 0 && (
          <div className="space-y-6">
            {detailCards.map((card) => card)}
          </div>
        )}
      </div>
    );
  };
  
  return (
    <div className="min-h-screen bg-black text-white relative overflow-hidden">
      {/* Background elements */}
      <div className="absolute inset-0 grid-pattern opacity-20"></div>
      <div className="absolute inset-0 gradient-bg"></div>
      {particles.map((particle) => (
        <div
          key={particle.id}
          className="absolute w-1 h-1 bg-blue-500 rounded-full animate-float"
          style={{
            left: `${particle.x}%`,
            top: `${particle.y}%`,
            animationDuration: `${particle.duration}s`,
            animationDelay: `${particle.delay}s`,
            opacity: 0.3
          }}
        />
      ))}

      {/* Header */}
      <header className="relative z-10 py-6 px-8 flex justify-between items-center">
        <div className="flex items-center space-x-4">
          <Code className="h-8 w-8 text-blue-500 animate-spin-slow" />
          <h1 className="text-2xl font-bold text-gradient">StackSense</h1>
        </div>
        <a
          href="https://github.com/Rayyanalik/StackSense.git"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center space-x-2 text-gray-400 hover:text-white transition-colors duration-300"
        >
          <Github className="h-6 w-6" />
          <span>GitHub</span>
        </a>
      </header>

      {/* Main Content */}
      <main className="relative z-10 container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12 animate-fade-in">
            <div className="inline-flex items-center px-3 py-1 bg-blue-900/30 text-blue-300 rounded-full text-sm mb-6 border border-blue-800/30 glass animate-glow">
              <Sparkles className="h-3 w-3 mr-1 animate-spin-slow" />
              Introducing StackSense
            </div>
            <h1 className="text-5xl font-bold mb-6 leading-tight animate-slide-up">
              Get the perfect{' '}
              <span className="text-gradient animate-gradient">
                Tech Stack
              </span>
            </h1>
            <p className="text-xl text-gray-400 mb-12 animate-fade-in" style={{animationDelay: '0.3s'}}>
              Describe your project idea and get AI-powered technology stack recommendations tailored to your needs.
            </p>
          </div>

          <div className="space-y-6 animate-fade-in" style={{animationDelay: '0.6s'}}>
            <div className="relative group max-w-2xl mx-auto">
              <div className="relative">
                <label htmlFor="project-description" className="sr-only">Project Description</label>
                <textarea
                  id="project-description"
                  value={description}
                  onChange={handleDescriptionChange}
                  placeholder=" "
                  className="relative w-full h-24 bg-gray-900/80 border border-gray-700/50 rounded-xl px-4 py-3 text-white placeholder-gray-500 resize-none focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 transition-all duration-300 glass hover:bg-gray-900/90 focus:bg-gray-900/95"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                      handleSubmit(e);
                    }
                  }}
                />
                {!description && !loading && (
                  <AnimatedPlaceholder
                    texts={[
                      "I need a tech stack for a real-time chat application...",
                      "Looking for a stack to build a data analytics dashboard...",
                      "What's the best stack for a machine learning project?",
                      "Need recommendations for a scalable e-commerce platform...",
                      "What stack should I use for a mobile-first web app?"
                    ]}
                    className="absolute top-4 left-4 text-gray-500 pointer-events-none"
                  />
                )}
              </div>
            </div>

            <div className="flex justify-center">
              <button
                onClick={handleSubmit}
                disabled={!description.trim() || loading}
                className="relative inline-flex items-center px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-medium rounded-xl hover:from-blue-500 hover:to-purple-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 hover:shadow-2xl hover:shadow-blue-500/25 hover:scale-105 group overflow-hidden"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-purple-400 opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    <span className="animate-pulse">Analyzing...</span>
                  </>
                ) : (
                  <>
                    <Send className="h-4 w-4 mr-2 group-hover:translate-x-1 transition-transform duration-300" />
                    Get Recommendations
                  </>
                )}
              </button>
            </div>
            
            {loading && (
              <p className="text-gray-400 text-lg text-center animate-pulse" style={{animationDelay: '1.2s'}}>
                StackSense is thinking... please hang on.
              </p>
            )}

            <p className="text-gray-500 text-sm text-center animate-fade-in" style={{animationDelay: '0.9s'}}>
              Press Cmd+Enter to submit
            </p>
          </div>

          <div className="mt-12">
            {!loading && recommendation && renderRecommendation()}
          </div>

          {error && (
            <div className="mt-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 animate-fade-in">
              {error}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};