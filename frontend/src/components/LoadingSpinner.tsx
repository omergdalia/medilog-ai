
import React from 'react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  color?: string; // Tailwind color class e.g., text-blue-500
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ size = 'md', color = 'text-indigo-600' }) => {
  const sizeClasses = {
    sm: 'w-5 h-5 border-2',
    md: 'w-8 h-8 border-4',
    lg: 'w-12 h-12 border-[6px]',
  };

  return (
    <div className={`animate-spin rounded-full ${sizeClasses[size]} border-t-transparent ${color}`}
         style={{ borderTopColor: 'transparent' }} // Ensure this style for the transparent part
    ></div>
  );
};
    