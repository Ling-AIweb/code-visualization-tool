"""
架构可视化服务
生成面向外行人的架构分层、服务聊天剧本和技术名词解释。
遵循 AGENTS.md 的生活化比喻原则。
"""
import logging
from typing import Dict, Any, List, Optional

from app.services.llm_service import llm_service, LLMError
from app.services.project_service import project_service

logger = logging.getLogger(__name__)

class ArchitectureService:
    """架构可视化服务，生成外行人能看懂的架构解释"""

    def __init__(self) -> None:
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get_cached_visualization(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取缓存的可视化数据。

        Args:
            task_id: 项目任务 ID

        Returns:
            缓存的数据，如果不存在则返回 None
        """
        return self._cache.get(task_id)

    def clear_cache(self, task_id: str) -> None:
        """
        清除指定任务的缓存。

        Args:
            task_id: 项目任务 ID
        """
        self._cache.pop(task_id, None)

    async def generate_architecture_visualization(
        self, task_id: str
    ) -> Dict[str, Any]:
        """
        生成完整的架构可视化数据，包括分层、场景和术语。
        优先返回缓存结果，避免重复调用 LLM。

        Args:
            task_id: 项目任务 ID

        Returns:
            包含 layers, scenarios, techTerms 的字典
        """
        # 优先返回缓存
        cached = self.get_cached_visualization(task_id)
        if cached is not None:
            logger.info("命中缓存，跳过 LLM 调用: task_id=%s", task_id)
            return cached

        # 获取项目数据
        project_data = project_service.get_project_data(task_id)
        file_summaries = project_service.get_file_summaries(task_id)

        if not project_data:
            raise ValueError("项目未找到或未完成解析")

        # 并行生成三个部分的数据
        layers_result = await self._generate_layers(file_summaries)
        scenarios_result = await self._generate_scenarios(file_summaries)
        terms_result = await self._generate_tech_terms(file_summaries)

        result = {
            "layers": layers_result,
            "scenarios": scenarios_result,
            "techTerms": terms_result,
        }

        # 写入缓存
        self._cache[task_id] = result
        logger.info("已缓存可视化结果: task_id=%s", task_id)

        return result

    async def _generate_layers(
        self, file_summaries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        生成架构分层信息。

        Args:
            file_summaries: 文件摘要列表

        Returns:
            层级列表
        """
        system_prompt = (
            "你是一个架构师，擅长用大白话解释软件架构。\n"
            "你的任务是把项目的代码结构，翻译成外行人也能懂的分层架构。\n\n"
            "规则：\n"
            "1. 按照典型的三层架构（前端展示层、业务逻辑层、数据存储层）来分层\n"
            "2. 如果项目比较复杂，可以细分到 4-5 层\n"
            "3. 每层要有：\n"
            "   - name: 层级名称（如「前端展示层」）\n"
            "   - description: 一句话技术描述\n"
            "   - plainExplanation: 用大白话解释这层是干嘛的（像跟朋友聊天一样）\n"
            "   - components: 这层包含的主要组件列表\n"
            "4. 组件要有：\n"
            "   - name: 组件名称\n"
            "   - role: 技术角色（如 Controller、Service、Database）\n"
            "   - description: 技术描述\n"
            "   - plainExplanation: 用大白话解释这个组件是干嘛的\n"
            "   - files: 该组件对应的代码文件路径列表（从项目根目录开始的相对路径）\n"
            "5. 禁止使用技术黑话，必须用生活化类比\n"
            "6. 返回 JSON 格式的 layers 数组\n\n"
            "返回格式示例：\n"
            "[\n"
            "  {\n"
            '    "id": "layer-0",\n'
            '    "name": "前端展示层",\n'
            '    "description": "用户界面和交互逻辑",\n'
            '    "plainExplanation": "这一层就像餐厅的大堂，负责接待客人、展示菜单、接收点单。用户直接接触的就是这一层。",\n'
            '    "color": "from-blue-400 to-blue-600",\n'
            '    "bgColor": "bg-blue-50",\n'
            '    "borderColor": "border-blue-200",\n'
            '    "components": [\n'
            "      {\n"
            '        "name": "前端界面",\n'
            '        "role": "Frontend",\n'
            '        "description": "用户界面组件",\n'
            '        "plainExplanation": "就像餐厅的装修和菜单，负责把内容展示给用户看。",\n'
            '        "files": ["frontend/src/pages/HomePage.tsx", "frontend/src/components/Header.tsx"]\n'
            "      }\n"
            "    ]\n"
            "  }\n"
            "]"
        )

        # 构建项目上下文
        project_context = self._build_project_context(file_summaries)

        user_prompt = (
            f"以下是一个项目的代码结构：\n\n{project_context}\n\n"
            "请根据以上代码结构，生成这个项目的架构分层信息。"
        )

        try:
            result = await llm_service.generate_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.7,
                max_tokens=8000,
            )

            # 确保返回的是列表
            if isinstance(result, dict) and "layers" in result:
                layers = result["layers"]
            elif isinstance(result, list):
                layers = result
            else:
                layers = []

            # 为每层添加必需的样式字段
            return self._enrich_layers_with_styles(layers)

        except LLMError as error:
            logger.warning("LLM 分层生成失败，使用默认模板: %s", str(error))
            return self._generate_default_layers()

    async def _generate_scenarios(
        self, file_summaries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        生成核心业务场景的群聊剧本。

        Args:
            file_summaries: 文件摘要列表

        Returns:
            场景列表
        """
        system_prompt = (
            "你是一个编剧，擅长把代码交互写成有趣的群聊对话。\n"
            "你的任务是基于项目的代码结构，生成 3-5 个核心业务场景的群聊剧本。\n\n"
            "规则：\n"
            "1. 识别项目的核心功能场景（如用户登录、下单、搜索等）\n"
            "2. 第一个场景必须是最核心的功能\n"
            "3. 每个场景包含：\n"
            "   - id: 场景唯一标识\n"
            "   - title: 场景名称（如「用户付款」）\n"
            "   - description: 一句话描述这个场景\n"
            "   - characters: 参与的角色列表\n"
            "   - messages: 对话消息列表\n"
            "4. 角色包含：\n"
            "   - id: 唯一标识\n"
            "   - name: 角色昵称（如「前端小美」）\n"
            "   - role: 技术角色（如 Frontend）\n"
            "   - personality: 性格描述\n"
            "   - color: 颜色样式（如 bg-blue-100 text-blue-700 border-blue-300）\n"
            "5. 消息包含：\n"
            "   - id: 消息唯一标识\n"
            "   - from: 发送者角色 ID\n"
            "   - to: 接收者角色 ID\n"
            "   - content: 消息内容（口语化，像同事在群里传话）\n"
            "   - codeRef: 对应的代码位置（如 routes.py:45）\n"
            "6. 对话要反映真实的代码调用流程\n"
            "7. 语言要口语化、有趣，像朋友聊天\n"
            "8. 禁止使用技术黑话\n"
            "9. 返回 JSON 格式的 scenarios 数组\n\n"
            "返回格式示例：\n"
            "[\n"
            "  {\n"
            '    "id": "scenario-0",\n'
            '    "title": "用户付款",\n'
            '    "description": "用户完成支付后，系统更新订单状态",\n'
            '    "characters": [\n'
            '      {\n'
            '        "id": "fe",\n'
            '        "name": "前端小美",\n'
            '        "role": "Frontend",\n'
            '        "personality": "活泼开朗，负责展示界面",\n'
            '        "color": "bg-blue-100 text-blue-700 border-blue-300"\n'
            "      }\n"
            "    ],\n"
            '    "messages": []\n'
            "  }\n"
            "]"
        )

        # 构建项目上下文
        project_context = self._build_project_context(file_summaries)

        user_prompt = (
            f"以下是一个项目的代码结构：\n\n{project_context}\n\n"
            "请根据以上代码结构，识别核心业务场景，并生成对应的群聊剧本。"
        )

        try:
            result = await llm_service.generate_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.8,
                max_tokens=8000,
            )

            # 确保返回的是列表
            if isinstance(result, dict) and "scenarios" in result:
                scenarios = result["scenarios"]
            elif isinstance(result, list):
                scenarios = result
            else:
                scenarios = []

            # 为每个场景添加必需的字段
            return self._enrich_scenarios_with_ids(scenarios)

        except LLMError as error:
            logger.warning("LLM 场景生成失败，使用默认模板: %s", str(error))
            return self._generate_default_scenarios()

    async def _generate_tech_terms(
        self, file_summaries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        生成技术名词的大白话解释。

        Args:
            file_summaries: 文件摘要列表

        Returns:
            术语列表
        """
        system_prompt = (
            "你是一个技术翻译官，擅长把技术术语翻译成大白话。\n"
            "你的任务是从项目的代码中提取技术术语，并给出生活化解释。\n\n"
            "规则：\n"
            "1. 识别项目中使用的关键技术术语（如 API、Database、async、JWT 等）\n"
            "2. 每个术语包含：\n"
            "   - id: 唯一标识\n"
            "   - term: 术语名称\n"
            "   - plainExplanation: 一句话白话解释\n"
            "   - analogy: 生活化类比（以「就像...」开头）\n"
            "   - relatedComponent: 相关的组件（可选）\n"
            "3. 解释要简短有趣，像跟朋友聊天\n"
            "4. 禁止使用技术黑话\n"
            "5. 返回 JSON 格式的 techTerms 数组\n\n"
            "返回格式示例：\n"
            "[\n"
            "  {\n"
            '    "id": "term-0",\n'
            '    "term": "API",\n'
            '    "plainExplanation": "应用程序接口，让不同软件之间可以互相沟通。",\n'
            '    "analogy": "就像餐厅的服务员，负责传递客人的点单给厨房，再把做好的菜端给客人。",\n'
            '    "relatedComponent": "后端服务"\n'
            "  }\n"
            "]"
        )

        # 构建项目上下文
        project_context = self._build_project_context(file_summaries)

        user_prompt = (
            f"以下是一个项目的代码结构：\n\n{project_context}\n\n"
            "请从以上代码中提取关键的技术术语，并给出大白话解释。"
        )

        try:
            result = await llm_service.generate_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.6,
                max_tokens=8000,
            )

            # 确保返回的是列表
            if isinstance(result, dict) and "techTerms" in result:
                terms = result["techTerms"]
            elif isinstance(result, list):
                terms = result
            else:
                terms = []

            # 为每个术语添加必需的字段
            return self._enrich_terms_with_ids(terms)

        except LLMError as error:
            logger.warning("LLM 术语生成失败，使用默认模板: %s", str(error))
            return self._generate_default_terms()

    def _build_project_context(
        self, file_summaries: List[Dict[str, Any]]
    ) -> str:
        """构建项目上下文描述"""
        if not file_summaries:
            return "这是一个空项目。"

        context_parts: List[str] = []
        
        # 只取前 20 个文件，避免 token 过多
        for summary in file_summaries[:20]:
            file_path = summary.get("file_path", "")
            classes = summary.get("classes", [])
            functions = summary.get("functions", [])
            methods = summary.get("methods", [])
            
            part = f"文件：{file_path}"
            if classes:
                part += f"\n  类：{', '.join(classes)}"
            if functions:
                part += f"\n  函数：{', '.join(functions[:8])}"
            if methods:
                part += f"\n  方法：{', '.join(methods[:8])}"
            
            context_parts.append(part)

        return "\n\n".join(context_parts)

    def _enrich_layers_with_styles(
        self, layers: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """为层级添加样式字段"""
        color_schemes = [
            {
                "color": "from-blue-400 to-blue-600",
                "bgColor": "bg-blue-50",
                "borderColor": "border-blue-200"
            },
            {
                "color": "from-violet-400 to-violet-600",
                "bgColor": "bg-violet-50",
                "borderColor": "border-violet-200"
            },
            {
                "color": "from-emerald-400 to-emerald-600",
                "bgColor": "bg-emerald-50",
                "borderColor": "border-emerald-200"
            },
            {
                "color": "from-amber-400 to-amber-600",
                "bgColor": "bg-amber-50",
                "borderColor": "border-amber-200"
            },
            {
                "color": "from-pink-400 to-pink-600",
                "bgColor": "bg-pink-50",
                "borderColor": "border-pink-200"
            },
        ]

        return [
            {
                **layer,
                "id": layer.get("id", f"layer-{index}"),
                "color": layer.get("color", color_schemes[index % len(color_schemes)]["color"]),
                "bgColor": layer.get("bgColor", color_schemes[index % len(color_schemes)]["bgColor"]),
                "borderColor": layer.get("borderColor", color_schemes[index % len(color_schemes)]["borderColor"]),
                "components": layer.get("components", []),
            }
            for index, layer in enumerate(layers)
        ]

    def _enrich_scenarios_with_ids(
        self, scenarios: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """为场景添加必需的字段"""
        character_colors = [
            "bg-blue-100 text-blue-700 border-blue-300",
            "bg-purple-100 text-purple-700 border-purple-300",
            "bg-green-100 text-green-700 border-green-300",
            "bg-orange-100 text-orange-700 border-orange-300",
            "bg-pink-100 text-pink-700 border-pink-300",
            "bg-indigo-100 text-indigo-700 border-indigo-300",
        ]

        return [
            {
                **scenario,
                "id": scenario.get("id", f"scenario-{index}"),
                "characters": [
                    {
                        **char,
                        "id": char.get("id", f"char-{scenario.get('id', index)}-{charIdx}"),
                        "color": char.get("color", character_colors[charIdx % len(character_colors)]),
                    }
                    for charIdx, char in enumerate(scenario.get("characters", []))
                ],
                "messages": [
                    {
                        **msg,
                        "id": msg.get("id", f"msg-{scenario.get('id', index)}-{msgIdx}"),
                    }
                    for msgIdx, msg in enumerate(scenario.get("messages", []))
                ],
            }
            for index, scenario in enumerate(scenarios)
        ]

    def _enrich_terms_with_ids(
        self, terms: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """为术语添加必需的字段"""
        return [
            {
                **term,
                "id": term.get("id", f"term-{index}"),
            }
            for index, term in enumerate(terms)
        ]

    def _generate_default_layers(self) -> List[Dict[str, Any]]:
        """生成默认的分层结构"""
        return [
            {
                "id": "layer-0",
                "name": "前端展示层",
                "description": "用户界面和交互逻辑",
                "plainExplanation": "这一层就像餐厅的大堂，负责接待客人、展示菜单、接收点单。用户直接接触的就是这一层。",
                "color": "from-blue-400 to-blue-600",
                "bgColor": "bg-blue-50",
                "borderColor": "border-blue-200",
                "components": [
                    {
                        "id": "comp-0-0",
                        "name": "前端界面",
                        "role": "Frontend",
                        "description": "React/Vue 组件",
                        "plainExplanation": "就像餐厅的装修和菜单，负责把内容展示给用户看。"
                    }
                ]
            },
            {
                "id": "layer-1",
                "name": "业务逻辑层",
                "description": "处理核心业务规则",
                "plainExplanation": "这一层就像餐厅的厨房，负责处理具体的业务逻辑。前端把用户的请求传过来，这里负责计算、判断、处理。",
                "color": "from-violet-400 to-violet-600",
                "bgColor": "bg-violet-50",
                "borderColor": "border-violet-200",
                "components": [
                    {
                        "id": "comp-1-0",
                        "name": "后端服务",
                        "role": "Service",
                        "description": "业务逻辑处理",
                        "plainExplanation": "就像餐厅的厨师团队，负责按照菜谱（业务规则）来处理订单。"
                    },
                    {
                        "id": "comp-1-1",
                        "name": "接口控制器",
                        "role": "Controller",
                        "description": "接收和分发请求",
                        "plainExplanation": "就像餐厅的服务员，负责把前台的点单传给厨房，再把做好的菜端给客人。"
                    }
                ]
            },
            {
                "id": "layer-2",
                "name": "数据存储层",
                "description": "数据持久化和管理",
                "plainExplanation": "这一层就像餐厅的仓库，负责存储和管理所有的数据。订单信息、用户资料都存在这里。",
                "color": "from-emerald-400 to-emerald-600",
                "bgColor": "bg-emerald-50",
                "borderColor": "border-emerald-200",
                "components": [
                    {
                        "id": "comp-2-0",
                        "name": "数据库",
                        "role": "Database",
                        "description": "数据存储",
                        "plainExplanation": "就像一个巨大的档案室，专门用来存储和管理所有的数据文件。"
                    }
                ]
            }
        ]

    def _generate_default_scenarios(self) -> List[Dict[str, Any]]:
        """生成默认的场景"""
        return [
            {
                "id": "scenario-0",
                "title": "用户操作流程",
                "description": "用户发起操作后，各个模块如何协作完成",
                "characters": [
                    {
                        "id": "char-fe",
                        "name": "前端小美",
                        "role": "Frontend",
                        "personality": "活泼开朗，负责展示界面",
                        "color": "bg-blue-100 text-blue-700 border-blue-300"
                    },
                    {
                        "id": "char-be",
                        "name": "后端阿强",
                        "role": "Backend",
                        "personality": "稳重、逻辑清晰",
                        "color": "bg-purple-100 text-purple-700 border-purple-300"
                    },
                    {
                        "id": "char-db",
                        "name": "数据库老墨",
                        "role": "Database",
                        "personality": "记性好、说话慢",
                        "color": "bg-green-100 text-green-700 border-green-300"
                    }
                ],
                "messages": [
                    {
                        "id": "msg-0-0",
                        "from": "char-fe",
                        "to": "char-be",
                        "content": "用户刚刚点了提交按钮，我这边收到请求了，你帮忙处理一下？",
                        "codeRef": "frontend/src/App.tsx:15"
                    },
                    {
                        "id": "msg-0-1",
                        "from": "char-be",
                        "to": "char-db",
                        "content": "收到！我先验证一下数据对不对，然后去查一下数据库里有没有这个用户。",
                        "codeRef": "backend/app/api/routes.py:23"
                    },
                    {
                        "id": "msg-0-2",
                        "from": "char-db",
                        "to": "char-be",
                        "content": "查到了，这个用户信息都在，你要的数据我给你打包好了。",
                        "codeRef": "backend/app/services/project_service.py:45"
                    },
                    {
                        "id": "msg-0-3",
                        "from": "char-be",
                        "to": "char-fe",
                        "content": "处理完了！结果我发给你了，展示给用户看吧。",
                        "codeRef": "backend/app/api/routes.py:30"
                    }
                ]
            }
        ]

    def _generate_default_terms(self) -> List[Dict[str, Any]]:
        """生成默认的术语"""
        return [
            {
                "id": "term-0",
                "term": "API",
                "plainExplanation": "应用程序接口，让不同软件之间可以互相沟通。",
                "analogy": "就像餐厅的服务员，负责传递客人的点单给厨房，再把做好的菜端给客人。",
                "relatedComponent": "后端服务"
            },
            {
                "id": "term-1",
                "term": "Database",
                "plainExplanation": "数据库，用来存储和管理数据的系统。",
                "analogy": "就像一个巨大的档案室，专门用来存储和管理所有的数据文件。",
                "relatedComponent": "数据存储层"
            },
            {
                "id": "term-2",
                "term": "async/await",
                "plainExplanation": "异步编程模式，让程序可以在等待时去做别的事。",
                "analogy": "就像点外卖，你下单后不用一直等，可以去做别的事，外卖好了再通知你。",
                "relatedComponent": "前端界面"
            },
            {
                "id": "term-3",
                "term": "JSON",
                "plainExplanation": "一种通用的数据格式，让不同系统都能看懂。",
                "analogy": "就像一种通用的表格格式，不管是中国人还是美国人都能看懂的数据格式。",
                "relatedComponent": "接口控制器"
            }
        ]

architecture_service = ArchitectureService()
