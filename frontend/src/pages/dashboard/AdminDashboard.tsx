import React, { useState, useEffect } from "react";

interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
  workspace_count: number;
}

interface AdminStats {
  total_users: number;
  total_revenue: number;
  active_subscriptions: number;
  videos_generated: number;
}

export default function AdminDashboard() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAdmin = async () => {
      const token = localStorage.getItem("access_token");
      if (!token) return;
      try {
        const statsRes = await fetch("/api/admin/stats", {
          headers: { Authorization: `Bearer ${token}` },
        });
        const usersRes = await fetch("/api/admin/users", {
          headers: { Authorization: `Bearer ${token}` },
        });
        const statsData = await statsRes.json();
        const usersData = await usersRes.json();
        setStats(statsData);
        setUsers(usersData);
      } catch (error) {
        console.error("Failed to fetch admin data", error);
      } finally {
        setLoading(false);
      }
    };
    fetchAdmin();
  }, []);

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">Admin Dashboard</h1>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-gray-500 text-sm font-medium mb-2">Total Users</h2>
            <p className="text-3xl font-bold text-blue-600">{stats?.total_users || 0}</p>
          </div>
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-gray-500 text-sm font-medium mb-2">Total Revenue</h2>
            <p className="text-3xl font-bold text-green-600">${(stats?.total_revenue || 0).toFixed(2)}</p>
          </div>
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-gray-500 text-sm font-medium mb-2">Active Subscriptions</h2>
            <p className="text-3xl font-bold text-purple-600">{stats?.active_subscriptions || 0}</p>
          </div>
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-gray-500 text-sm font-medium mb-2">Videos Generated</h2>
            <p className="text-3xl font-bold text-orange-600">{stats?.videos_generated || 0}</p>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-bold mb-4">Users</h2>
          {users.length === 0 ? (
            <p className="text-gray-500">No users yet</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-sm font-medium text-gray-900">Email</th>
                    <th className="px-6 py-3 text-left text-sm font-medium text-gray-900">Name</th>
                    <th className="px-6 py-3 text-left text-sm font-medium text-gray-900">Workspaces</th>
                    <th className="px-6 py-3 text-left text-sm font-medium text-gray-900">Joined</th>
                    <th className="px-6 py-3 text-left text-sm font-medium text-gray-900">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {users.map((user) => (
                    <tr key={user.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 text-sm text-gray-900">{user.email}</td>
                      <td className="px-6 py-4 text-sm text-gray-900">{user.name}</td>
                      <td className="px-6 py-4 text-sm text-gray-900">{user.workspace_count}</td>
                      <td className="px-6 py-4 text-sm text-gray-500">{new Date(user.created_at).toLocaleDateString()}</td>
                      <td className="px-6 py-4 text-sm"><button className="text-blue-600 hover:text-blue-800 mr-4">View</button><button className="text-red-600 hover:text-red-800">Suspend</button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
