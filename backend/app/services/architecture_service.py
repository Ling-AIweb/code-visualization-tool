"""
架构可视化服务
生成面向外行人的架构分层、服务聊天剧本和技术名词解释。
遵循 AGENTS.md 的生活化比喻原则。
"""
import json
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
        logger.info("开始生成架构可视化: task_id=%s", task_id)
        
        # 优先返回缓存
        cached = self.get_cached_visualization(task_id)
        if cached is not None:
            logger.info("命中缓存，跳过 LLM 调用: task_id=%s", task_id)
            return cached

        # 获取项目数据
        project_data = project_service.get_project_data(task_id)
        file_summaries = project_service.get_file_summaries(task_id)

        if not project_data:
            logger.error("项目数据未找到: task_id=%s", task_id)
            raise ValueError("项目未找到或未完成解析")

        logger.info("获取到文件摘要数量: %d", len(file_summaries))
        
        # 检查 file_summaries 是否为空
        if not file_summaries:
            logger.error("文件摘要为空，无法生成架构可视化数据")
            raise ValueError("文件摘要为空，请确保项目解析已完成")

        # 打印第一个文件摘要的详细信息用于调试
        if file_summaries:
            logger.debug("第一个文件摘要: %s", json.dumps(file_summaries[0], ensure_ascii=False))

        # 并行生成三个部分的数据
        try:
            logger.info("开始生成架构分层...")
            layers_result = await self._generate_layers(file_summaries)
            logger.info("架构分层生成完成，层数: %d", len(layers_result))
        except Exception as e:
            logger.error("架构分层生成失败: %s", str(e), exc_info=True)
            layers_result = self._generate_default_layers()
            logger.warning("使用默认架构分层")

        try:
            logger.info("开始生成场景剧本...")
            scenarios_result = await self._generate_scenarios(file_summaries)
            logger.info("场景剧本生成完成，场景数: %d", len(scenarios_result))
        except Exception as e:
            logger.error("场景剧本生成失败: %s", str(e), exc_info=True)
            scenarios_result = self._generate_default_scenarios()
            logger.warning("使用默认场景剧本")

        try:
            logger.info("开始生成术语词典...")
            terms_result = await self._generate_tech_terms(file_summaries)
            logger.info("术语词典生成完成，术语数: %d", len(terms_result))
        except Exception as e:
            logger.error("术语词典生成失败: %s", str(e), exc_info=True)
            terms_result = self._generate_default_terms()
            logger.warning("使用默认术语词典")

        result = {
            "layers": layers_result,
            "scenarios": scenarios_result,
            "techTerms": terms_result,
        }

        # 写入缓存
        self._cache[task_id] = result
        logger.info("架构可视化生成完成并已缓存: task_id=%s", task_id)
        logger.info("结果摘要: layers=%d, scenarios=%d, techTerms=%d", 
                   len(layers_result), len(scenarios_result), len(terms_result))

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
            "# 角色\n"
            "你是一位「代码翻译官」，专门将复杂的技术架构翻译成产品经理、运营人员也能听懂的「大白话」。\n"
            "你的目标读者是：完全没有技术背景的小白 PM/运营、初学者。\n\n"
            "# 任务\n"
            "分析项目的代码结构，生成 3-5 个架构分层，每个分层用生活化的场景来比喻。\n\n"
            "# 核心规则（必须严格遵守）\n\n"
            "1. **生活化类比**：\n"
            "   - 前端展示层 → 餐厅大堂/店铺橱窗\n"
            "   - 接口控制器 → 服务员/传声筒\n"
            "   - 业务逻辑层 → 厨房/加工车间\n"
            "   - 数据库 → 档案室/仓库\n"
            "   - 缓存 → 备忘录/常用物品\n"
            "   - 消息队列 → 待办事项/传单\n\n"
            "2. **禁止技术黑话**（绝对不能出现的词）：\n"
            "   - ❌ MVC、RESTful、ORM、IoC、DI、AOP\n"
            "   - ❌ 中间件、拦截器、适配器、装饰器\n"
            "   - ❌ 异步、同步、并发、多线程\n"
            "   - ❌ 事务、锁、索引、主键\n"
            "   - ✅ 可以用：接收请求、处理订单、存档案、排队等待\n\n"
            "3. **分层数量**：\n"
            "   - 简单项目：3 层（前端、后端、数据库）\n"
            "   - 复杂项目：4-5 层（增加网关、缓存、消息队列等）\n\n"
            "4. **组件映射**：\n"
            "   - Controller/Router → 服务员/接待员\n"
            "   - Service → 厨师/加工员\n"
            "   - Repository/DAO → 档案管理员\n"
            "   - Database → 档案室\n"
            "   - Cache → 备忘本\n"
            "   - Queue → 待办清单\n\n"
            "# 输出格式\n\n"
            "返回 JSON 数组，每个元素包含：\n"
            "- id: 唯一标识（layer-0, layer-1...）\n"
            "- name: 层级名称（如「前端展示层」）\n"
            "- description: 一句话技术描述（给开发看）\n"
            "- plainExplanation: 大白话解释（给小白看，必须用生活化比喻）\n"
            "- components: 组件列表（每个组件包含 name/role/description/plainExplanation/files）\n\n"
            "# Few-Shot 示例\n\n"
            "## 示例 1：电商系统\n"
            "```json\n"
            "[\n"
            "  {\n"
            '    "id": "layer-0",\n'
            '    "name": "前端展示层",\n'
            '    "description": "React/Vue 用户界面",\n'
            '    "plainExplanation": "就像电商平台的店铺橱窗，负责展示商品图片、价格，接收顾客的点击和下单操作。",\n'
            '    "components": [\n'
            "      {\n"
            '        "name": "商品页面",\n'
            '        "role": "Frontend",\n'
            '        "description": "商品详情页组件",\n'
            '        "plainExplanation": "就像商品卡片，展示商品照片、价格、评论，让顾客决定买不买。",\n'
            '        "files": ["frontend/src/pages/Product.tsx"]\n'
            "      }\n"
            "    ]\n"
            "  },\n"
            "  {\n"
            '    "id": "layer-1",\n'
            '    "name": "业务逻辑层",\n'
            '    "description": "订单处理服务",\n'
            '    "plainExplanation": "就像厨房，收到顾客点单后，负责检查库存、计算价格、安排发货。",\n'
            '    "components": [\n'
            "      {\n"
            '        "name": "订单服务",\n'
            '        "role": "Service",\n'
            '        "description": "订单创建和状态管理",\n'
            '        "plainExplanation": "就像厨房的厨师长，负责核对订单、安排做菜、打包外卖。",\n'
            '        "files": ["backend/app/services/order_service.py"]\n'
            "      }\n"
            "    ]\n"
            "  }\n"
            "]\n"
            "```"
        )

        # 构建项目上下文
        project_context = self._build_project_context(file_summaries)

        user_prompt = (
            f"以下是一个项目的代码结构：\n\n{project_context}\n\n"
            "请根据以上代码结构，生成这个项目的架构分层信息。"
        )

        try:
            logger.info("调用 LLM 生成架构分层，文件数: %d", len(file_summaries))
            result = await llm_service.generate_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.7,
                max_tokens=8000,
            )
            logger.info("LLM 返回结果类型: %s", type(result))

            # 确保返回的是列表
            if isinstance(result, dict) and "layers" in result:
                layers = result["layers"]
                logger.info("从字典中提取 layers，数量: %d", len(layers))
            elif isinstance(result, list):
                layers = result
                logger.info("直接使用列表，数量: %d", len(layers))
            else:
                logger.warning("LLM 返回格式异常，使用默认分层")
                layers = []

            # 为每层添加必需的样式字段
            return self._enrich_layers_with_styles(layers)

        except LLMError as error:
            logger.error("LLM 分层生成失败，使用默认模板: %s", str(error), exc_info=True)
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
            "# 角色\n"
            "你是一位「代码编剧」，擅长将枯燥的代码调用流程，写成生动有趣的群聊对话剧本。\n"
            "你的目标是：让小白 PM/运营通过看对话，就能理解代码是怎么跑起来的。\n\n"
            "# 任务\n"
            "分析项目的代码结构，识别 3-5 个核心业务场景，为每个场景生成群聊剧本。\n\n"
            "# 角色设定（必须使用）\n\n"
            "## 标准角色库\n"
            "- **前端小美**（Frontend）：活泼开朗，负责展示界面，说话带表情符号\n"
            "- **服务员阿强**（Controller/Router）：稳重靠谱，负责接收请求、分发任务\n"
            "- **厨师老王**（Service）：技术精湛，负责处理业务逻辑\n"
            "- **档案管理员老墨**（Database）：记性好但说话慢，负责存取数据\n"
            "- **备忘本小本**（Cache）：反应快，负责临时存储常用信息\n"
            "- **传单员小李**（Queue）：负责排队处理任务，有条不紊\n\n"
            "# 对话风格规则\n\n"
            "1. **口语化表达**：\n"
            "   - ✅ 「收到！」「搞定！」「稍等哈~」「查一下哈」\n"
            "   - ✅ 「@档案管理员，帮我查下这个用户的信息」\n"
            "   - ❌ 「请求已接收，正在处理数据...」\n"
            "   - ❌ 「执行数据库查询操作中...」\n\n"
            "2. **反映真实流程**：\n"
            "   - 前端 → 服务员 → 厨师 → 档案管理员\n"
            "   - 每条消息都要对应代码中的实际调用\n"
            "   - codeRef 必须真实存在（如 routes.py:45）\n\n"
            "3. **生活化比喻**：\n"
            "   - 查询数据 → 「翻档案」「查账本」\n"
            "   - 保存数据 → 「存档」「记下来」\n"
            "   - 处理请求 → 「点单」「做菜」\n"
            "   - 返回结果 → 「上菜」「打包好了」\n\n"
            "4. **禁止技术黑话**（绝对不能出现）：\n"
            "   - ❌ 「调用 API」「执行 SQL」「返回 JSON」\n"
            "   - ❌ 「异步处理」「事务回滚」「索引命中」\n"
            "   - ✅ 「传个话」「查一下档案」「刚才的订单先退回去」\n\n"
            "# 场景选择优先级\n\n"
            "1. **必选场景**（第一个）：最核心的业务流程（如：用户下单、用户登录）\n"
            "2. **推荐场景**：数据查询、订单处理、消息推送\n"
            "3. **避免场景**：配置加载、日志记录、健康检查\n\n"
            "# Few-Shot 示例\n\n"
            "## 示例：用户下单场景\n"
            "```json\n"
            "[\n"
            "  {\n"
            '    "id": "scenario-0",\n'
            '    "title": "用户下单",\n'
            '    "description": "用户提交订单后，系统验证库存并创建订单",\n'
            '    "characters": [\n'
            '      {\n'
            '        "id": "fe",\n'
            '        "name": "前端小美",\n'
            '        "role": "Frontend",\n'
            '        "personality": "活泼开朗，负责展示界面",\n'
            '        "color": "bg-blue-100 text-blue-700 border-blue-300"\n'
            "      },\n"
            '      {\n'
            '        "id": "ctrl",\n'
            '        "name": "服务员阿强",\n'
            '        "role": "Controller",\n'
            '        "personality": "稳重靠谱，负责接收请求、分发任务",\n'
            '        "color": "bg-purple-100 text-purple-700 border-purple-300"\n'
            "      },\n"
            '      {\n'
            '        "id": "svc",\n'
            '        "name": "厨师老王",\n'
            '        "role": "Service",\n'
            '        "personality": "技术精湛，负责处理业务逻辑",\n'
            '        "color": "bg-green-100 text-green-700 border-green-300"\n'
            "      },\n"
            '      {\n'
            '        "id": "db",\n'
            '        "name": "档案管理员老墨",\n'
            '        "role": "Database",\n'
            '        "personality": "记性好但说话慢，负责存取数据",\n'
            '        "color": "bg-orange-100 text-orange-700 border-orange-300"\n'
            "      }\n"
            "    ],\n"
            '    "messages": [\n'
            "      {\n"
            '        "id": "msg-0-0",\n'
            '        "from": "fe",\n'
            '        "to": "ctrl",\n'
            '        "content": "用户刚刚点了「提交订单」按钮，订单信息我打包好了，你帮忙处理一下~",\n'
            '        "codeRef": "frontend/src/pages/Order.tsx:88"\n'
            "      },\n"
            "      {\n"
            '        "id": "msg-0-1",\n'
            '        "from": "ctrl",\n'
            '        "to": "svc",\n'
            '        "content": "收到！我先检查一下订单格式对不对...嗯没问题，@厨师老王，这个订单交给你了！",\n'
            '        "codeRef": "backend/app/api/routes.py:45"\n'
            "      },\n"
            "      {\n"
            '        "id": "msg-0-2",\n'
            '        "from": "svc",\n'
            '        "to": "db",\n'
            '        "content": "@档案管理员老墨，帮我查下这个商品还有没有库存？顾客要买 5 个呢",\n'
            '        "codeRef": "backend/app/services/order_service.py:120"\n'
            "      },\n"
            "      {\n"
            '        "id": "msg-0-3",\n'
            '        "from": "db",\n'
            '        "to": "svc",\n'
            '        "content": "查到了...库存还有 10 个，够用。你要的订单信息我记下来了",\n'
            '        "codeRef": "backend/app/repositories/product_repo.py:67"\n'
            "      },\n"
            "      {\n"
            '        "id": "msg-0-4",\n'
            '        "from": "svc",\n'
            '        "to": "ctrl",\n'
            '        "content": "库存没问题，订单创建成功！结果我发给你了",\n'
            '        "codeRef": "backend/app/services/order_service.py:145"\n'
            "      },\n"
            "      {\n"
            '        "id": "msg-0-5",\n'
            '        "from": "ctrl",\n'
            '        "to": "fe",\n'
            '        "content": "搞定！订单号是 #12345，展示给用户看吧~",\n'
            '        "codeRef": "backend/app/api/routes.py:52"\n'
            "      }\n"
            "    ]\n"
            "  }\n"
            "]\n"
            "```"
        )

        # 构建项目上下文
        project_context = self._build_project_context(file_summaries)

        user_prompt = (
            f"以下是一个项目的代码结构：\n\n{project_context}\n\n"
            "请根据以上代码结构，识别核心业务场景，并生成对应的群聊剧本。"
        )

        try:
            logger.info("调用 LLM 生成场景剧本，文件数: %d", len(file_summaries))
            result = await llm_service.generate_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.8,
                max_tokens=8000,
            )
            logger.info("LLM 返回结果类型: %s", type(result))

            # 确保返回的是列表
            if isinstance(result, dict) and "scenarios" in result:
                scenarios = result["scenarios"]
                logger.info("从字典中提取 scenarios，数量: %d", len(scenarios))
            elif isinstance(result, list):
                scenarios = result
                logger.info("直接使用列表，数量: %d", len(scenarios))
            else:
                logger.warning("LLM 返回格式异常，使用默认场景")
                scenarios = []

            # 为每个场景添加必需的字段
            return self._enrich_scenarios_with_ids(scenarios)

        except LLMError as error:
            logger.error("LLM 场景生成失败，使用默认模板: %s", str(error), exc_info=True)
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
            "# 角色\n"
            "你是一位「技术小贴士」，专门把难懂的技术术语，翻译成小白也能听懂的「生活化解释」。\n"
            "你的目标：当用户悬停在专业词汇上时，弹出一条通俗易懂的小贴士。\n\n"
            "# 任务\n"
            "从项目的代码中提取 5-8 个关键技术术语，为每个术语生成生活化的解释和类比。\n\n"
            "# 术语选择优先级\n\n"
            "1. **高频术语**（必选）：API、Database、Cache、JWT、async/await\n"
            "2. **项目特有术语**：根据代码中的 imports 和使用频率选择\n"
            "3. **避免选择**：基础语法（if/else/for）、变量名、函数名\n\n"
            "# 解释规则\n\n"
            "1. **plainExplanation（一句话解释）**：\n"
            "   - 最多 30 字，简洁明了\n"
            "   - 禁止技术黑话（如：接口、协议、同步、异步）\n"
            "   - ✅ 「让不同软件互相沟通的工具」「临时存东西的地方」\n"
            "   - ❌ 「应用程序接口」「异步编程模式」\n\n"
            "2. **analogy（生活化类比）**：\n"
            "   - 必须以「就像...」开头\n"
            "   - 使用餐厅、商店、办公室等生活场景\n"
            "   - ✅ 「就像餐厅的服务员，负责传话」\n"
            "   - ✅ 「就像备忘本，记下常用的东西」\n"
            "   - ❌ 「就像一个中间件...」\n\n"
            "3. **relatedComponent（相关组件）**：\n"
            "   - 指出这个术语在哪个组件里用到\n"
            "   - 用生活化的名称（如：后端服务、订单处理）\n\n"
            "4. **relatedFiles（关联代码文件）**：\n"
            "   - 列出项目中使用了该术语的代码文件路径\n"
            "   - 从项目代码结构中匹配真实存在的文件\n"
            "   - 返回 1-3 个最相关的文件路径\n\n"
            "# 标准术语库（优先使用）\n\n"
            "| 术语 | plainExplanation | analogy |\n"
            "|------|------------------|--------|\n"
            "| API | 让不同软件互相沟通的工具 | 就像餐厅的服务员，负责传话 |\n"
            "| Database | 存储和管理数据的系统 | 就像档案室，专门存档案 |\n"
            "| Cache | 临时存储常用数据的地方 | 就像备忘本，记下常用的东西 |\n"
            "| JWT | 身份验证的通行证 | 就像会员卡，证明你是谁 |\n"
            "| async/await | 等待时去做别事的方式 | 就像点外卖，不用一直等 |\n"
            "| Queue | 排队处理任务的机制 | 就像传单，按顺序处理 |\n"
            "| Middleware | 请求经过的中转站 | 就像安检门，检查过才能进 |\n"
            "| Repository | 管理数据存取的接口 | 就像档案管理员，负责找档案 |\n\n"
            "# Few-Shot 示例\n\n"
            "## 示例\n"
            "```json\n"
            "[\n"
            "  {\n"
            '    "id": "term-0",\n'
            '    "term": "API",\n'
            '    "plainExplanation": "让不同软件互相沟通的工具",\n'
            '    "analogy": "就像餐厅的服务员，负责传递客人的点单给厨房，再把做好的菜端给客人。",\n'
            '    "relatedComponent": "后端服务",\n'
            '    "relatedFiles": ["backend/app/api/routes.py"]\n'
            "  },\n"
            "  {\n"
            '    "id": "term-1",\n'
            '    "term": "Database",\n'
            '    "plainExplanation": "存储和管理数据的系统",\n'
            '    "analogy": "就像一个巨大的档案室，专门用来存储和管理所有的数据文件。",\n'
            '    "relatedComponent": "数据存储层",\n'
            '    "relatedFiles": ["backend/app/models/database.py"]\n'
            "  },\n"
            "  {\n"
            '    "id": "term-2",\n'
            '    "term": "async/await",\n'
            '    "plainExplanation": "等待时去做别事的方式",\n'
            '    "analogy": "就像点外卖，你下单后不用一直等，可以去做别的事，外卖好了再通知你。",\n'
            '    "relatedComponent": "前端界面",\n'
            '    "relatedFiles": ["frontend/src/services/api.ts"]\n'
            "  },\n"
            "  {\n"
            '    "id": "term-3",\n'
            '    "term": "JWT",\n'
            '    "plainExplanation": "身份验证的通行证",\n'
            '    "analogy": "就像会员卡，证明你是谁，可以享受哪些服务。",\n'
            '    "relatedComponent": "用户认证",\n'
            '    "relatedFiles": ["backend/app/services/auth_service.py"]\n'
            "  }\n"
            "]\n"
            "```"
        )

        # 构建项目上下文
        project_context = self._build_project_context(file_summaries)

        user_prompt = (
            f"以下是一个项目的代码结构：\n\n{project_context}\n\n"
            "请从以上代码中提取关键的技术术语，并给出大白话解释。"
        )

        try:
            logger.info("调用 LLM 生成术语词典，文件数: %d", len(file_summaries))
            result = await llm_service.generate_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.6,
                max_tokens=8000,
            )
            logger.info("LLM 返回结果类型: %s", type(result))

            # 确保返回的是列表
            if isinstance(result, dict) and "techTerms" in result:
                terms = result["techTerms"]
                logger.info("从字典中提取 techTerms，数量: %d", len(terms))
            elif isinstance(result, list):
                terms = result
                logger.info("直接使用列表，数量: %d", len(terms))
            else:
                logger.warning("LLM 返回格式异常，使用默认术语")
                terms = []

            # 为每个术语添加必需的字段
            return self._enrich_terms_with_ids(terms)

        except LLMError as error:
            logger.error("LLM 术语生成失败，使用默认模板: %s", str(error), exc_info=True)
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
