import { createContext, useContext, useState, useCallback, type ReactNode } from 'react'

interface ToastCtx {
  visible: boolean
  message: string
  showToast: (message?: string) => void
}

const ToastContext = createContext<ToastCtx | null>(null)

export function ToastProvider({ children }: { children: ReactNode }) {
  const [visible, setVisible] = useState(false)
  const [message, setMessage] = useState('Feature coming soon')

  const showToast = useCallback((msg = 'Feature coming soon') => {
    setMessage(msg)
    setVisible(true)
    setTimeout(() => setVisible(false), 3000)
  }, [])

  return (
    <ToastContext.Provider value={{ visible, message, showToast }}>
      {children}
    </ToastContext.Provider>
  )
}

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be inside ToastProvider')
  return ctx
}
