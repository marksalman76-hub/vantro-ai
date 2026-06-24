export default function DashboardLoading() {
  return (
    <div className="p-8 max-w-5xl space-y-6 animate-pulse">
      <div className="h-8 w-48 bg-gray-800 rounded-xl" />
      <div className="grid grid-cols-3 gap-4">
        {[1, 2, 3].map(i => (
          <div key={i} className="h-24 bg-gray-800/60 rounded-2xl" />
        ))}
      </div>
      <div className="h-64 bg-gray-800/60 rounded-2xl" />
      <div className="h-40 bg-gray-800/60 rounded-2xl" />
    </div>
  );
}
