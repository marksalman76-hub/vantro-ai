import type { Metadata } from 'next'
import ClientAdminSidebar from './_components/ClientAdminSidebar'

export const metadata: Metadata = { title: 'Admin | Vantro' }

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return <ClientAdminSidebar>{children}</ClientAdminSidebar>
}
