import type { MetadataRoute } from 'next'

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
        disallow: ['/api/', '/register', '/onboarding', '/dashboard'],
      },
    ],
    sitemap: 'https://vantro.ai/sitemap.xml',
  }
}
