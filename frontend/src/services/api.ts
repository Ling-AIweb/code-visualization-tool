import axios from 'axios'
import type {
  UploadResponse,
  TaskStatusResponse,
  GenerateScriptRequest,
  GenerateScriptResponse,
  ProjectDetails
} from '../types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response) {
      // 服务器返回错误状态码
      console.error('API Error:', error.response.data)
      throw new Error(error.response.data.detail || error.response.data.message || '请求失败')
    } else if (error.request) {
      // 请求已发出但没有收到响应
      console.error('Network Error:', error.message)
      throw new Error('网络连接失败，请检查网络设置')
    } else {
      // 请求配置出错
      console.error('Request Error:', error.message)
      throw new Error('请求配置错误')
    }
  }
)

// 上传代码压缩包
export const uploadCode = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await apiClient.post<UploadResponse>('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    timeout: 300000,
    onUploadProgress: (progressEvent) => {
      if (progressEvent.total) {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        console.log(`Upload progress: ${progress}%`)
      }
    },
  })

  return response.data
}

// 获取任务状态
export const getTaskStatus = async (taskId: string): Promise<TaskStatusResponse> => {
  const response = await apiClient.get<TaskStatusResponse>(`/task/status?task_id=${taskId}`)
  return response.data
}

// 获取项目详情（聚合多个接口数据）
export const getProjectDetails = async (taskId: string): Promise<ProjectDetails> => {
  // 先获取任务状态
  const statusResponse = await apiClient.get<TaskStatusResponse>(`/task/status?task_id=${taskId}`)
  const taskStatus = statusResponse.data

  const result: ProjectDetails = {
    taskId,
    fileName: taskStatus.message || '项目',
    structure: undefined as any,
    architecture: undefined as any,
    chatScript: undefined as any,
    termDictionary: [],
    status: taskStatus.status === 'uploading' ? 'processing' : taskStatus.status as ProjectDetails['status'],
    progress: taskStatus.progress,
  }

  // 如果任务未完成，直接返回状态信息
  if (taskStatus.status !== 'completed') {
    return result
  }

  // 任务完成后，并行获取结构和架构可视化数据
  const [structureResult, architectureResult] = await Promise.allSettled([
    apiClient.get(`/project/structure?task_id=${taskId}`),
    apiClient.get(`/architecture/visualization?task_id=${taskId}`),
  ])

  // 填充项目结构
  if (structureResult.status === 'fulfilled') {
    const structureData = structureResult.value.data
    result.structure = structureData.tree
    result.architecture = { mermaidCode: structureData.mermaid_diagram || '' }
  }

  // 填充架构可视化数据（分层 + 群聊剧本 + 术语词典）
  if (architectureResult.status === 'fulfilled') {
    const visualizationData = architectureResult.value.data

    // 将 layers 数据合并到 architecture 中
    const layers = visualizationData.layers || []
    if (layers.length > 0) {
      result.architecture = {
        ...result.architecture,
        mermaidCode: result.architecture?.mermaidCode || '',
        layers,
      }
    }

    const scenarios = visualizationData.scenarios || []
    if (scenarios.length > 0) {
      result.chatScript = {
        scenarios: scenarios.map((scenario: any) => ({
          id: scenario.id || `scenario-${scenarios.indexOf(scenario)}`,
          title: scenario.title || '',
          description: scenario.description || '',
          characters: scenario.characters || [],
          dialogues: (scenario.messages || []).map((message: any) => ({
            from: message.from,
            to: message.to,
            content: message.content,
            codeRef: message.codeRef,
          })),
        })),
      }
    }

    const techTerms = visualizationData.techTerms || []
    if (techTerms.length > 0) {
      result.termDictionary = techTerms.map((term: any) => ({
        term: term.term || '',
        laymanExplanation: term.plainExplanation || '',
        technicalExplanation: term.description || '',
        examples: term.examples || [],
      }))
    }
  }

  return result
}

// 生成群聊剧本
export const generateChatScript = async (
  request: GenerateScriptRequest
): Promise<GenerateScriptResponse> => {
  const response = await apiClient.post<GenerateScriptResponse>('/chat/generate', request)
  return response.data
}

// 获取术语解释
export const explainTerm = async (term: string, codeSnippet?: string): Promise<any> => {
  const params: any = { term }
  if (codeSnippet) {
    params.code_snippet = codeSnippet
  }
  const response = await apiClient.get('/explain/term', { params })
  return response.data
}

// 获取项目结构
export const getProjectStructure = async (taskId: string): Promise<any> => {
  const response = await apiClient.get(`/project/structure?task_id=${taskId}`)
  return response.data
}

export default apiClient
