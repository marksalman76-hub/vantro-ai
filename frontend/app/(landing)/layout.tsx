import { ReactNode } from 'react'
import Navbar from '@/components/Navbar'

export default function LandingLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen" style={{ backgroundColor: 'rgb(11, 15, 25)' }}>
      <Navbar />
      {children}
    </div>
  )
}
