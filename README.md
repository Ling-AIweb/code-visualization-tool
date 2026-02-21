# 代码逻辑可视化工具

一款将复杂代码库转化为"大白话"和"拟人化群聊"的 AI 可视化解析工具。

## 项目结构

```
.
├── frontend/          # React 前端应用
│   ├── src/
│   │   ├── components/  # 组件
│   │   ├── pages/       # 页面
│   │   ├── services/    # API 服务
│   │   ├── types/       # TypeScript 类型
│   │   └── utils/       # 工具函数
│   └── package.json
├── backend/           # FastAPI 后端应用
│   ├── app/
│   │   ├── api/         # API 路由
│   │   ├── core/        # 核心配置
│   │   ├── models/      # 数据模型
│   │   ├── services/    # 业务服务
│   │   └── utils/       # 工具函数
│   ├── main.py
│   └── requirements.txt
└── shared/            # 共享类型定义
    └── types/
```

## 快速开始

### 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入 API_KEY 等配置

# 启动服务
python main.py
```

后端服务将在 http://localhost:8000 启动

### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env

# 启动开发服务器
npm run dev
```

前端应用将在 http://localhost:3000 启动

## 功能特性

- **代码解析**: 支持 ZIP 项目上传，智能扫描目录结构
- **架构可视化**: 自动生成 Mermaid 架构图
- **群聊剧本**: 将代码交互转化为拟人化对话
- **白话解释**: 用生活化类比解释技术术语

## 技术栈

- **前端**: React 18 + TypeScript + Tailwind CSS + Vite
- **后端**: FastAPI + Python 3.10+
- **AI**: LangChain + OpenAI/Gemini
- **数据库**: ChromaDB (向量数据库)

## API 文档

启动后端服务后，访问 http://localhost:8000/docs 查看 Swagger API 文档

## 开发规范

- 遵循 PEP 8 Python 代码规范
- 使用 TypeScript 严格模式
- 组件采用 Hooks 模式
- 提交前运行 linter 检查

## 许可证

MIT License
