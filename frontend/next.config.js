/** @type {import('next').NextConfig} */
const nextConfig = {
  compress: true,
  productionBrowserSourceMaps: false,
  transpilePackages: ['lenis'],
  turbopack: {
    root: __dirname,
  },

  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          { key: 'X-Frame-Options',           value: 'DENY'                                       },
          { key: 'X-Content-Type-Options',     value: 'nosniff'                                   },
          { key: 'Referrer-Policy',            value: 'strict-origin-when-cross-origin'           },
          { key: 'Permissions-Policy',         value: 'camera=(), microphone=(), geolocation=()' },
          { key: 'X-DNS-Prefetch-Control',     value: 'on'                                        },
          { key: 'Strict-Transport-Security',  value: 'max-age=31536000; includeSubDomains'       },
        ],
      },
      {
        // Long-term cache for static assets
        source: '/(_next/static|fonts|images)/(.*)',
        headers: [
          { key: 'Cache-Control', value: 'public, max-age=31536000, immutable' },
        ],
      },
    ]
  },

  images: {
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048],
    imageSizes:  [16, 32, 48, 64, 96, 128, 256, 384],
    minimumCacheTTL: 86400,
    dangerouslyAllowSVG: true,
    contentSecurityPolicy: "default-src 'self'; script-src 'none'; sandbox;",
  },
}

module.exports = nextConfig
