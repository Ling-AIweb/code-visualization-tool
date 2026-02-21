"""
项目解析服务
处理文件上传、解压、目录扫描、代码脱敏、LLM 白话摘要生成和架构图生成。
支持异步处理与进度回传，24 小时自动清理。
"""
import uuid
import zipfile
import os
import asyncio
import shutil
import logging
import time
from io import BytesIO
from typing import Dict, Any, Optional, List
from pathlib import Path

from app.utils.sanitizer import sanitize_file_content
from app.utils.chunker import (
    scan_project_files,
    should_skip_path,
    is_code_file,
    MAX_FILE_SIZE_BYTES,
)
from app.services.llm_service import llm_service, LLMError
from app.core.config import settings

logger = logging.getLogger(__name__)

# 任务自动清理时间（24 小时）
TASK_EXPIRY_SECONDS = 24 * 60 * 60


class ProjectService:
    """项目解析服务，管理上传、解析、存储的完整生命周期"""

    def __init__(self) -> None:
        self.tasks: Dict[str, Dict[str, Any]] = {}

    async def upload_and_parse(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        上传并解析项目文件（同步模式，返回文件列表）。

        Args:
            file_content: ZIP 文件的字节内容
            filename: 原始文件名

        Returns:
            包含 task_id 和 file_list 的字典

        Raises:
            ValueError: 文件过大或格式不正确时
        """
        # 校验文件大小
        if len(file_content) > settings.max_upload_size_bytes:
            raise ValueError(
                f"文件大小超过限制（最大 {settings.MAX_UPLOAD_SIZE_MB}MB）"
            )

        # 校验 ZIP 格式
        if not zipfile.is_zipfile(BytesIO(file_content)):
            raise ValueError("上传的文件不是有效的 ZIP 格式")

        task_id = str(uuid.uuid4())
        temp_dir = f"/tmp/codestory_{task_id}"

        try:
            # 解压文件
            os.makedirs(temp_dir, exist_ok=True)
            with zipfile.ZipFile(BytesIO(file_content), "r") as zip_ref:
                zip_ref.extractall(temp_dir)

            # 扫描目录结构，获取文件列表
            file_list = self._scan_files(temp_dir)

            # 保存任务数据（用于后续异步处理）
            self.tasks[task_id] = {
                "task_id": task_id,
                "file_list": file_list,
                "directory": temp_dir,
                "status": "processing",
                "progress": 0,
                "message": "开始解析项目...",
                "project_data": None,
                "file_summaries": [],
                "created_at": time.time(),
            }

            # 启动后台异步解析任务
            asyncio.create_task(self._parse_project(task_id, file_content, filename))

            return {
                "task_id": task_id,
                "file_list": file_list
            }

        except Exception as error:
            raise ValueError(f"解析失败: {str(error)}")

    async def _parse_project(
        self, task_id: str, file_content: bytes, filename: str
    ) -> None:
        """异步解析项目的完整流程"""
        temp_dir = f"/tmp/codestory_{task_id}"

        try:
            # Step 1: 解压文件
            self._update_progress(task_id, 10, "正在解压文件...")
            os.makedirs(temp_dir, exist_ok=True)

            with zipfile.ZipFile(BytesIO(file_content), "r") as zip_ref:
                zip_ref.extractall(temp_dir)

            # Step 2: 扫描目录结构
            self._update_progress(task_id, 25, "正在扫描目录结构...")
            project_tree = self._scan_directory(temp_dir)

            # 处理空目录
            if self._is_empty_project(project_tree):
                self.tasks[task_id]["status"] = "failed"
                self.tasks[task_id]["message"] = "项目为空或不包含可解析的源代码文件"
                self._safe_cleanup(temp_dir)
                return

            # Step 3: 提取文件摘要（代码分片）
            self._update_progress(task_id, 40, "正在提取代码摘要...")
            file_summaries = scan_project_files(temp_dir)

            # Step 4: 对源代码进行脱敏处理
            self._update_progress(task_id, 50, "正在进行代码脱敏...")
            sanitized_summaries = self._sanitize_summaries(temp_dir, file_summaries)

            # Step 5: 调用 LLM 生成白话摘要
            self._update_progress(task_id, 60, "AI 正在翻阅代码，生成白话摘要...")
            enriched_tree = await self._enrich_tree_with_summaries(
                project_tree, sanitized_summaries
            )

            # Step 6: 调用 LLM 生成架构图
            self._update_progress(task_id, 80, "正在生成架构图...")
            mermaid_diagram = await self._generate_mermaid_with_llm(
                sanitized_summaries
            )

            # Step 7: 保存结果
            self._update_progress(task_id, 95, "正在整理结果...")
            self.tasks[task_id]["project_data"] = {
                "tree": enriched_tree,
                "mermaid_diagram": mermaid_diagram,
            }
            self.tasks[task_id]["file_summaries"] = sanitized_summaries

            # 完成
            self.tasks[task_id]["status"] = "completed"
            self.tasks[task_id]["progress"] = 100
            self.tasks[task_id]["message"] = "项目解析完成！"

        except Exception as error:
            logger.error("项目解析失败: %s", str(error), exc_info=True)
            self.tasks[task_id]["status"] = "failed"
            self.tasks[task_id]["message"] = f"解析失败: {str(error)}"
        finally:
            # 解析完成后立即清理临时文件（严禁持久化存储用户源码）
            self._safe_cleanup(temp_dir)

    def _update_progress(self, task_id: str, progress: int, message: str) -> None:
        """更新任务进度"""
        self.tasks[task_id]["progress"] = progress
        self.tasks[task_id]["message"] = message

    def _is_empty_project(self, tree: Dict[str, Any]) -> bool:
        """检查项目是否为空（无可解析的源代码文件）"""
        if tree["type"] == "file":
            return not is_code_file(Path(tree["name"]))

        children = tree.get("children", [])
        if not children:
            return True

        return all(self._is_empty_project(child) for child in children)

    def _scan_files(self, dir_path: str) -> List[str]:
        """
        递归扫描目录，获取所有文件路径

        Args:
            dir_path: 目录路径

        Returns:
            文件路径列表
        """
        root_path = Path(dir_path)
        file_list: List[str] = []

        for item in root_path.rglob("*"):
            if item.is_file():
                # 获取相对路径
                relative_path = item.relative_to(root_path)
                file_list.append(str(relative_path))

        return sorted(file_list)

    def _scan_directory(self, dir_path: str) -> Dict[str, Any]:
        """扫描目录结构，自动过滤无关配置文件"""
        root_path = Path(dir_path)
        return self._build_tree(root_path, root_path)

    def _build_tree(self, current_path: Path, root_path: Path) -> Dict[str, Any]:
        """递归构建目录树，跳过无关目录"""
        relative = current_path.relative_to(root_path)

        if current_path.is_file():
            return {
                "name": current_path.name,
                "type": "file",
                "path": str(relative),
                "description": self._generate_file_description(current_path),
                "summary": "",
            }

        children: List[Dict[str, Any]] = []
        try:
            for item in sorted(current_path.iterdir()):
                if should_skip_path(item.relative_to(root_path)):
                    continue
                if item.name.startswith("."):
                    continue
                children.append(self._build_tree(item, root_path))
        except PermissionError:
            pass

        return {
            "name": current_path.name,
            "type": "folder",
            "path": str(relative),
            "children": children,
        }

    def _generate_file_description(self, file_path: Path) -> str:
        """生成文件的白话描述"""
        suffix = file_path.suffix.lower()
        descriptions = {
            ".py": "Python 源代码 — 后端逻辑",
            ".js": "JavaScript 源代码 — 前端交互",
            ".ts": "TypeScript 源代码 — 带类型的前端逻辑",
            ".jsx": "React 组件 — 界面模块",
            ".tsx": "React TypeScript 组件 — 带类型的界面模块",
            ".java": "Java 源代码 — 后端服务",
            ".go": "Go 源代码 — 高性能后端",
            ".css": "样式表 — 页面的「衣服」",
            ".scss": "Sass 样式表 — 高级版的「衣服」",
            ".html": "网页模板 — 页面的「骨架」",
            ".json": "配置文件 — 系统的「说明书」",
            ".yml": "配置文件 — 系统的「说明书」",
            ".yaml": "配置文件 — 系统的「说明书」",
            ".md": "文档 — 项目的「使用手册」",
            ".sql": "数据库脚本 — 档案室的「整理规则」",
            ".vue": "Vue 组件 — 界面模块",
            ".svelte": "Svelte 组件 — 轻量界面模块",
        }
        return descriptions.get(suffix, "文件")

    def _sanitize_summaries(
        self, temp_dir: str, file_summaries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """对文件摘要中的代码内容进行脱敏"""
        root_path = Path(temp_dir)

        for summary in file_summaries:
            file_path = root_path / summary["file_path"]
            if file_path.exists() and file_path.is_file():
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    sanitized = sanitize_file_content(summary["file_path"], content)
                    # 只保留脱敏后的前 3000 字符用于 LLM 处理
                    summary["sanitized_preview"] = sanitized[:3000]
                except (PermissionError, OSError):
                    summary["sanitized_preview"] = ""
            else:
                summary["sanitized_preview"] = ""

        return file_summaries

    async def _enrich_tree_with_summaries(
        self,
        tree: Dict[str, Any],
        file_summaries: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """用 LLM 生成的白话摘要丰富目录树"""
        # 构建文件路径到摘要的映射
        summary_map: Dict[str, Dict[str, Any]] = {
            s["file_path"]: s for s in file_summaries
        }

        # 收集需要生成摘要的代码文件
        code_files_for_summary: List[Dict[str, Any]] = [
            s for s in file_summaries
            if is_code_file(Path(s["file_name"]))
            and s.get("sanitized_preview", "").strip()
        ]

        # 批量生成白话摘要（最多处理 20 个核心文件以控制成本）
        if code_files_for_summary:
            files_to_summarize = code_files_for_summary[:20]
            summaries_text = await self._batch_summarize_files(files_to_summarize)

            for file_path, summary_text in summaries_text.items():
                if file_path in summary_map:
                    summary_map[file_path]["ai_summary"] = summary_text

        # 将摘要写入目录树
        self._apply_summaries_to_tree(tree, summary_map)

        return tree

    async def _batch_summarize_files(
        self, files: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """批量调用 LLM 为文件生成白话摘要"""
        result: Dict[str, str] = {}

        # 构建批量摘要 prompt
        files_description = ""
        for file_info in files:
            preview = file_info.get("sanitized_preview", "")[:1500]
            classes = file_info.get("classes", [])
            functions = file_info.get("functions", [])
            methods = file_info.get("methods", [])

            files_description += f"\n--- 文件：{file_info['file_path']} ---\n"
            if classes:
                files_description += f"类：{', '.join(classes)}\n"
            if functions:
                files_description += f"函数：{', '.join(functions[:10])}\n"
            if methods:
                files_description += f"方法：{', '.join(methods[:10])}\n"
            files_description += f"代码预览：\n{preview}\n"

        system_prompt = (
            "你是一个代码翻译官，专门把代码功能翻译成大白话。\n"
            "规则：\n"
            "1. 禁止使用技术黑话，必须转化为生活化类比\n"
            "2. 每个文件用 1-2 句话概括其核心功能\n"
            "3. 用 JSON 格式返回，key 是文件路径，value 是白话摘要\n"
            "示例：{\"auth_service.py\": \"这是保安大叔的工作手册，负责检查每个来访者的身份证\"}"
        )

        try:
            parsed = await llm_service.generate_json(
                system_prompt=system_prompt,
                user_prompt=f"请为以下代码文件生成白话摘要：\n{files_description}",
                temperature=0.5,
                max_tokens=8000,
            )
            # parsed 应该是 {file_path: summary_text} 的字典
            for key, value in parsed.items():
                if isinstance(value, str):
                    result[key] = value
        except LLMError as error:
            logger.warning("批量摘要生成失败，使用基础描述: %s", str(error))
            for file_info in files:
                result[file_info["file_path"]] = self._generate_file_description(
                    Path(file_info["file_name"])
                )

        return result

    def _apply_summaries_to_tree(
        self, tree: Dict[str, Any], summary_map: Dict[str, Dict[str, Any]]
    ) -> None:
        """将 AI 摘要应用到目录树节点"""
        if tree["type"] == "file":
            file_path = tree["path"]
            if file_path in summary_map:
                ai_summary = summary_map[file_path].get("ai_summary", "")
                if ai_summary:
                    tree["summary"] = ai_summary
            return

        for child in tree.get("children", []):
            self._apply_summaries_to_tree(child, summary_map)

    async def _generate_mermaid_with_llm(
        self, file_summaries: List[Dict[str, Any]]
    ) -> str:
        """调用 LLM 生成 Mermaid 架构图"""
        # 构建项目结构描述
        structure_description = "项目文件结构：\n"
        for summary in file_summaries[:30]:
            classes = summary.get("classes", [])
            functions = summary.get("functions", [])
            methods = summary.get("methods", [])
            imports = summary.get("imports", [])

            structure_description += f"\n文件：{summary['file_path']}"
            if classes:
                structure_description += f" | 类：{', '.join(classes)}"
            if functions:
                structure_description += f" | 函数：{', '.join(functions[:5])}"
            if methods:
                structure_description += f" | 方法：{', '.join(methods[:5])}"
            if imports:
                structure_description += f" | 依赖：{', '.join(imports[:5])}"

        system_prompt = (
            "你是一个架构图生成专家。根据项目文件结构，生成 Mermaid.js 的 graph TD 架构图。\n"
            "规则：\n"
            "1. 节点名称使用白话中文（如：用户界面、后端逻辑中心、核心数据库）\n"
            "2. 连线标签使用动作描述（如：递交资料、查阅档案）\n"
            "3. 只展示核心模块之间的调用关系，不要列出每个文件\n"
            "4. 使用不同的节点形状区分类型：[] 方框表示服务，() 圆角表示组件，[()] 表示数据库\n"
            "5. 直接返回 Mermaid 代码文本，不要用 JSON 包装，不要加 ```mermaid 标记"
        )

        try:
            mermaid_code = await llm_service.chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": structure_description},
                ],
                temperature=0.5,
                max_tokens=1500,
            )
            # 清理可能的 markdown 标记
            cleaned = mermaid_code.strip()
            if cleaned.startswith("```"):
                lines = cleaned.split("\n")
                cleaned = "\n".join(lines[1:])
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3].strip()
            return cleaned
        except LLMError as error:
            logger.warning("LLM 架构图生成失败，使用基础版: %s", str(error))
            return self._generate_fallback_mermaid(file_summaries)

    def _generate_fallback_mermaid(self, file_summaries: List[Dict[str, Any]]) -> str:
        """当 LLM 不可用时，生成基础版 Mermaid 架构图"""
        lines = ["graph TD"]
        folders: Dict[str, List[str]] = {}

        for summary in file_summaries:
            parts = summary["file_path"].split("/")
            if len(parts) > 1:
                folder = parts[0]
                if folder not in folders:
                    folders[folder] = []
                folders[folder].append(summary["file_name"])

        node_index = 0
        folder_ids: Dict[str, str] = {}
        for folder_name in folders:
            node_id = f"F{node_index}"
            folder_ids[folder_name] = node_id
            lines.append(f'    {node_id}["{folder_name}"]')
            node_index += 1

        # 简单连接相邻文件夹
        folder_list = list(folder_ids.values())
        for i in range(len(folder_list) - 1):
            lines.append(f"    {folder_list[i]} --> {folder_list[i + 1]}")

        return "\n".join(lines)

    def _safe_cleanup(self, dir_path: str) -> None:
        """安全清理临时目录"""
        try:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
        except OSError as error:
            logger.warning("清理临时目录失败: %s", str(error))

    def _cleanup_expired_tasks(self) -> None:
        """清理超过 24 小时的过期任务"""
        current_time = time.time()
        expired_task_ids = [
            task_id
            for task_id, task_data in self.tasks.items()
            if current_time - task_data.get("created_at", 0) > TASK_EXPIRY_SECONDS
        ]
        for task_id in expired_task_ids:
            del self.tasks[task_id]
            logger.info("已清理过期任务: %s", task_id)

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """获取任务状态"""
        if task_id not in self.tasks:
            return {"status": "not_found", "message": "任务不存在"}

        task = self.tasks[task_id]
        return {
            "task_id": task_id,
            "status": task["status"],
            "progress": task["progress"],
            "message": task["message"],
        }

    def get_project_data(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取项目解析数据"""
        task = self.tasks.get(task_id)
        if not task or task["status"] != "completed":
            return None
        return task["project_data"]

    def get_file_summaries(self, task_id: str) -> List[Dict[str, Any]]:
        """获取项目的文件摘要列表（供群聊剧本生成使用）"""
        task = self.tasks.get(task_id)
        if not task or task["status"] != "completed":
            return []
        return task.get("file_summaries", [])


project_service = ProjectService()