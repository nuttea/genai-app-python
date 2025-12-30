'use client';

import { useEffect } from 'react';
import { AlertCircle } from 'lucide-react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log error to Datadog
    console.error('Application error:', error);
  }, [error]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-background">
      <div className="max-w-md w-full mx-4">
        <div className="bg-card border border-border rounded-lg p-8 text-center">
          <div className="flex justify-center mb-4">
            <div className="p-4 bg-red-100 text-red-600 rounded-full">
              <AlertCircle className="w-8 h-8" />
            </div>
          </div>
          <h2 className="text-2xl font-bold text-foreground mb-2">
            Something went wrong!
          </h2>
          <p className="text-muted-foreground mb-6">
            {error.message || 'An unexpected error occurred. Please try again.'}
          </p>
          <button
            onClick={() => reset()}
            className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium"
          >
            Try again
          </button>
        </div>
      </div>
    </div>
  );
}

