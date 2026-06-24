'use client';

import { useState, useEffect } from 'react';

const STORAGE_KEY = 'cookie_consent';

async function postConsent(accepted: boolean): Promise<void> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  if (!token) return;
  try {
    await fetch('/api/users/consent', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ accepted }),
    });
  } catch {
    // silently fail — localStorage already records the choice
  }
}

export function CookieBanner() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) {
      setVisible(true);
    }
  }, []);

  const handleChoice = async (accepted: boolean) => {
    localStorage.setItem(STORAGE_KEY, accepted ? 'accepted' : 'declined');
    setVisible(false);
    await postConsent(accepted);
  };

  if (!visible) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 p-4 flex justify-center">
      <div className="bg-gray-900 border border-gray-700 rounded-2xl shadow-2xl p-5 max-w-xl w-full flex flex-col sm:flex-row items-start sm:items-center gap-4">
        <p className="text-sm text-gray-300 flex-1">
          We use cookies to improve your experience. By continuing you agree to our use of cookies.
        </p>
        <div className="flex gap-3 shrink-0">
          <button
            onClick={() => handleChoice(false)}
            className="px-4 py-2 text-sm text-gray-400 border border-gray-700 hover:border-gray-500 rounded-xl transition-colors"
          >
            Decline
          </button>
          <button
            onClick={() => handleChoice(true)}
            className="px-4 py-2 text-sm font-semibold text-white bg-violet-600 hover:bg-violet-500 rounded-xl transition-colors"
          >
            Accept
          </button>
        </div>
      </div>
    </div>
  );
}
