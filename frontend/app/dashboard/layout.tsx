import ClientSidebar from './_components/ClientSidebar';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div
      className="flex min-h-screen"
      style={{ background: '#0A0D14' }}
    >
      <ClientSidebar />
      <main
        className="flex-1 overflow-y-auto"
        style={{ background: '#0A0D14', minHeight: '100vh' }}
      >
        {children}
      </main>
    </div>
  );
}
