import { useEffect } from 'react'
import { X, AlertCircle, CheckCircle } from 'lucide-react'

interface ToastProps {
  type: 'error' | 'success' | 'info'
  message: string
  duration?: number
  onClose: () => void
}

export default function Toast({ type, message, duration = 5000, onClose }: ToastProps) {
  useEffect(() => {
    const timer = setTimeout(onClose, duration)
    return () => clearTimeout(timer)
  }, [duration, onClose])

  const getIcon = () => {
    switch (type) {
      case 'error':
        return <AlertCircle className="w-5 h-5" />
      case 'success':
        return <CheckCircle className="w-5 h-5" />
      default:
        return null
    }
  }

  const getBackgroundColor = () => {
    switch (type) {
      case 'error':
        return 'bg-red-500/90 border-red-500'
      case 'success':
        return 'bg-emerald-500/90 border-emerald-500'
      default:
        return 'bg-white/90 border-white'
    }
  }

  return (
    <div className="fixed top-24 right-6 z-[100] animate-slide-in">
      <div
        className={`
          ${getBackgroundColor()}
          backdrop-blur-md
          border-2
          px-6 py-4
          rounded-none
          shadow-lg
          flex items-center gap-3
          min-w-[300px]
          max-w-[500px]
          transition-all duration-300
        `}
      >
        <div className="flex-shrink-0 text-white">
          {getIcon()}
        </div>
        <p className="flex-1 text-sm font-medium text-white">
          {message}
        </p>
        <button
          onClick={onClose}
          className="flex-shrink-0 text-white/80 hover:text-white transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
