import { useState, useRef, useCallback } from 'react'
import { FileArchive, Loader2, CheckCircle2, AlertCircle, X } from 'lucide-react'
import axios from 'axios'
import Toast from './Toast'

interface UploadResult {
  taskId: string
  fileName: string
  fileCount: number
  status: 'uploading' | 'processing' | 'completed' | 'failed'
  progress: number
  message: string
}

interface CodeUploadZoneProps {
  onUploadComplete: (taskId: string, fileName: string) => void
}

export default function CodeUploadZone({ onUploadComplete }: CodeUploadZoneProps) {
  const [isDragOver, setIsDragOver] = useState(false)
  const [currentUpload, setCurrentUpload] = useState<UploadResult | null>(null)
  const [toast, setToast] = useState<{ type: 'error' | 'success' | 'info'; message: string } | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const handleDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault()
    event.stopPropagation()
    setIsDragOver(true)
  }, [])

  const handleDragLeave = useCallback((event: React.DragEvent) => {
    event.preventDefault()
    event.stopPropagation()
    setIsDragOver(false)
  }, [])

  const handleDrop = useCallback((event: React.DragEvent) => {
    event.preventDefault()
    event.stopPropagation()
    setIsDragOver(false)

    const droppedFiles = event.dataTransfer.files
    if (droppedFiles.length > 0) {
      processFile(droppedFiles[0])
    }
  }, [])

  const handleFileSelect = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      processFile(event.target.files[0])
    }
  }, [])

  const processFile = async (file: File) => {
    if (!file.name.endsWith('.zip')) {
      setCurrentUpload({
        taskId: '',
        fileName: file.name,
        fileCount: 0,
        status: 'failed',
        progress: 0,
        message: '请上传 ZIP 格式的代码压缩包',
      })
      setToast({ type: 'error', message: '请上传 ZIP 格式的代码压缩包' })
      return
    }

    const maxSizeMB = 500
    if (file.size > maxSizeMB * 1024 * 1024) {
      setCurrentUpload({
        taskId: '',
        fileName: file.name,
        fileCount: 0,
        status: 'failed',
        progress: 0,
        message: `文件大小超过 ${maxSizeMB}MB 限制`,
      })
      setToast({ type: 'error', message: `文件大小超过 ${maxSizeMB}MB 限制` })
      return
    }

    setCurrentUpload({
      taskId: '',
      fileName: file.name,
      fileCount: 0,
      status: 'uploading',
      progress: 10,
      message: '正在上传文件...',
    })

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await axios.post('/api/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 600000, // 10 分钟超时，大文件上传+解压需要时间
        maxContentLength: Infinity,
        maxBodyLength: Infinity,
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const uploadPercent = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            setCurrentUpload((previous) => ({
              ...previous!,
              progress: Math.min(uploadPercent, 20),
              message: uploadPercent < 100 ? `正在上传... ${uploadPercent}%` : '上传完成，正在解压...',
            }))
          }
        },
      })

      const { task_id: taskId, file_list: fileList } = response.data

      setCurrentUpload((previous) => ({
        ...previous!,
        taskId,
        fileCount: fileList.length,
        status: 'processing',
        progress: 25,
        message: '上传成功，AI 正在解析代码结构...',
      }))

      startPollingStatus(taskId, file.name)
    } catch (error: any) {
      setCurrentUpload((previous) => ({
        ...previous!,
        status: 'failed',
        progress: 0,
        message: error.response?.data?.detail || '上传失败，请检查网络后重试',
      }))
      setToast({ type: 'error', message: error.response?.data?.detail || '上传失败，请检查网络后重试' })
    }
  }

  const startPollingStatus = (taskId: string, fileName: string) => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current)
    }

    pollingRef.current = setInterval(async () => {
      try {
        const statusResponse = await axios.get(`/api/task/status?task_id=${taskId}`)
        const { status, progress, message } = statusResponse.data

        if (status === 'completed') {
          clearInterval(pollingRef.current!)
          pollingRef.current = null

          setCurrentUpload((previous) => ({
            ...previous!,
            status: 'completed',
            progress: 100,
            message: '解析完成！架构图已生成 🎉',
          }))

          onUploadComplete(taskId, fileName)

          setTimeout(() => {
            setCurrentUpload(null)
          }, 2500)
        } else if (status === 'failed') {
          clearInterval(pollingRef.current!)
          pollingRef.current = null

          setCurrentUpload((previous) => ({
            ...previous!,
            status: 'failed',
            progress: 0,
            message: message || '解析失败，请重试',
          }))
          setToast({ type: 'error', message: message || '解析失败，请重试' })
        } else {
          setCurrentUpload((previous) => ({
            ...previous!,
            progress: progress || previous!.progress,
            message: message || previous!.message,
          }))
        }
      } catch {
        clearInterval(pollingRef.current!)
        pollingRef.current = null

        setCurrentUpload((previous) => ({
          ...previous!,
          status: 'failed',
          message: '网络连接中断，请重试',
        }))
        setToast({ type: 'error', message: '网络连接中断，请重试' })
      }
    }, 2000)
  }

  const dismissUpload = () => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current)
      pollingRef.current = null
    }
    setCurrentUpload(null)
  }

  const isUploading = currentUpload?.status === 'uploading' || currentUpload?.status === 'processing'

  return (
    <div className="w-full">
      {/* Toast Notification */}
      {toast && (
        <Toast
          type={toast.type}
          message={toast.message}
          onClose={() => setToast(null)}
        />
      )}
      
      {/* Upload Drop Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !isUploading && fileInputRef.current?.click()}
        className={`
          relative overflow-hidden border-2 border-dashed p-16
          transition-all duration-300 ease cursor-pointer group rounded-none
          ${isDragOver
            ? 'border-white bg-white/5'
            : isUploading
              ? 'border-white/40 bg-white/5 cursor-default'
              : 'border-white/30 hover:border-white hover:bg-white/5'
          }
        `}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".zip"
          onChange={handleFileSelect}
          className="hidden"
        />

        {!currentUpload ? (
          /* Default state */
          <div className="flex flex-col items-center gap-4 relative z-10">
            <div className="text-6xl mb-6">📁</div>
            <div className="text-center">
              <p className="text-2xl font-bold mb-4">
                拖拽文件到这里
              </p>
              <p className="opacity-60 mb-8">
                或 <span className="font-semibold underline decoration-white/40 underline-offset-2">点击选择文件</span>，支持 ZIP 格式
              </p>
            </div>
            <div className="flex items-center gap-2 px-4 py-1.5 bg-white/10 rounded-full">
              <FileArchive className="w-3.5 h-3.5" />
              <span className="text-xs">最大 500MB · 自动解析生成架构图</span>
            </div>
          </div>
        ) : (
          /* Upload progress state */
          <div className="flex flex-col items-center gap-4 relative z-10">
            <div className="flex items-center gap-3 w-full max-w-md">
              {currentUpload.status === 'failed' ? (
                <div className="w-12 h-12 bg-red-500/20 flex items-center justify-center flex-shrink-0">
                  <AlertCircle className="w-6 h-6 text-red-400" />
                </div>
              ) : currentUpload.status === 'completed' ? (
                <div className="w-12 h-12 bg-emerald-500/20 flex items-center justify-center flex-shrink-0">
                  <CheckCircle2 className="w-6 h-6 text-emerald-400" />
                </div>
              ) : (
                <div className="w-12 h-12 bg-white/10 flex items-center justify-center flex-shrink-0">
                  <Loader2 className="w-6 h-6 animate-spin" />
                </div>
              )}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold truncate">
                  {currentUpload.fileName}
                </p>
                <p className="text-xs opacity-60 mt-0.5">
                  {currentUpload.message}
                </p>
                {currentUpload.status === 'processing' && currentUpload.progress > 0 && (
                  <div className="mt-2 h-1.5 bg-white/20 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-white rounded-full transition-all duration-300"
                      style={{ width: `${currentUpload.progress}%` }}
                    />
                  </div>
                )}
              </div>
              {currentUpload.status !== 'uploading' && currentUpload.status !== 'processing' && (
                <button
                  onClick={dismissUpload}
                  className="p-2 hover:bg-white/10 transition-colors cursor-pointer"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
