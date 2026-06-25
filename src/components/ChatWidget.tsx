'use client';

import { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, Loader2 } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: "Hi! I'm Vantro's AI assistant. Ask me anything about our platform, agents, or pricing." },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  useEffect(() => {
    if (open) inputRef.current?.focus();
  }, [open]);

  async function send() {
    const text = input.trim();
    if (!text || loading) return;
    const next: Message[] = [...messages, { role: 'user', content: text }];
    setMessages(next);
    setInput('');
    setLoading(true);
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: next }),
      });
      if (!res.ok) throw new Error('failed');
      const data = await res.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.content }]);
    } catch {
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: 'Sorry, something went wrong. Please try again or email hello@vantro.ai.' },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleKey(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  }

  return (
    <div style={{ position: 'fixed', bottom: 24, right: 24, zIndex: 500 }}>
      {open && (
        <div
          style={{
            position: 'absolute',
            bottom: 64,
            right: 0,
            width: 360,
            height: 480,
            backgroundColor: 'oklch(0.18 0 0)',
            border: '1px solid rgba(255,255,255,0.10)',
            borderRadius: 16,
            boxShadow: '0 24px 80px rgba(0,0,0,0.6)',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
          }}
        >
          {/* Header */}
          <div
            style={{
              padding: '14px 16px',
              borderBottom: '1px solid rgba(255,255,255,0.08)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexShrink: 0,
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  backgroundColor: 'oklch(0.75 0.18 145)',
                  boxShadow: '0 0 6px oklch(0.75 0.18 145)',
                }}
              />
              <span style={{ fontFamily: 'Space Grotesk, sans-serif', fontWeight: 600, fontSize: 14, color: 'oklch(0.97 0 0)' }}>
                Vantro Assistant
              </span>
            </div>
            <button
              onClick={() => setOpen(false)}
              style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'oklch(0.60 0 0)', padding: 4, display: 'flex' }}
            >
              <X size={16} />
            </button>
          </div>

          {/* Messages */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '12px 14px', display: 'flex', flexDirection: 'column', gap: 10 }}>
            {messages.map((msg, i) => (
              <div
                key={i}
                style={{
                  alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                  maxWidth: '85%',
                  backgroundColor: msg.role === 'user' ? 'oklch(0.97 0 0)' : 'rgba(255,255,255,0.07)',
                  color: msg.role === 'user' ? 'oklch(0.12 0 0)' : 'oklch(0.85 0 0)',
                  borderRadius: msg.role === 'user' ? '12px 12px 4px 12px' : '12px 12px 12px 4px',
                  padding: '9px 12px',
                  fontSize: 13,
                  lineHeight: 1.55,
                  fontFamily: 'Inter, sans-serif',
                }}
              >
                {msg.content}
              </div>
            ))}
            {loading && (
              <div
                style={{
                  alignSelf: 'flex-start',
                  backgroundColor: 'rgba(255,255,255,0.07)',
                  borderRadius: '12px 12px 12px 4px',
                  padding: '9px 12px',
                  display: 'flex',
                  gap: 6,
                  alignItems: 'center',
                }}
              >
                <Loader2 size={12} style={{ color: 'oklch(0.60 0 0)', animation: 'spin 1s linear infinite' }} />
                <span style={{ fontSize: 12, color: 'oklch(0.60 0 0)', fontFamily: 'Inter, sans-serif' }}>Thinking…</span>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div
            style={{
              padding: '10px 12px',
              borderTop: '1px solid rgba(255,255,255,0.08)',
              display: 'flex',
              gap: 8,
              flexShrink: 0,
            }}
          >
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKey}
              placeholder="Ask anything…"
              disabled={loading}
              style={{
                flex: 1,
                background: 'rgba(255,255,255,0.06)',
                border: '1px solid rgba(255,255,255,0.10)',
                borderRadius: 8,
                padding: '8px 12px',
                fontSize: 13,
                color: 'oklch(0.97 0 0)',
                fontFamily: 'Inter, sans-serif',
                outline: 'none',
              }}
            />
            <button
              onClick={send}
              disabled={loading || !input.trim()}
              style={{
                background: input.trim() && !loading ? 'oklch(0.97 0 0)' : 'rgba(255,255,255,0.12)',
                border: 'none',
                borderRadius: 8,
                width: 36,
                height: 36,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: input.trim() && !loading ? 'pointer' : 'default',
                flexShrink: 0,
                transition: 'background 0.15s',
              }}
            >
              <Send size={14} style={{ color: input.trim() && !loading ? 'oklch(0.12 0 0)' : 'oklch(0.50 0 0)' }} />
            </button>
          </div>
        </div>
      )}

      {/* Toggle button */}
      <button
        onClick={() => setOpen(o => !o)}
        aria-label={open ? 'Close chat' : 'Open chat'}
        style={{
          width: 52,
          height: 52,
          borderRadius: '50%',
          background: 'oklch(0.97 0 0)',
          border: 'none',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 4px 24px rgba(0,0,0,0.4)',
          transition: 'transform 0.2s ease, box-shadow 0.2s ease',
        }}
        onMouseEnter={e => {
          (e.currentTarget as HTMLButtonElement).style.transform = 'scale(1.08)';
          (e.currentTarget as HTMLButtonElement).style.boxShadow = '0 8px 32px rgba(0,0,0,0.5)';
        }}
        onMouseLeave={e => {
          (e.currentTarget as HTMLButtonElement).style.transform = 'scale(1)';
          (e.currentTarget as HTMLButtonElement).style.boxShadow = '0 4px 24px rgba(0,0,0,0.4)';
        }}
      >
        {open
          ? <X size={20} style={{ color: 'oklch(0.12 0 0)' }} />
          : <MessageCircle size={20} style={{ color: 'oklch(0.12 0 0)' }} />
        }
      </button>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
