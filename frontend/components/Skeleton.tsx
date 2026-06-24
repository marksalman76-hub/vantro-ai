'use client';

interface SkeletonProps {
  className?: string;
  lines?: number;
}

export function Skeleton({ className = '', lines = 1 }: SkeletonProps) {
  if (lines === 1) {
    return <div className={`animate-pulse bg-gray-800 rounded ${className}`} />;
  }
  return (
    <div className={`space-y-2 ${className}`}>
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className={`animate-pulse bg-gray-800 rounded h-4 ${i === lines - 1 ? 'w-3/4' : 'w-full'}`}
        />
      ))}
    </div>
  );
}

export function SkeletonCard() {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5 flex flex-col gap-3">
      <div className="animate-pulse bg-gray-800 rounded h-3 w-24" />
      <div className="animate-pulse bg-gray-800 rounded h-8 w-32" />
      <div className="animate-pulse bg-gray-800 rounded h-3 w-20" />
    </div>
  );
}

export function SkeletonTable({ rows = 5 }: { rows?: number }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden">
      {/* Header */}
      <div className="px-5 py-4 border-b border-gray-800 flex items-center gap-4">
        <div className="animate-pulse bg-gray-800 rounded h-3 w-32" />
        <div className="animate-pulse bg-gray-800 rounded h-3 w-20" />
        <div className="animate-pulse bg-gray-800 rounded h-3 w-24 ml-auto" />
      </div>
      {/* Rows */}
      <div className="divide-y divide-gray-800/60">
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="px-5 py-4 flex items-center gap-4">
            <div className="flex-1 space-y-2">
              <div className="animate-pulse bg-gray-800 rounded h-3 w-48" />
              <div className="animate-pulse bg-gray-800 rounded h-2.5 w-32" />
            </div>
            <div className="animate-pulse bg-gray-800 rounded-full h-5 w-20" />
            <div className="animate-pulse bg-gray-800 rounded h-3 w-10" />
          </div>
        ))}
      </div>
    </div>
  );
}
