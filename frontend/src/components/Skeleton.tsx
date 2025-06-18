import React from 'react';

interface SkeletonProps {
  className?: string;
  width?: string | number;
  height?: string | number;
  rounded?: boolean;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  className = '',
  width = '100%',
  height = '1rem',
  rounded = false
}) => {
  return (
    <div
      className={`animate-pulse bg-gray-200 ${rounded ? 'rounded-full' : 'rounded'} ${className}`}
      style={{
        width,
        height
      }}
    />
  );
};

interface SkeletonTextProps {
  lines?: number;
  className?: string;
}

export const SkeletonText: React.FC<SkeletonTextProps> = ({
  lines = 3,
  className = ''
}) => {
  return (
    <div className={`space-y-2 ${className}`}>
      {Array.from({ length: lines }).map((_, index) => (
        <Skeleton
          key={index}
          height="1rem"
          width={index === lines - 1 ? '60%' : '100%'}
        />
      ))}
    </div>
  );
};

interface SkeletonCardProps {
  className?: string;
}

export const SkeletonCard: React.FC<SkeletonCardProps> = ({
  className = ''
}) => {
  return (
    <div className={`p-4 bg-white rounded-lg shadow ${className}`}>
      <Skeleton height="1.5rem" width="60%" className="mb-4" />
      <SkeletonText lines={3} className="mb-4" />
      <div className="flex space-x-2">
        <Skeleton height="2rem" width="6rem" rounded />
        <Skeleton height="2rem" width="6rem" rounded />
      </div>
    </div>
  );
}; 