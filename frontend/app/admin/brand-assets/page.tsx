'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface BrandAsset {
  id: string;
  name: string;
  filename: string;
  mime_type: string;
  size: number;
  created_at: string;
}

function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function assetIcon(mime: string) {
  if (mime.startsWith('image/')) return '▧';
  if (mime.startsWith('video/')) return '▶';
  if (mime === 'application/pdf') return '📄';
  return '✎';
}

function assetColor(mime: string) {
  if (mime.startsWith('image/')) return 'text-blue-400 bg-blue-500/10 border-blue-500/20';
  if (mime.startsWith('video/')) return 'text-violet-400 bg-violet-500/10 border-violet-500/20';
  if (mime === 'application/pdf') return 'text-red-400 bg-red-500/10 border-red-500/20';
  return 'text-gray-300 bg-gray-800 border-gray-700';
}

export default function BrandAssetsPage() {
  const router = useRouter();
  const [assets, setAssets] = useState<BrandAsset[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  function getToken() {
    return localStorage.getItem('admin_token') || localStorage.getItem('token') || '';
  }

  useEffect(() => {
    const token = getToken();
    if (!token) { router.push('/admin-login'); return; }
    fetch('/api/admin/brand-assets', { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(d => setAssets(d.assets || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [router]);

  async function handleUpload(files: FileList | null) {
    if (!files || files.length === 0) return;
    const token = getToken();
    setUploading(true);
    setUploadError('');
    const uploaded: BrandAsset[] = [];
    for (const file of Array.from(files)) {
      const fd = new FormData();
      fd.append('file', file);
      try {
        const res = await fetch('/api/admin/brand-assets', {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
          body: fd,
        });
        if (res.ok) {
          const asset = await res.json();
          uploaded.push(asset);
        } else {
          const d = await res.json().catch(() => ({}));
          setUploadError(d.detail || 'Upload failed');
        }
      } catch {
        setUploadError('Upload failed — network error');
      }
    }
    if (uploaded.length > 0) {
      setAssets(prev => [...uploaded, ...prev]);
    }
    setUploading(false);
    if (fileInputRef.current) fileInputRef.current.value = '';
  }

  async function handleDelete(id: string) {
    const token = getToken();
    setDeletingId(id);
    try {
      const res = await fetch(`/api/admin/brand-assets/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        setAssets(prev => prev.filter(a => a.id !== id));
      }
    } catch {}
    setDeletingId(null);
  }

  return (
    <div className="p-6 max-w-4xl" style={{ paddingTop: '5rem' }}>
      <div className="mb-6 flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <Link href="/admin/create-media" className="text-xs text-gray-500 hover:text-gray-300">← Back to Create Media</Link>
          </div>
          <h1 className="text-xl font-bold text-white">Brand Assets</h1>
          <p className="text-gray-500 text-xs mt-1">Upload logos, product images, style references, and scripts for your media requests</p>
        </div>
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
          className="flex items-center gap-1.5 px-4 py-2 bg-violet-600 hover:bg-violet-700 disabled:opacity-50 text-white text-xs font-semibold rounded-xl transition-colors"
        >
          {uploading ? 'Uploading…' : '+ Upload asset'}
        </button>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept="image/*,video/*,application/pdf,.doc,.docx,.txt"
          className="hidden"
          onChange={e => handleUpload(e.target.files)}
        />
      </div>

      {uploadError && (
        <div className="mb-4 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2.5">
          <p className="text-red-300 text-xs">{uploadError}</p>
        </div>
      )}

      {/* Drop zone */}
      <div
        className="border-2 border-dashed border-gray-800 hover:border-violet-500/40 rounded-xl p-8 mb-6 text-center transition-colors cursor-pointer"
        onClick={() => fileInputRef.current?.click()}
        onDragOver={e => { e.preventDefault(); }}
        onDrop={e => { e.preventDefault(); handleUpload(e.dataTransfer.files); }}
      >
        <p className="text-gray-600 text-xs">Drag & drop files here, or click to browse</p>
        <p className="text-gray-700 text-[10px] mt-1">Images, videos, PDFs, Word docs, text files — max 50 MB each</p>
      </div>

      {/* Assets table */}
      <div className="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-800 text-xs text-gray-500">
              {['File', 'Type', 'Size', 'Uploaded', 'Actions'].map(h => (
                <th key={h} className="px-4 py-3 text-left font-medium">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800/60">
            {loading && (
              <tr>
                <td colSpan={5} className="py-6 px-4">
                  <div className="space-y-2">
                    {[1,2,3].map(i => <div key={i} className="h-10 bg-gray-800 rounded animate-pulse" />)}
                  </div>
                </td>
              </tr>
            )}
            {!loading && assets.length === 0 && (
              <tr>
                <td colSpan={5} className="text-center text-gray-600 text-sm py-10">
                  No brand assets yet. Upload your first asset above.
                </td>
              </tr>
            )}
            {assets.map(asset => (
              <tr key={asset.id} className="hover:bg-gray-800/30 transition-colors">
                <td className="px-4 py-3">
                  <p className="text-white text-xs font-medium truncate max-w-[220px]">{asset.name}</p>
                  <p className="text-gray-700 text-[10px] font-mono">{asset.id.slice(0, 8)}…</p>
                </td>
                <td className="px-4 py-3">
                  <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded border ${assetColor(asset.mime_type)}`}>
                    {assetIcon(asset.mime_type)} {asset.mime_type.split('/')[1]?.toUpperCase() || asset.mime_type}
                  </span>
                </td>
                <td className="px-4 py-3 text-gray-400 text-xs">{formatSize(asset.size)}</td>
                <td className="px-4 py-3 text-gray-500 text-xs">
                  {new Date(asset.created_at).toLocaleDateString()}
                </td>
                <td className="px-4 py-3">
                  <button
                    onClick={() => handleDelete(asset.id)}
                    disabled={deletingId === asset.id}
                    className="text-xs text-gray-500 hover:text-red-400 transition-colors disabled:opacity-40"
                  >
                    {deletingId === asset.id ? 'Deleting…' : 'Delete'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
