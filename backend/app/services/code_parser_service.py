"""
代码解析服务
遍历项目文件，提取核心代码，调用 LLM 生成生活化比喻摘要，存储为 JSON
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, List

from app.utils.chunker import (
    scan_project_files,
    is_code_file,
    should_skip_path,
)
from app.utils.sanitizer import sanitize_file_content
from app.services.llm_service import llm_service, LLMError
from app.services.vector_service import vector_service

logger = logging.getLogger(__name__)


class CodeParserService:
    """代码解析服务，负责提取核心代码并生成生活化比喻摘要"""

    def __init__(self) -> None:
        self.max_files_to_summarize = 20  # 最多处理 20 个核心文件以控制成本
        self.enable_vector_storage = True  # 是否启用向量数据库存储

    async def parse_project(
        self, project_dir: str
    ) -> Dict[str, Any]:
        """
        解析项目，提取核心代码并生成生活化比喻摘要

        Args:
            project_dir: 项目根目录路径

        Returns:
            包含文件摘要列表的字典
        """
        logger.info("开始解析项目: %s", project_dir)

        # Step 1: 扫描项目文件，提取核心代码
        logger.info("Step 1: 扫描项目文件...")
        file_summaries = scan_project_files(project_dir)

        # 过滤出核心代码文件（忽略配置文件、依赖包）
        core_code_files = self._filter_core_code_files(file_summaries)
        logger.info("找到 %d 个核心代码文件", len(core_code_files))

        # Step 2: 对核心代码进行脱敏处理
        logger.info("Step 2: 对代码进行脱敏处理...")
        sanitized_files = self._sanitize_code_files(
            project_dir, core_code_files
        )

        # Step 3: 调用 LLM 生成生活化比喻摘要
        logger.info("Step 3: 调用 LLM 生成生活化比喻摘要...")
        files_with_summaries = await self._generate_lifestyle_summaries(
            sanitized_files
        )

        # Step 4: 将摘要存储为 JSON 格式
        logger.info("Step 4: 格式化摘要数据...")
        result = {
            "total_files": len(file_summaries),
            "core_code_files": len(core_code_files),
            "summarized_files": len(files_with_summaries),
            "file_summaries": files_with_summaries,
        }

        # Step 5: 将代码片段存储到向量数据库（如果启用）
        if self.enable_vector_storage:
            logger.info("Step 5: 存储代码片段到向量数据库...")
            await self._store_to_vector_database(sanitized_files)

        logger.info("项目解析完成")
        return result

    def _filter_core_code_files(
        self, file_summaries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        过滤核心代码文件，忽略配置文件和依赖包

        Args:
            file_summaries: 所有文件的摘要列表

        Returns:
            核心代码文件列表
        """
        core_files = []

        for summary in file_summaries:
            file_name = summary.get("file_name", "")
            file_path = summary.get("file_path", "")
            extension = summary.get("extension", "")

            # 跳过配置文件
            if extension in {".json", ".yml", ".yaml", ".toml", ".ini", ".cfg", ".xml"}:
                continue

            # 跳过文档文件
            if extension in {".md", ".txt", ".rst"}:
                continue

            # 跳过样式文件
            if extension in {".css", ".scss", ".less", ".sass"}:
                continue

            # 跳过模板文件
            if extension in {".html", ".htm"}:
                continue

            # 只保留源代码文件
            if is_code_file(Path(file_name)):
                # 跳过测试文件
                if "test" in file_name.lower() or "spec" in file_name.lower():
                    continue

                # 跳过超大文件
                if summary.get("is_large", False):
                    logger.info("跳过大文件: %s", file_path)
                    continue

                core_files.append(summary)

        return core_files

    def _sanitize_code_files(
        self, project_dir: str, file_summaries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        对代码文件进行脱敏处理

        Args:
            project_dir: 项目根目录
            file_summaries: 文件摘要列表

        Returns:
            包含脱敏后代码预览的文件列表
        """
        root_path = Path(project_dir)
        sanitized_files = []

        for summary in file_summaries:
            file_path = root_path / summary["file_path"]

            if not file_path.exists() or not file_path.is_file():
                sanitized_files.append(summary)
                continue

            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                sanitized_content = sanitize_file_content(
                    summary["file_path"], content
                )

                # 只保留前 3000 字符用于 LLM 处理
                summary["sanitized_preview"] = sanitized_content[:3000]
                sanitized_files.append(summary)

            except (PermissionError, OSError) as error:
                logger.warning("读取文件失败: %s, 错误: %s", file_path, error)
                summary["sanitized_preview"] = ""
                sanitized_files.append(summary)

        return sanitized_files

    async def _generate_lifestyle_summaries(
        self, file_summaries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        调用 LLM 为每个核心文件生成生活化比喻摘要

        Args:
            file_summaries: 文件摘要列表

        Returns:
            包含生活化摘要的文件列表
        """
        # 限制处理数量以控制成本
        files_to_process = file_summaries[: self.max_files_to_summarize]

        if not files_to_process:
            return file_summaries

        # 构建批量处理 prompt
        files_description = self._build_files_description(files_to_process)

        system_prompt = self._build_system_prompt()

        try:
            # 调用 LLM 生成摘要
            parsed_result = await llm_service.generate_json(
                system_prompt=system_prompt,
                user_prompt=files_description,
                temperature=0.7,
                max_tokens=3000,
            )

            # 将 LLM 返回的摘要映射到文件
            summary_map = parsed_result if isinstance(parsed_result, dict) else {}

            for file_info in files_to_process:
                file_path = file_info["file_path"]

                if file_path in summary_map:
                    file_info["lifestyle_summary"] = summary_map[file_path]
                else:
                    # 如果 LLM 没有为该文件生成摘要，使用基础描述
                    file_info["lifestyle_summary"] = self._generate_fallback_summary(
                        file_info
                    )

            logger.info("成功生成 %d 个文件的生活化摘要", len(summary_map))

        except LLMError as error:
            logger.warning("LLM 摘要生成失败，使用基础描述: %s", str(error))
            # 降级处理：使用基础描述
            for file_info in files_to_process:
                file_info["lifestyle_summary"] = self._generate_fallback_summary(
                    file_info
                )

        return file_summaries

    def _build_files_description(
        self, file_summaries: List[Dict[str, Any]]
    ) -> str:
        """
        构建文件描述文本，用于发送给 LLM

        Args:
            file_summaries: 文件摘要列表

        Returns:
            文件描述文本
        """
        description = "以下是需要解析的代码文件：\n\n"

        for file_info in file_summaries:
            preview = file_info.get("sanitized_preview", "")[:1500]
            classes = file_info.get("classes", [])
            functions = file_info.get("functions", [])
            methods = file_info.get("methods", [])
            imports = file_info.get("imports", [])

            description += f"--- 文件：{file_info['file_path']} ---\n"

            if classes:
                description += f"类：{', '.join(classes)}\n"
            if functions:
                description += f"函数：{', '.join(functions[:10])}\n"
            if methods:
                description += f"方法：{', '.join(methods[:10])}\n"
            if imports:
                description += f"依赖：{', '.join(imports[:5])}\n"

            description += f"代码预览：\n{preview}\n\n"

        return description

    def _build_system_prompt(self) -> str:
        """
        构建系统提示词，要求 LLM 生成生活化比喻摘要

        Returns:
            系统提示词
        """
        return (
            "你是一个代码翻译官，专门把代码功能翻译成小白也能听懂的大白话。\n\n"
            "规则：\n"
            "1. 禁止使用技术黑话，必须转化为生活化类比\n"
            "2. 每个文件用 1 句话概括其核心功能\n"
            "3. 使用比喻手法，让非技术人员也能秒懂\n"
            "4. 常用比喻参考：\n"
            "   - 数据库 = 档案室\n"
            "   - API = 传声筒\n"
            "   - Controller = 前台接待\n"
            "   - Service = 业务部主管\n"
            "   - Model = 数据模型\n"
            "   - Utils = 工具箱\n"
            "   - Config = 说明书\n\n"
            "5. 必须返回合法的 JSON 格式，key 是文件路径，value 是生活化比喻摘要\n"
            "6. 不要使用 markdown 代码块标记\n\n"
            "示例输出：\n"
            "{\n"
            '  "src/auth/login.py": "这是保安大叔的工作手册，负责检查每个来访者的身份证和通行证",\n'
            '  "src/user/model.py": "这是访客登记表，记录每个来访者的基本信息和联系方式",\n'
            '  "src/api/routes.py": "这是前台接待台，负责把来访者的请求转达给相应的部门"\n'
            "}\n"
        )

    def _generate_fallback_summary(self, file_info: Dict[str, Any]) -> str:
        """
        生成降级摘要（当 LLM 不可用时使用）

        Args:
            file_info: 文件信息

        Returns:
            基础描述
        """
        file_name = file_info.get("file_name", "")
        extension = file_info.get("extension", "")

        # 基于文件扩展名生成基础描述
        descriptions = {
            ".py": f"这是 {file_name}，负责处理后端逻辑",
            ".js": f"这是 {file_name}，负责处理前端交互",
            ".ts": f"这是 {file_name}，负责处理带类型的前端逻辑",
            ".jsx": f"这是 {file_name}，负责渲染界面组件",
            ".tsx": f"这是 {file_name}，负责渲染带类型的界面组件",
            ".java": f"这是 {file_name}，负责处理后端服务",
            ".go": f"这是 {file_name}，负责处理高性能后端逻辑",
            ".vue": f"这是 {file_name}，负责渲染界面模块",
            ".svelte": f"这是 {file_name}，负责渲染轻量界面模块",
        }

        return descriptions.get(
            extension, f"这是 {file_name}，项目的核心代码文件"
        )

    async def _store_to_vector_database(
        self, file_summaries: List[Dict[str, Any]]
    ) -> None:
        """
        将代码片段存储到向量数据库

        Args:
            file_summaries: 文件摘要列表
        """
        fragments = []

        for file_info in file_summaries:
            file_path = file_info.get("file_path", "")
            extension = file_info.get("extension", "")
            sanitized_preview = file_info.get("sanitized_preview", "")

            if not sanitized_preview:
                continue

            # 为每个文件创建唯一的片段 ID
            fragment_id = file_path.replace("/", "_").replace("\\", "_")

            # 提取元数据
            metadata = {
                "file_name": file_info.get("file_name", ""),
                "language": extension.lstrip("."),
                "classes": file_info.get("classes", []),
                "functions": file_info.get("functions", []),
                "methods": file_info.get("methods", []),
            }

            fragments.append({
                "id": fragment_id,
                "content": sanitized_preview,
                "file_path": file_path,
                "language": extension.lstrip("."),
                "metadata": metadata
            })

        if fragments:
            try:
                added_count = await vector_service.add_code_fragments(fragments)
                logger.info("成功存储 %d 个代码片段到向量数据库", added_count)
            except Exception as error:
                logger.warning("存储到向量数据库失败: %s", str(error))

    def save_to_json(self, data: Dict[str, Any], output_path: str) -> None:
        """
        将解析结果保存为 JSON 文件

        Args:
            data: 解析结果数据
            output_path: 输出文件路径
        """
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info("摘要数据已保存到: %s", output_path)
        except IOError as error:
            logger.error("保存 JSON 文件失败: %s", error)
            raise


# 创建全局实例
code_parser_service = CodeParserService()
