import type { Metadata } from 'next';
import AdminSidebar from './_components/AdminSidebar';
import AdminAuthGuard from './_components/AdminAuthGuard';

export const metadata: Metadata = {
  title: 'Admin | Vantro',
  robots: { index: false, follow: false },
};

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <AdminAuthGuard sidebar={<AdminSidebar />}>
      {children}
    </AdminAuthGuard>
  );
}
