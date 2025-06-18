import { useEffect, useRef, useCallback } from 'react';

interface UseInfiniteScrollOptions {
  onLoadMore: () => void;
  hasMore: boolean;
  loading: boolean;
  threshold?: number;
}

export function useInfiniteScroll({
  onLoadMore,
  hasMore,
  loading,
  threshold = 100
}: UseInfiniteScrollOptions) {
  const observer = useRef<IntersectionObserver | null>(null);
  const lastElementRef = useCallback(
    (node: HTMLElement | null) => {
      if (loading) return;
      
      if (observer.current) {
        observer.current.disconnect();
      }
      
      observer.current = new IntersectionObserver(
        (entries) => {
          if (entries[0].isIntersecting && hasMore) {
            onLoadMore();
          }
        },
        {
          rootMargin: `${threshold}px`
        }
      );
      
      if (node) {
        observer.current.observe(node);
      }
    },
    [loading, hasMore, onLoadMore, threshold]
  );
  
  useEffect(() => {
    return () => {
      if (observer.current) {
        observer.current.disconnect();
      }
    };
  }, []);
  
  return lastElementRef;
} 