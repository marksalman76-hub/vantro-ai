'use client'

import { useEffect, useState } from 'react'

const AGENTS = [
  { name: 'Atlas',    role: 'Operations Orchestrator', img: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-01-atlas-HcT8hzhWCVimMA7hv773NB.webp' },
  { name: 'Echo',     role: 'Customer Support',        img: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-02-echo-jBseNuruo6zVaNEwKn4uiC.webp' },
  { name: 'Ledger',   role: 'Finance & Accounting',    img: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-03-ledger-F85UZALSwUyRYrbFukUT32.webp' },
  { name: 'Quill',    role: 'Content Writer',          img: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-04-quill-bj87Aczd4DkvzVpDymRCXC.webp' },
  { name: 'Pixel',    role: 'Design & Creative',       img: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-05-pixel-5wPhecN9KKS2GP83txqg3L.webp' },
  { name: 'Forge',    role: 'Code & Engineering',      img: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-06-forge-74Qoi5iZ6HSHfAKCtpmGiV.webp' },
  { name: 'Sentinel', role: 'Security & Compliance',   img: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-07-sentinel-R2z9W7XcosMCmKrgyy5egK.webp' },
  { name: 'Pulse',    role: 'Marketing Strategist',    img: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-08-pulse-HnoLtavTCfRkHgHn4oRHWY.webp' },
  { name: 'Harbor',   role: 'Recruiting & HR',         img: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-09-harbor-JSYpGWNWqMBKuGkeADyUGQ.webp' },
  { name: 'Vector',   role: 'Data Analyst',            img: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-10-vector-h5yum6XcwDvxJveuEcaaRr.webp' },
  { name: 'Scout',    role: 'Research Agent',          img: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-11-scout-RA2fVyF7bjnc6jF6huf2u7.webp' },
  { name: 'Relay',    role: 'Email & Comms',           img: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-12-relay-hw2y7EPjNeEPfnsw4Gbb8v.webp' },
  { name: 'Nova',     role: 'Sales Closer',            img: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-13-nova-RjP6GCP9dydGjYzxoGqUS4.webp' },
  { name: 'Cipher',   role: 'Legal Reviewer',          img: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-14-cipher-6bpayqEPE2evcWh4kx4ewj.webp' },
  { name: 'Tempo',    role: 'Project Manager',         img: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-15-tempo-SH2nCJiGUVjw6yNbfvyR5r.webp' },
  { name: 'Mosaic',   role: 'Social Media Manager',    img: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-16-mosaic-BLWJNJuQDBV5a4YBrz4p5X.webp' },
  { name: 'Lumen',    role: 'Brand Strategist',        img: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-17-lumen-2qvMVEXiCmKsKCbwvMDhsa.webp' },
  { name: 'Drift',    role: 'Logistics & Supply',      img: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-18-drift-53Ynh9MkY87HuXeNL6Rtqc.webp' },
  { name: 'Sage',     role: 'Knowledge Base',          img: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-19-sage-8wXDmjtcYDgZwwVf5p8Tyn.webp' },
  { name: 'Bolt',     role: 'Automation Engineer',     img: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-20-bolt-62QDSf9Xu4fefkZnymAYSB.webp' },
  { name: 'Aria',     role: 'Voice & Telephony',       img: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-21-aria-GdEzW9bgD4tMZaCrMfUAUK.webp' },
  { name: 'Onyx',     role: 'Executive Assistant',     img: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-22-onyx-YJEsc2eKjrVan3gzHX8awN.webp' },
]

const STATS = [
  { label: 'Tasks Completed', value: '1,248', delta: '+12% this week' },
  { label: 'Messages Today',  value: '384',   delta: '+8% vs yesterday' },
  { label: 'Active Agents',   value: '22',    delta: 'All online' },
  { label: 'Avg Response',    value: '1.2s',  delta: '-18% faster' },
]

export default function DashboardPage() {
  const [workspace, setWorkspace] = useState('')

  useEffect(() => {
    const w = localStorage.getItem('workspace_name')
    if (w) setWorkspace(w)
  }, [])

  const hour = new Date().getHours()
  const greeting = hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening'

  return (
    <div style={{ padding: '32px 36px', maxWidth: 1100 }}>
      <div style={{ marginBottom: 32 }}>
        <h1 style={{ color: '#fff', fontSize: 22, fontWeight: 700, letterSpacing: '-0.02em' }}>
          {greeting}{workspace ? `, ${workspace}` : ''}
        </h1>
        <p style={{ color: 'rgba(255,255,255,0.35)', fontSize: 13, marginTop: 4 }}>
          Your AI workforce is online and ready.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14, marginBottom: 36 }}>
        {STATS.map(s => (
          <div key={s.label} style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 12, padding: '18px 20px' }}>
            <p style={{ color: 'rgba(255,255,255,0.35)', fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 8 }}>{s.label}</p>
            <p style={{ color: '#fff', fontSize: 24, fontWeight: 700, letterSpacing: '-0.02em' }}>{s.value}</p>
            <p style={{ color: '#34d399', fontSize: 11, marginTop: 4 }}>{s.delta}</p>
          </div>
        ))}
      </div>

      <div style={{ marginBottom: 14, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <h2 style={{ color: '#fff', fontSize: 14, fontWeight: 600 }}>Your Agents</h2>
        <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.3)' }}>{AGENTS.length} active</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(158px, 1fr))', gap: 12 }}>
        {AGENTS.map(agent => (
          <div
            key={agent.name}
            style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 12, padding: '16px 14px', cursor: 'pointer', transition: 'all 0.15s' }}
            onMouseEnter={e => { const el = e.currentTarget as HTMLElement; el.style.background = 'rgba(255,255,255,0.07)'; el.style.borderColor = 'rgba(255,107,53,0.25)' }}
            onMouseLeave={e => { const el = e.currentTarget as HTMLElement; el.style.background = 'rgba(255,255,255,0.04)'; el.style.borderColor = 'rgba(255,255,255,0.07)' }}
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={agent.img} alt={agent.name} width={40} height={40} style={{ borderRadius: '50%', marginBottom: 10, objectFit: 'cover' }} />
            <p style={{ color: '#fff', fontSize: 13, fontWeight: 600, marginBottom: 2 }}>{agent.name}</p>
            <p style={{ color: 'rgba(255,255,255,0.35)', fontSize: 11, marginBottom: 10, lineHeight: 1.3 }}>{agent.role}</p>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, fontSize: 10, color: '#34d399', background: 'rgba(52,211,153,0.1)', padding: '2px 8px', borderRadius: 100 }}>
              <span style={{ width: 5, height: 5, borderRadius: '50%', background: '#34d399', flexShrink: 0 }} />
              Online
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
