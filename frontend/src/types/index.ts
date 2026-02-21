// 项目结构类型
export interface ProjectStructure {
  name: string
  path: string
  type: 'folder' | 'file'
  children?: ProjectStructure[]
  description?: string
}

// 角色/组件类型
export interface Character {
  id: string
  name: string
  role: string
  avatar?: string
  personality: string
}

// 对话消息类型
export interface DialogueMessage {
  from: string
  to: string
  content: string
  codeRef?: string
  timestamp?: number
}

// 场景项类型（单个操作链路的群聊剧本）
export interface ScenarioItem {
  id: string
  title: string
  description: string
  characters: Character[]
  dialogues: DialogueMessage[]
}

// 群聊剧本类型（支持多场景）
export interface ChatScript {
  scenarios: ScenarioItem[]
}

// 术语解释类型
export interface TermExplanation {
  term: string
  laymanExplanation: string
  technicalExplanation: string
  examples: string[]
}

// 架构层级组件类型
export interface ArchitectureComponent {
  name: string
  role: string
  description: string
  plainExplanation: string
  files?: string[]
}

// 架构层级类型
export interface ArchitectureLayer {
  id: string
  name: string
  description: string
  plainExplanation: string
  color?: string
  bgColor?: string
  borderColor?: string
  components: ArchitectureComponent[]
}

// 架构图类型
export interface ArchitectureGraph {
  mermaidCode: string
  description?: string
  layers?: ArchitectureLayer[]
}

// 项目详情类型
export interface ProjectDetails {
  taskId: string
  fileName: string
  structure: ProjectStructure
  architecture: ArchitectureGraph
  chatScript: ChatScript
  termDictionary: TermExplanation[]
  status: 'processing' | 'completed' | 'failed'
  progress: number
}

// API 响应类型
export interface UploadResponse {
  task_id: string
  file_list: string[]
}

export interface TaskStatusResponse {
  status: 'uploading' | 'processing' | 'completed' | 'failed'
  progress: number
  message: string
  project_details?: ProjectDetails
}

export interface GenerateScriptRequest {
  task_id: string
  scenario?: string
}

export interface GenerateScriptResponse {
  scenario: string
  characters: Character[]
  dialogues: DialogueMessage[]
}
