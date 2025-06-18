import React, { useState, useEffect, useCallback } from 'react';
import { Send, Loader2, Code, Lightbulb, Sparkles, Github } from 'lucide-react';
import AnimatedPlaceholder from './AnimatedPlaceholder';
import { techStackApi, ProjectDescription, TechStackRecommendation, SimilarProject } from '../api/techStackApi';
import { useDebounce } from '../hooks/useDebounce';
import { Skeleton, SkeletonText, SkeletonCard } from './Skeleton';
import { useInfiniteScroll } from '../hooks/useInfiniteScroll';

interface Particle {
  id: number;
  x: number;
  y: number;
  size: number;
  duration: number;
  delay: number;
}

// Improved dark skeleton loader with shimmer effect
const SkeletonBox: React.FC<{ className?: string }> = ({ className }) => (
  <div
    className={`relative overflow-hidden rounded-lg h-24 w-full mb-4 ${className || ''}`}
    style={{ minHeight: 96, background: 'linear-gradient(90deg, #23272f 25%, #2d323c 50%, #23272f 75%)' }}
  >
    <div className="absolute inset-0 animate-skeleton-shimmer" style={{ background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.04), transparent)' }} />
  </div>
);

// Add shimmer animation to global styles if not present
// .animate-skeleton-shimmer {
//   animation: shimmer 1.5s infinite linear;
// }
// @keyframes shimmer {
//   0% { transform: translateX(-100%); }
//   100% { transform: translateX(100%); }
// }

