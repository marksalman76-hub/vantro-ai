export default function AdminLoading() {
  return (
    <div className="p-8 max-w-6xl space-y-6 animate-pulse">
      <div className="h-8 w-56 bg-gray-800 rounded-xl" />
      <div className="grid grid-cols-4 gap-4">
        {[1, 2, 3, 4].map(i => (
          <div key={i} className="h-20 bg-gray-800/60 rounded-2xl" />
        ))}
      </div>
      <div className="h-72 bg-gray-800/60 rounded-2xl" />
    </div>
  );
}
