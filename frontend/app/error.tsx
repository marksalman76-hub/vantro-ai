'use client';

import { useEffect } from 'react';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('[Vantro] Unhandled error:', error);
  }, [error]);

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center p-8">
      <div className="max-w-md w-full text-center">
        <div className="w-16 h-16 rounded-2xl bg-red-500/10 border border-red-500/20 flex items-center justify-center mx-auto mb-6 text-3xl">
          ⚠
        </div>
        <h1 className="text-xl font-bold text-white mb-2">Something went wrong</h1>
        <p className="text-gray-500 text-sm mb-6">
          An unexpected error occurred. Your data is safe — please try again or contact support if this persists.
        </p>
        {error?.digest && (
          <p className="text-gray-700 text-xs font-mono mb-6">Error ID: {error.digest}</p>
        )}
        <div className="flex items-center justify-center gap-3">
          <button
            onClick={reset}
            className="px-5 py-2.5 rounded-xl text-sm font-semibold bg-violet-600 hover:bg-violet-500 text-white transition-colors"
          >
            Try again
          </button>
          <a
            href="/dashboard"
            className="px-5 py-2.5 rounded-xl text-sm font-medium bg-gray-800 hover:bg-gray-700 text-gray-300 transition-colors"
          >
            Go to dashboard
          </a>
        </div>
      </div>
    </div>
  );
}
