'use client';

import { useState } from 'react';

interface RefundModalProps {
  onClose: () => void;
  onSuccess: (message: string) => void;
  onError: (message: string) => void;
}

export default function RefundModal({ onClose, onSuccess, onError }: RefundModalProps) {
  const [loading, setLoading] = useState(false);

  const handleConfirm = async () => {
    const token = localStorage.getItem('token');
    if (!token) { onError('Not authenticated. Please log in again.'); return; }

    setLoading(true);
    try {
      const res = await fetch('/api/billing/refund-request', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      if (res.ok) {
        onSuccess(data.detail || 'Refund processed. Your subscription has been cancelled.');
      } else {
        onError(data.detail || 'An error occurred. Please contact support@vantro.ai.');
      }
    } catch {
      onError('Unable to reach the server. Please try again or contact support@vantro.ai.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="bg-gray-900 border border-gray-700 rounded-2xl w-full max-w-md p-6 shadow-2xl">
        <h2 className="text-white font-bold text-lg mb-1">Request a Refund</h2>
        <p className="text-gray-400 text-xs mb-5">Please read the policy below before confirming.</p>

        <div className="bg-gray-800/60 border border-gray-700 rounded-xl p-4 mb-6 text-xs text-gray-300 leading-relaxed space-y-2">
          <p>
            <span className="text-white font-semibold">Refund Policy:</span> You are eligible for a full
            refund within <span className="text-white font-semibold">72 hours of signup</span> if no agent
            tasks have been run.
          </p>
          <p>
            This action will <span className="text-red-400 font-semibold">cancel your subscription immediately</span> and
            cannot be undone. Refunds typically appear on your statement within 5–10 business days.
          </p>
          <p>
            If you have already run agent tasks, you are not eligible for a refund. Contact{' '}
            <a href="mailto:support@vantro.ai" className="text-violet-400 hover:text-violet-300 underline">
              support@vantro.ai
            </a>{' '}
            if you have questions.
          </p>
        </div>

        <div className="flex gap-3 justify-end">
          <button
            onClick={onClose}
            disabled={loading}
            className="px-4 py-2 rounded-xl text-sm font-medium border border-gray-700 text-gray-400 hover:text-white hover:border-gray-600 disabled:opacity-50 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleConfirm}
            disabled={loading}
            className="px-4 py-2 rounded-xl text-sm font-semibold bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white transition-colors"
          >
            {loading ? 'Processing…' : 'Confirm Refund'}
          </button>
        </div>
      </div>
    </div>
  );
}
