import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, AlertCircle, Home, Layers, MessageSquare, BookOpen } from 'lucide-react'
import ProjectStructureTree from '../components/ProjectStructureTree'
import ArchitectureMap from '../components/ArchitectureMap'
import ChatScript from '../components/ChatScript'
import TermDictionary from '../components/TermDictionary'
import { getProjectDetails } from '../services/api'
import { ProjectDetails } from '../types'

type TabType = 'structure' | 'architecture' | 'chat' | 'dictionary'

export default function ProjectDetailsPage() {
  const { taskId } = useParams<{ taskId: string }>()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState<TabType>('structure')
  const [projectDetails, setProjectDetails] = useState<ProjectDetails | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!taskId) {
      setError('项目 ID 缺失')
      setLoading(false)
      return
    }

    fetchProjectDetails()
  }, [taskId])

  // 当任务处于 processing 状态时，自动轮询直到完成
  useEffect(() => {
    if (!projectDetails || projectDetails.status !== 'processing') return

    const pollingInterval = setInterval(async () => {
      try {
        const details = await getProjectDetails(taskId!)
        setProjectDetails(details)
        if (details.status !== 'processing') {
          clearInterval(pollingInterval)
        }
      } catch {
        clearInterval(pollingInterval)
      }
    }, 3000)

    return () => clearInterval(pollingInterval)
  }, [projectDetails?.status, taskId])

  const fetchProjectDetails = async () => {
    try {
      setLoading(true)
      setError(null)
      const details = await getProjectDetails(taskId!)
      setProjectDetails(details)
    } catch (err: any) {
      setError(err.message || '获取项目详情失败')
    } finally {
      setLoading(false)
    }
  }

  const tabs = [
    { id: 'structure' as TabType, label: '项目结构', icon: Layers },
    { id: 'architecture' as TabType, label: '架构图', icon: Home },
    { id: 'chat' as TabType, label: '群聊剧本', icon: MessageSquare },
    { id: 'dictionary' as TabType, label: '术语词典', icon: BookOpen },
  ]

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-white border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-lg opacity-60">正在加载项目详情...</p>
        </div>
      </div>
    )
  }

  if (error || !projectDetails) {
    return (
      <div className="min-h-screen flex items-center justify-center px-6">
        <div className="text-center max-w-md">
          <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="w-8 h-8 text-red-400" />
          </div>
          <h2 className="text-2xl font-bold mb-2">加载失败</h2>
          <p className="opacity-60 mb-6">{error || '无法获取项目详情'}</p>
          <div className="flex gap-4 justify-center">
            <button
              onClick={() => fetchProjectDetails()}
              className="btn-primary px-6 py-3"
            >
              重试
            </button>
            <button
              onClick={() => navigate('/')}
              className="border border-white/20 px-6 py-3 hover:bg-white/10 transition-colors"
            >
              返回首页
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (projectDetails.status === 'processing') {
    return (
      <div className="min-h-screen flex items-center justify-center px-6">
        <div className="text-center max-w-md">
          <div className="w-16 h-16 border-4 border-white border-t-transparent rounded-full animate-spin mx-auto mb-6"></div>
          <h2 className="text-2xl font-bold mb-2">AI 正在解析代码</h2>
          <p className="opacity-60 mb-6">{projectDetails.progress}% 完成</p>
          <div className="w-full h-2 bg-white/20 rounded-full overflow-hidden mb-4">
            <div
              className="h-full bg-white transition-all duration-500 rounded-full"
              style={{ width: `${projectDetails.progress}%` }}
            />
          </div>
          <p className="text-sm opacity-40">解析完成后将自动跳转...</p>
        </div>
      </div>
    )
  }

  if (projectDetails.status === 'failed') {
    return (
      <div className="min-h-screen flex items-center justify-center px-6">
        <div className="text-center max-w-md">
          <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="w-8 h-8 text-red-400" />
          </div>
          <h2 className="text-2xl font-bold mb-2">解析失败</h2>
          <p className="opacity-60 mb-6">代码解析过程中出现错误，请重新上传</p>
          <button
            onClick={() => navigate('/')}
            className="btn-primary px-6 py-3"
          >
            返回首页
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen">
      {/* 顶部导航栏 */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-black/80 backdrop-blur-md border-b border-white/10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <button
              onClick={() => navigate('/')}
              className="flex items-center gap-2 text-sm opacity-60 hover:opacity-100 transition-opacity"
            >
              <ArrowLeft className="w-4 h-4" />
              返回首页
            </button>
            
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center">
                <span className="text-black font-bold text-sm">AI</span>
              </div>
              <span className="font-semibold">{projectDetails.fileName}</span>
            </div>
          </div>
        </div>
      </nav>

      {/* 主内容区 */}
      <div className="pt-32 px-6 pb-12">
        <div className="max-w-7xl mx-auto">
          {/* 页面标题 */}
          <div className="mb-8">
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              代码可视化
            </h1>
            <p className="text-lg opacity-60">
              用生活化的方式理解代码逻辑
            </p>
          </div>

          {/* Tab 切换 */}
          <div className="mb-8">
            <div className="flex gap-2 border-b border-white/20">
              {tabs.map((tab) => {
                const Icon = tab.icon
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`
                      flex items-center gap-2 px-6 py-3 transition-all duration-300
                      ${activeTab === tab.id
                        ? 'text-white border-b-2 border-white'
                        : 'opacity-60 hover:opacity-100 hover:bg-white/5'
                      }
                    `}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="font-medium">{tab.label}</span>
                  </button>
                )
              })}
            </div>
          </div>

          {/* Tab 内容 */}
          <div className="animate-fade-in">
            {activeTab === 'structure' && projectDetails.structure && (
              <ProjectStructureTree
                structure={projectDetails.structure}
                onNodeClick={(node) => {
                  console.log('Clicked node:', node)
                }}
              />
            )}

            {activeTab === 'architecture' && projectDetails.architecture && (
              <ArchitectureMap graph={projectDetails.architecture} />
            )}

            {activeTab === 'chat' && projectDetails.chatScript && (
              <ChatScript script={projectDetails.chatScript} />
            )}

            {activeTab === 'dictionary' && projectDetails.termDictionary && (
              <TermDictionary terms={projectDetails.termDictionary} />
            )}
          </div>

          {/* 底部操作栏 */}
          <div className="mt-12 pt-8 border-t border-white/10 flex items-center justify-between">
            <div className="text-sm opacity-40">
              {projectDetails.status === 'completed' ? '✅ 解析完成' : '⏳ 处理中'}
            </div>
            <button
              onClick={fetchProjectDetails}
              className="text-sm px-4 py-2 border border-white/20 hover:bg-white/10 transition-colors"
            >
              刷新数据
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
