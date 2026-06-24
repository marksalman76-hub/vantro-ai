'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { motion } from 'framer-motion'

const menuItems = [
  { icon: '📊', label: 'Dashboard', href: '/dashboard' },
  { icon: '✂️', label: 'Editor',    href: '/editor' },
  { icon: '📁', label: 'Projects',  href: '/projects' },
  { icon: '⚙️', label: 'Settings',  href: '/settings' },
]

export default function Sidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const [collapsed, setCollapsed] = useState(false)

  const handleLogout = () => {
    localStorage.removeItem('token')
    router.push('/login')
  }

  return (
    <motion.div
      animate={{ width: collapsed ? 80 : 280 }}
      transition={{ duration: 0.25, ease: 'easeInOut' }}
      className="flex flex-col shrink-0 h-screen overflow-hidden"
      style={{
        background: 'rgba(10, 14, 30, 0.95)',
        borderRight: '1px solid rgba(255,255,255,0.08)',
        backdropFilter: 'blur(20px)',
      }}
    >
      {/* Logo */}
      <div className="p-4 border-b border-white/[0.06]">
        <Link href="/dashboard" className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl flex items-center justify-center text-white font-black text-base shrink-0"
            style={{ background: 'linear-gradient(135deg,#3B82F6,#8B5CF6)', boxShadow: '0 0 20px rgba(59,130,246,0.4)' }}>
            V
          </div>
          {!collapsed && (
            <motion.span
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="font-bold text-white text-lg whitespace-nowrap"
            >
              Vantro
            </motion.span>
          )}
        </Link>
      </div>

      {/* Nav */}
      <nav className="flex-1 p-3 space-y-1">
        {menuItems.map(item => {
          const active = pathname === item.href || (item.href !== '/dashboard' && pathname?.startsWith(item.href))
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 p-3 rounded-xl transition-all ${
                active
                  ? 'bg-blue-500/15 text-blue-300 border border-blue-500/25'
                  : 'text-white/50 hover:text-white hover:bg-white/[0.06] border border-transparent'
              }`}
            >
              <span className="text-xl shrink-0">{item.icon}</span>
              {!collapsed && <span className="text-sm font-medium whitespace-nowrap">{item.label}</span>}
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="p-3 border-t border-white/[0.06] space-y-1">
        <button
          onClick={() => setCollapsed(c => !c)}
          className="w-full flex items-center gap-3 p-3 rounded-xl text-sm text-white/30 hover:text-white/60 hover:bg-white/[0.04] transition-all"
        >
          <span className="text-xl">{collapsed ? '→' : '←'}</span>
          {!collapsed && <span>Collapse</span>}
        </button>
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 p-3 rounded-xl text-sm text-white/30 hover:text-red-400 hover:bg-red-500/[0.06] transition-all"
        >
          <span className="text-xl">🚪</span>
          {!collapsed && <span>Logout</span>}
        </button>
      </div>
    </motion.div>
  )
}
