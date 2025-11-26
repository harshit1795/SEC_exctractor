'use client';

interface LoadingProps {
  message?: string;
  size?: 'sm' | 'md' | 'lg';
}

export function Loading({ message = 'Loading...', size = 'md' }: LoadingProps) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  };

  return (
    <div className="flex flex-col items-center justify-center p-8">
      <div
        className={`${sizeClasses[size]} animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent`}
      ></div>
      {message && <p className="mt-4 text-gray-600">{message}</p>}
    </div>
  );
}

