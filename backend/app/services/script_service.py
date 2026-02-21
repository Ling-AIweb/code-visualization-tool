"""
群聊剧本生成服务
基于实际代码结构和 LLM，生成拟人化群聊剧本。
遵循 TECH_DESIGN.md 的剧本 JSON 结构规范。
"""
import logging
from typing import Dict, Any, List

from app.services.llm_service import llm_service, LLMError
from app.services.project_service import project_service

logger = logging.getLogger(__name__)

# 角色映射模板：将代码组件类型映射为拟人化角色
ROLE_MAPPING = {
    "Controller": {"name_suffix": "前台小妹", "personality": "急躁但专业，负责接待来访者"},
    "Service": {"name_suffix": "业务部主管", "personality": "沉稳保守，处理核心业务逻辑"},
    "Repository": {"name_suffix": "档案管理员", "personality": "记性好但动作慢，管理所有档案"},
    "Database": {"name_suffix": "老墨", "personality": "记性好但动作慢，管理所有档案"},
    "Model": {"name_suffix": "表格设计师", "personality": "严谨细致，定义数据的格式"},
    "Middleware": {"name_suffix": "保安大叔", "personality": "一丝不苟，检查每个来访者"},
    "Frontend": {"name_suffix": "网页小美", "personality": "活泼开朗，负责展示界面"},
    "Auth": {"name_suffix": "门卫队长", "personality": "严格把关，验证身份"},
    "Config": {"name_suffix": "行政助理", "personality": "细心周到，管理各种配置"},
    "Utils": {"name_suffix": "工具箱小哥", "personality": "万能帮手，提供各种小工具"},
    "Router": {"name_suffix": "导航员", "personality": "方向感极强，指引每个请求去对的地方"},
}