export const FrontendUI: React.FC = () => {
  const [description, setDescription] = useState('');
  const [requirements, setRequirements] = useState<string[]>([]);
  const [constraints, setConstraints] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [recommendation, setRecommendation] = useState<TechStackRecommendation | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [similarProjects, setSimilarProjects] = useState<SimilarProject[]>([]);
  const [hasMoreProjects, setHasMoreProjects] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [page, setPage] = useState(1);
  const [particles, setParticles] = useState<Particle[]>([]);

  // Generate floating particles
  useEffect(() => {
    const generateParticles = () => {
      const newParticles: Particle[] = [];
      for (let i = 0; i < 50; i++) {
        newParticles.push({
          id: i,
          x: Math.random() * 100,
          y: Math.random() * 100,
          size: Math.random() * 3 + 1,
          duration: Math.random() * 20 + 10,
          delay: Math.random() * 5
        });
      }
      setParticles(newParticles);
    };
    generateParticles();
  }, []);

  const debouncedGetRecommendation = useDebounce(async (description: string, requirements: string[], constraints: string[]) => {
    try {
      setLoading(true);
      setError(null);

      const recommendation = await techStackApi.getRecommendation({
        description,
        requirements,
        constraints
      });

      setRecommendation(recommendation);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, 500);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setRecommendation(null);
    try {
      const response = await fetch('http://localhost:8005/api/v1/tech-stack/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          description,
          requirements: [],
          constraints: {}
        })
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Failed to get recommendation');
      }
      const data = await response.json();
      setRecommendation(data);
    } catch (err: any) {
      setError(err.message || 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setDescription('');
    setRequirements([]);
    setConstraints([]);
    setRecommendation(null);
    setError(null);
  };

  const loadMoreProjects = useCallback(async () => {
    if (!recommendation || loadingMore) return;

    try {
      setLoadingMore(true);
      const newProjects = recommendation.similar_projects.slice(
        (page - 1) * 3,
        page * 3
      );

      if (newProjects.length === 0) {
        setHasMoreProjects(false);
        return;
      }

      setSimilarProjects(prev => [...prev, ...newProjects]);
      setPage(prev => prev + 1);
    } finally {
      setLoadingMore(false);
    }
  }, [recommendation, page, loadingMore]);

  const lastProjectRef = useInfiniteScroll({
    onLoadMore: loadMoreProjects,
    hasMore: hasMoreProjects,
    loading: loadingMore
  });

  // Reset similar projects when new recommendation is received
  useEffect(() => {
    if (recommendation) {
      setSimilarProjects(recommendation.similar_projects.slice(0, 3));
      setHasMoreProjects(recommendation.similar_projects.length > 3);
      setPage(2);
    }
  }, [recommendation]);

  const renderLoadingState = () => (
    <div className="space-y-6">
      <SkeletonCard className="mb-8" />
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <SkeletonCard />
        <SkeletonCard />
      </div>
    </div>
  );

  const getAllTechnologies = (project: any) => {
    if (Array.isArray(project.technologies)) return project.technologies;
    // fallback: combine all tech categories
    return [
      ...(project.frontend || []),
      ...(project.backend || []),
      ...(project.database || []),
      ...(project.devops || [])
    ];
  };

  const renderRecommendation = () => {
    if (!recommendation) return null;

    return (
      <div className="space-y-6">
        <div className="bg-gray-900/80 border border-gray-700/50 rounded-xl p-6 glass">
          <h2 className="text-2xl font-bold mb-4 text-white">Recommended Tech Stack</h2>
          <div className="flex flex-wrap gap-2 mb-4">
            {recommendation.primary_tech_stack && recommendation.primary_tech_stack.length > 0 ? (
              recommendation.primary_tech_stack.map((tech: any, idx: number) => (
                <li key={idx} className="mb-1">
                  <span className="font-semibold text-blue-300">{tech.category}:</span> {tech.name}
                </li>
              ))
            ) : (
              <li>No recommendation found.</li>
            )}
          </div>
          <p className="text-gray-400">{recommendation.explanation}</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-gray-900/80 border border-gray-700/50 rounded-xl p-6 glass">
            <h3 className="text-xl font-semibold mb-4 text-white">Alternative Options</h3>
            {recommendation.alternatives && Object.keys(recommendation.alternatives).length > 0 && (
              <div>
                <h3 className="text-lg font-semibold mb-1 text-blue-300">Alternatives:</h3>
                <ul>
                  {Object.entries(recommendation.alternatives).map(([category, techs]) => (
                    <li key={category} className="mb-1">
                      <span className="font-semibold">{category}:</span> {Array.isArray(techs) ? techs.map((t: any) => t.name).join(', ') : ''}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
          
          <div className="bg-gray-900/80 border border-gray-700/50 rounded-xl p-6 glass">
            <h3 className="text-xl font-semibold mb-4 text-white">Similar Projects</h3>
            <div className="space-y-4">
              {similarProjects.map((project, index) => (
                <div
                  key={index}
                  ref={index === similarProjects.length - 1 ? lastProjectRef : null}
                  className="border-b border-gray-700/50 pb-4 last:border-b-0"
                >
                  <h4 className="font-medium mb-2 text-white">{project.name}</h4>
                  <p className="text-gray-400 text-sm mb-2">{project.description}</p>
                  <div className="flex flex-wrap gap-2">
                    {getAllTechnologies(project).map((tech: string, techIndex: number) => (
                      <span
                        key={techIndex}
                        className="px-2 py-1 bg-gray-800/50 text-gray-300 rounded text-xs border border-gray-700/50"
                      >
                        {tech}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
              {loadingMore && (
                <div className="flex justify-center py-4">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-black text-white relative overflow-hidden">
      {/* Grid Pattern Background */}
      <div className="absolute inset-0 grid-pattern opacity-20"></div>
      
      {/* Gradient Background */}
      <div className="absolute inset-0 gradient-bg"></div>
      
      {/* Floating Particles */}
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
          href="https://github.com/yourusername/stacksense"
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
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 to-purple-600/20 rounded-xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              <div className="relative">
                <label htmlFor="project-description" className="sr-only">Project Description</label>
                <textarea
                  id="project-description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder=" "
                  className="relative w-full h-24 bg-gray-900/80 border border-gray-700/50 rounded-xl px-4 py-3 text-white placeholder-gray-500 resize-none focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 transition-all duration-300 glass hover:bg-gray-900/90 focus:bg-gray-900/95"
                  disabled={loading}
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
                    className="absolute top-4 left-4 text-gray-500"
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
            
            <p className="text-gray-500 text-sm text-center animate-fade-in" style={{animationDelay: '0.9s'}}>
              Press Cmd+Enter to submit
            </p>
          </div>

          {loading ? renderLoadingState() : renderRecommendation()}

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