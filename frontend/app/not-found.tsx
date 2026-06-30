import Link from 'next/link'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: '404 — Page Not Found',
  robots: { index: false, follow: false },
}

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center px-4">
      {/* Background glow */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[400px] bg-violet-600/8 rounded-full blur-[120px]" />
      </div>

      <div className="text-center max-w-lg relative">
        {/* Big 404 */}
        <div className="text-[120px] font-black leading-none bg-gradient-to-b from-white/20 to-transparent bg-clip-text text-transparent select-none mb-2">
          404
        </div>

        <h1 className="text-2xl font-bold text-white mb-3">Page not found</h1>
        <p className="text-gray-400 mb-10 leading-relaxed">
          That page doesn't exist. It may have been moved, deleted, or you may have followed a broken link.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
          <Link
            href="/"
            className="bg-purple-600 hover:bg-purple-700 text-white font-semibold px-6 py-3 rounded-xl transition-colors"
          >
            Go home
          </Link>
        </div>
      </div>
    </div>
  )
}
