import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { X, Clock, FileText, CheckCircle, Loader2, AlertCircle } from 'lucide-react'
import { getHistoryList, type HistoryItem } from '../services/api'

interface HistoryModalProps {
  isOpen: boolean
  onClose: () => void
}

export default function HistoryModal({ isOpen, onClose }: HistoryModalProps) {
  const [history, setHistory] = useState<HistoryItem[]>([])
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    if (isOpen) {
      fetchHistory()
    }
  }, [isOpen])

  const fetchHistory = async () => {
    setLoading(true)
    try {
      const data = await getHistoryList()
      setHistory(data)
    } catch (error: any) {
      console.error('获取历史记录失败:', error)
      alert(error.message || '获取历史记录失败')
    } finally {
      setLoading(false)
    }
  }

  const handleViewProject = (taskId: string) => {
    navigate(`/project/${taskId}`)
    onClose()
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'processing':
        return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
      case 'failed':
        return <AlertCircle className="w-5 h-5 text-red-500" />
      default:
        return <Clock className="w-5 h-5 text-gray-500" />
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return '已完成'
      case 'processing':
        return '处理中'
      case 'failed':
        return '失败'
      default:
        return '未知'
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return '刚刚'
    if (diffMins < 60) return `${diffMins} 分钟前`
    if (diffHours < 24) return `${diffHours} 小时前`
    if (diffDays < 7) return `${diffDays} 天前`
    
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    })
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-white rounded-2xl w-full max-w-2xl max-h-[80vh] overflow-hidden shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <Clock className="w-6 h-6 text-gray-700" />
            <h2 className="text-xl font-bold text-gray-900">历史记录</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[60vh]">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 text-gray-400 animate-spin" />
            </div>
          ) : history.length === 0 ? (
            <div className="text-center py-12">
              <Clock className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">暂无历史记录</p>
              <p className="text-sm text-gray-400 mt-2">上传代码后将显示在这里</p>
            </div>
          ) : (
            <div className="space-y-3">
              {history.map((item) => (
                <div
                  key={item.task_id}
                  className="flex items-center gap-4 p-4 border border-gray-200 rounded-xl hover:border-gray-300 hover:bg-gray-50 transition-all cursor-pointer group"
                  onClick={() => item.status === 'completed' && handleViewProject(item.task_id)}
                >
                  <div className="flex-shrink-0">
                    {getStatusIcon(item.status)}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <FileText className="w-4 h-4 text-gray-400 flex-shrink-0" />
                      <h3 className="font-medium text-gray-900 truncate">
                        {item.file_name}
                      </h3>
                    </div>
                    <div className="flex items-center gap-3 text-sm text-gray-500">
                      <span>{formatDate(item.created_at)}</span>
                      {item.file_count !== undefined && (
                        <>
                          <span>•</span>
                          <span>{item.file_count} 个文件</span>
                        </>
                      )}
                      <span>•</span>
                      <span className="flex items-center gap-1">
                        {getStatusText(item.status)}
                      </span>
                    </div>
                  </div>

                  {item.status === 'completed' && (
                    <div className="flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
                      <span className="text-sm text-gray-600">查看详情 →</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
