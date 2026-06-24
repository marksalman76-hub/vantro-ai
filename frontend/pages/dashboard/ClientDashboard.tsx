import React, { useState, useEffect } from "react";

interface MediaHistory {
  id: string;
  avatar: string;
  script: string;
  status: "pending" | "processing" | "completed" | "failed";
  video_url?: string;
  created_at: string;
}

interface CreditsAccount {
  total_credits: number;
  used_credits: number;
  remaining_credits: number;
}

export default function ClientDashboard() {
  const [credits, setCredits] = useState<CreditsAccount | null>(null);
  const [mediaHistory, setMediaHistory] = useState<MediaHistory[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboard = async () => {
      const token = localStorage.getItem("access_token");
      if (!token) return;

      try {
        const creditsRes = await fetch("/api/credits", {
          headers: { Authorization: `Bearer ${token}` },
        });
        const historyRes = await fetch("/api/media-jobs", {
          headers: { Authorization: `Bearer ${token}` },
        });

        const creditsData = await creditsRes.json();
        const historyData = await historyRes.json();

        setCredits(creditsData);
        setMediaHistory(historyData);
      } catch (error) {
        console.error("Failed to fetch dashboard", error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
  }, []);

  if (loading) return <div className="p-8">Loading...</div>;

  const usagePercent = credits ? (credits.used_credits / credits.total_credits) * 100 : 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">Dashboard</h1>

        {/* Credits Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-gray-500 text-sm font-medium mb-2">Total Credits</h2>
            <p className="text-3xl font-bold text-blue-600">{credits?.total_credits || 0}</p>
          </div>
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-gray-500 text-sm font-medium mb-2">Used Credits</h2>
            <p className="text-3xl font-bold text-orange-600">{credits?.used_credits || 0}</p>
          </div>
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-gray-500 text-sm font-medium mb-2">Remaining</h2>
            <p className="text-3xl font-bold text-green-600">{credits?.remaining_credits || 0}</p>
          </div>
        </div>

        {/* Usage Progress */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-xl font-bold mb-4">Usage This Month</h2>
          <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
            <div
              className="bg-gradient-to-r from-blue-500 to-indigo-600 h-full"
              style={{ width: `${Math.min(usagePercent, 100)}%` }}
            ></div>
          </div>
          <p className="text-sm text-gray-600 mt-2">{Math.round(usagePercent)}% used</p>
        </div>

        {/* Media History */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-bold mb-4">Recent Videos</h2>
          {mediaHistory.length === 0 ? (
            <p className="text-gray-500">No videos yet. Create your first video!</p>
          ) : (
            <div className="space-y-4">
              {mediaHistory.map((media) => (
                <div key={media.id} className="flex items-center justify-between border-b pb-4">
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{media.avatar}</p>
                    <p className="text-sm text-gray-500 truncate">{media.script.substring(0, 50)}...</p>
                    <p className="text-xs text-gray-400">{new Date(media.created_at).toLocaleDateString()}</p>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      media.status === "completed" ? "bg-green-100 text-green-800" :
                      media.status === "processing" ? "bg-yellow-100 text-yellow-800" :
                      media.status === "failed" ? "bg-red-100 text-red-800" :
                      "bg-gray-100 text-gray-800"
                    }`}>
                      {media.status}
                    </span>
                    {media.video_url && (
                      <a href={media.video_url} className="text-blue-600 hover:text-blue-800">Watch</a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