class ScriptService:
    """群聊剧本生成服务"""

    async def generate_chat_script(
        self, scenario: str, task_id: str
    ) -> Dict[str, Any]:
        """
        基于实际代码结构和业务场景，调用 LLM 生成拟人化群聊剧本。

        Args:
            scenario: 用户输入的业务场景（如"用户登录"）
            task_id: 项目任务 ID

        Returns:
            符合 TECH_DESIGN.md 剧本 JSON 结构的字典
        """
        # 获取项目的文件摘要（代码分片后的结构化数据）
        file_summaries = project_service.get_file_summaries(task_id)

        # 构建代码上下文
        code_context = self._build_code_context(file_summaries)

        # 调用 LLM 生成剧本
        script = await self._generate_script_with_llm(scenario, code_context)

        return script

    def _build_code_context(self, file_summaries: List[Dict[str, Any]]) -> str:
        """
        将文件摘要构建为 LLM 可理解的代码上下文描述。

        Args:
            file_summaries: 文件摘要列表

        Returns:
            代码上下文文本
        """
        if not file_summaries:
            return "这是一个空项目，没有可解析的源代码文件。"

        context_parts: List[str] = []
        for summary in file_summaries[:25]:
            file_path = summary.get("file_path", "")
            classes = summary.get("classes", [])
            functions = summary.get("functions", [])
            methods = summary.get("methods", [])
            ai_summary = summary.get("ai_summary", "")
            preview = summary.get("sanitized_preview", "")[:800]

            part = f"文件：{file_path}"
            if classes:
                part += f"\n  类：{', '.join(classes)}"
            if functions:
                part += f"\n  函数：{', '.join(functions[:8])}"
            if methods:
                part += f"\n  方法：{', '.join(methods[:8])}"
            if ai_summary:
                part += f"\n  功能：{ai_summary}"
            if preview:
                part += f"\n  代码片段：\n{preview}"

            context_parts.append(part)

        return "\n\n".join(context_parts)

    async def _generate_script_with_llm(
        self, scenario: str, code_context: str
    ) -> Dict[str, Any]:
        """
        调用 LLM 生成群聊剧本。

        Args:
            scenario: 业务场景
            code_context: 代码上下文

        Returns:
            剧本字典
        """
        system_prompt = (
            "你是一个代码剧本编剧。你的任务是把代码模块之间的交互，编写成一个生动有趣的「群聊对话」。\n\n"
            "规则：\n"
            "1. 根据代码中的实际模块（Controller、Service、Database 等）创建角色\n"
            "2. 每个角色有独特的性格和说话风格\n"
            "3. 对话内容必须反映代码的真实调用流程\n"
            "4. 每句对话必须关联到具体的代码文件和行号（code_ref 字段）\n"
            "5. 语言风格要口语化、有趣，像朋友之间的群聊\n"
            "6. 禁止使用技术黑话，用生活化类比代替\n"
            "7. 对话数量在 6-12 条之间\n\n"
            "返回的 JSON 必须严格遵循以下格式：\n"
            "{\n"
            '  "scenario": "场景名称",\n'
            '  "characters": [\n'
            '    {"id": "唯一标识", "name": "角色昵称", "role": "代码角色", "personality": "性格描述"}\n'
            "  ],\n"
            '  "dialogues": [\n'
            '    {"from": "发送者id", "to": "接收者id", "content": "对话内容", "code_ref": "文件名:行号"}\n'
            "  ]\n"
            "}"
        )

        user_prompt = (
            f"业务场景：{scenario}\n\n"
            f"项目代码结构：\n{code_context}\n\n"
            f"请根据以上代码结构，为「{scenario}」场景生成一个群聊剧本。"
        )

        try:
            script = await llm_service.generate_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.8,
                max_tokens=3000,
            )

            # 校验剧本结构完整性
            validated_script = self._validate_script_structure(script, scenario)
            return validated_script

        except LLMError as error:
            logger.warning("LLM 剧本生成失败，使用基础模板: %s", str(error))
            return self._generate_fallback_script(scenario)

    def _validate_script_structure(
        self, script: Dict[str, Any], scenario: str
    ) -> Dict[str, Any]:
        """
        校验 AI 生成的剧本 JSON 结构合法性。

        Args:
            script: AI 生成的剧本字典
            scenario: 原始场景名称

        Returns:
            校验并修正后的剧本
        """
        # 确保 scenario 字段存在
        if "scenario" not in script or not script["scenario"]:
            script["scenario"] = scenario

        # 确保 characters 字段存在且为列表
        if "characters" not in script or not isinstance(script["characters"], list):
            script["characters"] = []

        # 校验每个角色的必要字段
        valid_characters: List[Dict[str, Any]] = []
        for character in script["characters"]:
            if not isinstance(character, dict):
                continue
            validated_character = {
                "id": character.get("id", f"char_{len(valid_characters)}"),
                "name": character.get("name", "未知角色"),
                "role": character.get("role", "Unknown"),
                "personality": character.get("personality", ""),
            }
            valid_characters.append(validated_character)
        script["characters"] = valid_characters

        # 确保 dialogues 字段存在且为列表
        if "dialogues" not in script or not isinstance(script["dialogues"], list):
            script["dialogues"] = []

        # 收集有效的角色 ID
        valid_character_ids = {char["id"] for char in valid_characters}

        # 校验每条对话的必要字段
        valid_dialogues: List[Dict[str, Any]] = []
        for dialogue in script["dialogues"]:
            if not isinstance(dialogue, dict):
                continue
            from_id = dialogue.get("from", "")
            to_id = dialogue.get("to", "")
            content = dialogue.get("content", "")

            if not content:
                continue

            # 如果 from/to 不在角色列表中，跳过
            if from_id not in valid_character_ids or to_id not in valid_character_ids:
                continue

            valid_dialogues.append({
                "from": from_id,
                "to": to_id,
                "content": content,
                "code_ref": dialogue.get("code_ref", ""),
            })

        script["dialogues"] = valid_dialogues

        return script

    def _generate_fallback_script(self, scenario: str) -> Dict[str, Any]:
        """当 LLM 不可用时，生成基础模板剧本"""
        return {
            "scenario": scenario,
            "characters": [
                {
                    "id": "user",
                    "name": "用户小明",
                    "role": "User",
                    "personality": "好奇、急躁、喜欢提问",
                },
                {
                    "id": "fe",
                    "name": "网页小美",
                    "role": "Frontend",
                    "personality": "活泼、喜欢展示界面",
                },
                {
                    "id": "be",
                    "name": "后端阿强",
                    "role": "Backend",
                    "personality": "稳重、逻辑清晰",
                },
                {
                    "id": "db",
                    "name": "数据库老墨",
                    "role": "Database",
                    "personality": "记性好、说话慢",
                },
            ],
            "dialogues": [
                {
                    "from": "user",
                    "to": "fe",
                    "content": f"小美，我想{scenario}！",
                    "code_ref": "",
                },
                {
                    "from": "fe",
                    "to": "be",
                    "content": "阿强，收到请求，帮忙处理一下！",
                    "code_ref": "",
                },
                {
                    "from": "be",
                    "to": "db",
                    "content": "老墨，帮我查下相关数据！",
                    "code_ref": "",
                },
                {
                    "from": "db",
                    "to": "be",
                    "content": "找到了！数据在这里。",
                    "code_ref": "",
                },
                {
                    "from": "be",
                    "to": "fe",
                    "content": "处理完成，结果给你！",
                    "code_ref": "",
                },
                {
                    "from": "fe",
                    "to": "user",
                    "content": f"{scenario}成功啦！",
                    "code_ref": "",
                },
            ],
        }


script_service = ScriptService()