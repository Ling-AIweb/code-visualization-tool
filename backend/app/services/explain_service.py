"""
术语解释服务
接入 LLM 动态解释代码中的技术术语，用生活化类比让小白也能理解。
同时保留本地术语字典作为 fallback。
"""
import re
import logging
from typing import Dict, Any, List

from app.services.llm_service import llm_service, LLMError

logger = logging.getLogger(__name__)

# 本地术语字典（作为 LLM 不可用时的 fallback）
LOCAL_TERM_DICTIONARY: Dict[str, Dict[str, str]] = {
    "API": {
        "plain": "应用程序接口",
        "analogy": "就像餐厅的服务员，负责传递客人的点单给厨房，再把做好的菜端给客人。",
    },
    "Database": {
        "plain": "数据库",
        "analogy": "就像一个巨大的档案室，专门用来存储和管理所有的数据文件。",
    },
    "Controller": {
        "plain": "控制器",
        "analogy": "就像公司的前台接待，负责接收请求并分发给合适的部门处理。",
    },
    "Service": {
        "plain": "服务层",
        "analogy": "就像公司的业务部门，专门处理具体的业务逻辑和计算。",
    },
    "Model": {
        "plain": "数据模型",
        "analogy": "就像表格的模板，定义了数据应该长什么样、有什么字段。",
    },
    "Repository": {
        "plain": "数据仓库",
        "analogy": "就像仓库管理员，专门负责和数据库打交道，存取数据。",
    },
    "Middleware": {
        "plain": "中间件",
        "analogy": "就像安检员，在进入系统前先检查一遍，确保安全合规。",
    },
    "async": {
        "plain": "异步",
        "analogy": "就像点外卖，你下单后不用一直等，可以去做别的事，外卖好了再通知你。",
    },
    "callback": {
        "plain": "回调函数",
        "analogy": "就像留了个电话号码，事情办完了就给你打电话通知。",
    },
    "Promise": {
        "plain": "承诺对象",
        "analogy": "就像订餐小票，上面写着「承诺30分钟内送达」，你可以等着取餐。",
    },
    "JWT": {
        "plain": "JSON Web Token",
        "analogy": "就像一张电子门票，盖了章之后可以用来证明你的身份，不用每次都出示身份证。",
    },
    "RESTful": {
        "plain": "RESTful 接口",
        "analogy": "就像一套标准的快递寄送规则，大家都按这个规则来，沟通更顺畅。",
    },
    "SQL": {
        "plain": "结构化查询语言",
        "analogy": "就像档案室的查询指令，告诉管理员「帮我找出所有姓张的客户资料」。",
    },
    "HTTP": {
        "plain": "超文本传输协议",
        "analogy": "就像快递公司的运输规则，规定了包裹怎么打包、怎么寄送、怎么签收。",
    },
    "JSON": {
        "plain": "JavaScript 对象表示法",
        "analogy": "就像一种通用的表格格式，不管是中国人还是美国人都能看懂的数据格式。",
    },
    "Cache": {
        "plain": "缓存",
        "analogy": "就像把常用的文件放在桌面上，不用每次都跑去档案室翻找。",
    },
    "WebSocket": {
        "plain": "网络套接字",
        "analogy": "就像打电话，双方可以随时说话，不用像发短信那样一来一回。",
    },
    "Docker": {
        "plain": "容器化工具",
        "analogy": "就像集装箱，把应用和它需要的所有东西打包在一起，搬到哪里都能用。",
    },
}

# 常见技术术语关键词列表
COMMON_TERMS = [
    "API", "Database", "DB", "Controller", "Service",
    "Model", "Repository", "Middleware", "async", "await",
    "callback", "Promise", "JWT", "RESTful", "HTTP",
    "JSON", "XML", "SQL", "NoSQL", "Cache", "Redis",
    "WebSocket", "Docker", "Kubernetes", "CI/CD", "Git",
    "ORM", "MVC", "MVVM", "GraphQL", "gRPC",
    "OAuth", "CORS", "CSRF", "XSS", "SSL", "TLS",
]


class ExplainService:
    """术语解释服务，优先使用 LLM 动态解释，fallback 到本地字典"""

    async def explain_term(self, code_snippet: str) -> Dict[str, Any]:
        """
        解释代码片段中的技术术语。
        优先调用 LLM 生成动态解释，失败时使用本地字典。

        Args:
            code_snippet: 代码片段或技术术语

        Returns:
            包含 term、plain_explanation、analogy 的字典
        """
        # 提取关键词
        keywords = self._extract_keywords(code_snippet)

        # 优先尝试 LLM 动态解释
        try:
            explanation = await self._explain_with_llm(code_snippet, keywords)
            return explanation
        except LLMError as error:
            logger.warning("LLM 术语解释失败，使用本地字典: %s", str(error))

        # Fallback: 使用本地字典
        return self._explain_with_local_dictionary(code_snippet, keywords)

    async def _explain_with_llm(
        self, code_snippet: str, keywords: List[str]
    ) -> Dict[str, Any]:
        """调用 LLM 动态解释代码片段"""
        system_prompt = (
            "你是一个技术翻译官，专门把代码和技术术语翻译成大白话。\n"
            "规则：\n"
            "1. 禁止使用技术黑话，必须用生活化的类比来解释\n"
            "2. 解释要简短有趣，像跟朋友聊天一样\n"
            "3. 返回 JSON 格式：\n"
            '{"term": "术语名称", "plain_explanation": "一句话白话解释", '
            '"analogy": "生活化类比，以「就像...」开头"}'
        )

        user_prompt = f"请解释以下代码/术语：\n{code_snippet}"
        if keywords:
            user_prompt += f"\n\n其中包含的关键技术术语：{', '.join(keywords)}"

        result = await llm_service.generate_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.6,
            max_tokens=500,
        )

        # 校验返回结构
        return {
            "term": result.get("term", keywords[0] if keywords else "代码片段"),
            "plain_explanation": result.get(
                "plain_explanation", "这段代码实现了一个特定的功能。"
            ),
            "analogy": result.get(
                "analogy", "就像一个工具，帮助程序完成特定的任务。"
            ),
        }

    def _explain_with_local_dictionary(
        self, code_snippet: str, keywords: List[str]
    ) -> Dict[str, Any]:
        """使用本地字典解释术语"""
        for keyword in keywords:
            # 精确匹配
            if keyword in LOCAL_TERM_DICTIONARY:
                term_info = LOCAL_TERM_DICTIONARY[keyword]
                return {
                    "term": keyword,
                    "plain_explanation": term_info["plain"],
                    "analogy": term_info["analogy"],
                }

            # 不区分大小写匹配
            for dict_key, term_info in LOCAL_TERM_DICTIONARY.items():
                if keyword.lower() == dict_key.lower():
                    return {
                        "term": dict_key,
                        "plain_explanation": term_info["plain"],
                        "analogy": term_info["analogy"],
                    }

        # 没有匹配到任何术语
        return {
            "term": keywords[0] if keywords else "代码片段",
            "plain_explanation": "这段代码是程序的一部分，用于实现特定的功能。",
            "analogy": "就像一个菜谱，告诉计算机按什么步骤来完成任务。",
        }

    def _extract_keywords(self, code_snippet: str) -> List[str]:
        """从代码片段中提取可能的技术术语"""
        keywords: List[str] = []

        for term in COMMON_TERMS:
            if term.lower() in code_snippet.lower():
                keywords.append(term)

        # 提取 CamelCase 标识符
        camel_case_words = re.findall(r"\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b", code_snippet)
        keywords.extend(camel_case_words[:5])

        return keywords


explain_service = ExplainService()