import type { Metadata } from 'next';
import ClientSidebar from './_components/ClientSidebar';

export const metadata: Metadata = {
  title: 'Workspace | Vantro',
  description: 'Your Vantro AI agent workspace.',
  robots: { index: false, follow: false },
};

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-950 text-white flex">
      <ClientSidebar />
      <main className="flex-1 overflow-auto min-h-screen">
        {children}
      </main>
    </div>
  );
}
