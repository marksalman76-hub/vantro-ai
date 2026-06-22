import type { Metadata } from 'next';
import AdminSidebar from './_components/AdminSidebar';

export const metadata: Metadata = {
  title: 'Admin | Vantro',
  robots: { index: false, follow: false },
};

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-950 text-white flex">
      <AdminSidebar />
      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
  );
}
