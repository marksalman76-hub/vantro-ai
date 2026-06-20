import type { MetadataRoute } from 'next'

export default function sitemap(): MetadataRoute.Sitemap {
  const base = 'https://vantro.ai'
  return [
    { url: base,           lastModified: new Date(), changeFrequency: 'weekly',  priority: 1   },
    { url: `${base}/#agents`,          lastModified: new Date(), changeFrequency: 'monthly', priority: 0.9 },
    { url: `${base}/#integrations`,    lastModified: new Date(), changeFrequency: 'monthly', priority: 0.8 },
    { url: `${base}/#roi-calculator`,  lastModified: new Date(), changeFrequency: 'monthly', priority: 0.7 },
    { url: `${base}/#testimonials`,    lastModified: new Date(), changeFrequency: 'monthly', priority: 0.6 },
    { url: `${base}/privacy`,          lastModified: new Date(), changeFrequency: 'yearly',  priority: 0.4 },
    { url: `${base}/terms`,            lastModified: new Date(), changeFrequency: 'yearly',  priority: 0.4 },
  ]
}
