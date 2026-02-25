import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { uploadCode } from '../services/api'
import HistoryModal from '../components/HistoryModal'

export default function HomePage() {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [dragOver, setDragOver] = useState(false)
  const [historyModalOpen, setHistoryModalOpen] = useState(false)
  const navigate = useNavigate()

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setFile(event.target.files[0])
    }
  }

  const handleDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault()
    setDragOver(true)
  }, [])

  const handleDragLeave = useCallback(() => {
    setDragOver(false)
  }, [])

  const handleDrop = useCallback((event: React.DragEvent) => {
    event.preventDefault()
    setDragOver(false)
    if (event.dataTransfer.files && event.dataTransfer.files[0]) {
      setFile(event.dataTransfer.files[0])
    }
  }, [])

  const handleUpload = async () => {
    if (!file) return

    setUploading(true)

    try {
      const result = await uploadCode(file)
      navigate(`/project/${result.task_id}`)
    } catch (error: any) {
      console.error('上传失败:', error)
      alert(error.message || '上传失败，请重试')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-black/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
              <span className="text-black font-bold text-lg">AI</span>
            </div>
            <span className="text-xl font-bold tracking-tight">CODE</span>
          </div>
          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-sm hover:text-gray-300 transition-colors">功能</a>
            <a href="#upload" className="text-sm hover:text-gray-300 transition-colors">开始</a>
            <a href="#about" className="text-sm hover:text-gray-300 transition-colors">关于</a>
            <button
              onClick={() => setHistoryModalOpen(true)}
              className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-sm">历史记录</span>
            </button>
          </div>
        </div>
      </nav>
      
      {/* Hero Section */}
      <section className="min-h-screen flex flex-col justify-center px-6 pt-20">
        <div className="max-w-7xl mx-auto w-full">
          <div className="text-center mb-12">
            <p className="text-sm tracking-[0.3em] uppercase mb-6 opacity-60 fade-in">
              AI-Powered Code Understanding
            </p>
            <h1 className="hero-title mb-8 fade-in stagger-1">
              让代码<br/>
              <span className="text-outline">会说话</span>
            </h1>
            <p className="text-lg max-w-2xl mx-auto opacity-80 leading-relaxed fade-in stagger-2">
              将复杂的代码逻辑转化为小白可理解的<br/>
              生活化比喻与拟人化群聊
            </p>
          </div>
          
          <div className="flex flex-col items-center gap-8 fade-in stagger-3">
            <button 
              onClick={() => document.getElementById('upload')?.scrollIntoView({ behavior: 'smooth' })}
              className="btn-primary px-20 py-8 text-2xl font-semibold"
            >
              立即体验
            </button>
          </div>
        </div>
      </section>
      
      {/* Marquee */}
      <div className="border-y border-white/20 py-6 overflow-hidden">
        <div className="marquee-container">
          <div className="marquee-content">
            <span className="marquee-text">
              代码解析 • 架构可视化 • 生活化比喻 • 拟人化群聊 • 
              代码解析 • 架构可视化 • 生活化比喻 • 拟人化群聊 • 
              代码解析 • 架构可视化 • 生活化比喻 • 拟人化群聊 • 
            </span>
          </div>
        </div>
      </div>
      
      {/* Features Section */}
      <section className="py-24 px-6" id="features">
        <div className="max-w-7xl mx-auto">
          <h2 className="section-title mb-16">
            核心功能
          </h2>
          
          <div className="grid md:grid-cols-3 gap-6">
            <div className="card-hover border-thin p-8 cursor-pointer">
              <div className="text-5xl mb-6 card-icon">🏗️</div>
              <h3 className="text-2xl font-bold mb-4">架构分层</h3>
              <p className="opacity-70 card-text leading-relaxed">
                看看系统是怎么一层层搭起来的
              </p>
            </div>
            
            <div className="card-hover border-thin p-8 cursor-pointer">
              <div className="text-5xl mb-6 card-icon">💬</div>
              <h3 className="text-2xl font-bold mb-4">服务聊天</h3>
              <p className="opacity-70 card-text leading-relaxed">
                看看各个模块之间怎么"说话"
              </p>
            </div>
            
            <div className="card-hover border-thin p-8 cursor-pointer">
              <div className="text-5xl mb-6 card-icon">📚</div>
              <h3 className="text-2xl font-bold mb-4">名词解释</h3>
              <p className="opacity-70 card-text leading-relaxed">
                用大白话解释技术术语
              </p>
            </div>
          </div>
        </div>
      </section>
      
      {/* Upload Section */}
      <section className="py-24 px-6 bg-white text-black" id="upload">
        <div className="max-w-7xl mx-auto">
          <h2 className="section-title mb-8 text-left">
            上传代码
          </h2>
          <p className="text-lg opacity-70 mb-12 text-left">
            拖拽你的代码压缩包，AI 将自动生成架构可视化
          </p>
          
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`upload-zone p-16 text-center cursor-pointer ${dragOver ? 'border-white bg-white/5' : ''}`}
          >
            <input
              type="file"
              id="file-upload"
              accept=".zip"
              onChange={handleFileChange}
              className="hidden"
            />
            <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center">
              <div className="text-6xl mb-6">📁</div>
              <p className="text-2xl font-bold mb-4">
                {file ? file.name : '拖拽文件到这里'}
              </p>
              <p className="opacity-60 mb-8">
                {file
                  ? `${(file.size / 1024 / 1024).toFixed(1)} MB · 准备就绪`
                  : '或点击选择文件，支持 ZIP 格式'
                }
              </p>
              {file && (
                <button
                  onClick={(e) => {
                    e.preventDefault()
                    handleUpload()
                  }}
                  disabled={uploading}
                  className="bg-black text-white px-8 py-4 text-lg font-semibold hover:bg-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {uploading ? (
                    <>
                      <div className="w-5 h-5 border-2 border-current border-t-transparent rounded-full animate-spin inline-block mr-2" />
                      正在上传...
                    </>
                  ) : (
                    '开始上传'
                  )}
                </button>
              )}
            </label>
          </div>
        </div>
      </section>
      
      {/* How It Works */}
      <section className="py-24 px-6 pb-[300px]">
        <div className="max-w-7xl mx-auto">
          <h2 className="section-title mb-[120px] text-left">
            如何使用
          </h2>
          
          <div className="grid md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="text-6xl font-bold opacity-20 mb-4">01</div>
              <h3 className="text-xl font-bold mb-2">上传代码</h3>
              <p className="opacity-60">上传 ZIP 格式的代码压缩包</p>
            </div>
            
            <div className="text-center">
              <div className="text-6xl font-bold opacity-20 mb-4">02</div>
              <h3 className="text-xl font-bold mb-2">AI 分析</h3>
              <p className="opacity-60">自动分析代码结构</p>
            </div>
            
            <div className="text-center">
              <div className="text-6xl font-bold opacity-20 mb-4">03</div>
              <h3 className="text-xl font-bold mb-2">生成可视化</h3>
              <p className="opacity-60">生成架构图和群聊剧本</p>
            </div>
            
            <div className="text-center">
              <div className="text-6xl font-bold opacity-20 mb-4">04</div>
              <h3 className="text-xl font-bold mb-2">理解代码</h3>
              <p className="opacity-60">用生活化比喻理解逻辑</p>
            </div>
          </div>
        </div>
      </section>
      
      {/* Example Section */}
      <section className="py-24 px-6 bg-white text-black pb-[200px]" id="about">
        <div className="max-w-7xl mx-auto">
          <h2 className="section-title mb-[100px] text-left">
            示例场景
          </h2>
          
          <div className="grid md:grid-cols-2 gap-8">
            <div className="border order-black/20 p-8 hover:border-black transition-colors">
              <div className="text-4xl mb-4">🍽️</div>
              <h3 className="text-2xl font-bold mb-4">餐厅比喻</h3>
              <p className="opacity-70 leading-relaxed">
                API 接口 = 餐厅前台<br/>
                数据库 = 食材仓库<br/>
                业务逻辑 = 厨师烹饪<br/>
                缓存 = 备菜台
              </p>
            </div>
            
            <div className="border border-black/20 p-8 hover:border-black transition-colors">
              <div className="text-4xl mb-4">🏭</div>
              <h3 className="text-2xl font-bold mb-4">工厂比喻</h3>
              <p className="opacity-70 leading-relaxed">
                函数 = 工位<br/>
                参数 = 原材料<br/>
                返回值 = 成品<br/>
                调用 = 流水线
              </p>
            </div>
          </div>
        </div>
      </section>
      
      {/* Footer */}
      <footer className="py-12 px-6 border-t border-white/20">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center">
              <span className="text-black font-bold text-sm">AI</span>
            </div>
            <span className="font-bold">CODE</span>
          </div>
          <p className="opacity-60 text-sm">© 2026 AI Code Understanding. 让每个人都能看懂代码。</p>
        </div>
      </footer>
      
      {/* History Modal */}
      <HistoryModal
        isOpen={historyModalOpen}
        onClose={() => setHistoryModalOpen(false)}
      />
    </div>
  )
}