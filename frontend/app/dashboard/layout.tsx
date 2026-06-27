import ClientSidebar from './_components/ClientSidebar';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div
      className="flex min-h-screen"
      style={{ background: 'var(--t-bg)' }}
    >
      <ClientSidebar />
      <main
        className="flex-1 overflow-y-auto"
        style={{ background: 'var(--t-bg)', minHeight: '100vh' }}
      >
        {children}
      </main>
    </div>
  );
}
