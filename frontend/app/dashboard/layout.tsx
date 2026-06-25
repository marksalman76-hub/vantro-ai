import ClientSidebar from './_components/ClientSidebar';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div
      className="flex min-h-screen"
      style={{ background: 'oklch(0.14 0 0)', color: 'oklch(0.97 0 0)' }}
    >
      <ClientSidebar />
      <main
        className="flex-1 overflow-y-auto"
        style={{ background: 'oklch(0.14 0 0)', minHeight: '100vh' }}
      >
        {children}
      </main>
    </div>
  );
}
