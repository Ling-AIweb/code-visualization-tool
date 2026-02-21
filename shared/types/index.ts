// 角色类型
export interface Character {
  id: string;
  name: string;
  role: string;
  personality: string;
  avatar?: string;
}

// 对话类型
export interface Dialogue {
  from: string;
  to: string;
  content: string;
  code_ref: string;
  timestamp?: number;
}

// 剧本类型
export interface Script {
  scenario: string;
  characters: Character[];
  dialogues: Dialogue[];
}

// 项目结构类型
export interface ProjectNode {
  name: string;
  type: 'file' | 'folder';
  path: string;
  description?: string;
  children?: ProjectNode[];
}

// 上传响应类型
export interface UploadResponse {
  task_id: string;
  status: 'processing' | 'completed' | 'failed';
  message: string;
}

// 项目结构响应类型
export interface ProjectStructureResponse {
  tree: ProjectNode;
  mermaid_diagram: string;
}

// 剧本生成请求类型
export interface GenerateScriptRequest {
  scenario: string;
  task_id: string;
}

// 术语解释请求类型
export interface ExplainTermRequest {
  code_snippet: string;
}

// 术语解释响应类型
export interface ExplainTermResponse {
  term: string;
  plain_explanation: string;
  analogy: string;
}
