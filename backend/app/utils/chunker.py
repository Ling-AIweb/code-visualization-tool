"""
代码分片与摘要提取工具
将源代码文件拆分为可管理的片段，并提取类名、函数名、注释等关键信息。
"""
import re
from typing import Dict, List, Any
from pathlib import Path


# 需要跳过的目录和文件
SKIP_DIRECTORIES = {
    "node_modules", ".git", "__pycache__", ".venv", "venv",
    "dist", "build", ".next", ".nuxt", "target", "bin", "obj",
    ".idea", ".vscode", ".DS_Store", "vendor", "packages",
}

SKIP_FILE_PATTERNS = {
    ".min.js", ".min.css", ".map", ".lock", ".sum",
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico",
    ".woff", ".woff2", ".ttf", ".eot",
    ".pyc", ".pyo", ".class", ".o", ".so", ".dll",
}

# 支持解析的源代码扩展名
CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java",
    ".go", ".rb", ".php", ".cs", ".cpp", ".c", ".h",
    ".vue", ".svelte", ".rs", ".kt", ".swift",
}

# 配置/文档文件（只提取摘要，不做深度解析）
CONFIG_EXTENSIONS = {
    ".json", ".yml", ".yaml", ".toml", ".ini", ".cfg",
    ".xml", ".html", ".css", ".scss", ".less",
    ".md", ".txt", ".rst",
}

MAX_FILE_SIZE_BYTES = 500 * 1024  # 500KB，超过此大小的文件只提取摘要
MAX_CHUNK_CHARS = 2000  # 每个分片最大字符数


def should_skip_path(path: Path) -> bool:
    """判断是否应该跳过该路径"""
    for part in path.parts:
        if part in SKIP_DIRECTORIES:
            return True
    file_name = path.name.lower()
    return any(file_name.endswith(pattern) for pattern in SKIP_FILE_PATTERNS)


def is_code_file(path: Path) -> bool:
    """判断是否为源代码文件"""
    return path.suffix.lower() in CODE_EXTENSIONS


def is_config_file(path: Path) -> bool:
    """判断是否为配置/文档文件"""
    return path.suffix.lower() in CONFIG_EXTENSIONS


def extract_python_summary(content: str) -> Dict[str, Any]:
    """提取 Python 文件的类名、函数名、导入和文档字符串"""
    classes = re.findall(r"^class\s+(\w+)", content, re.MULTILINE)
    functions = re.findall(r"^(?:async\s+)?def\s+(\w+)", content, re.MULTILINE)
    imports = re.findall(r"^(?:from\s+\S+\s+)?import\s+(.+)$", content, re.MULTILINE)
    docstrings = re.findall(r'"""(.*?)"""', content, re.DOTALL)

    top_docstring = ""
    if docstrings:
        top_docstring = docstrings[0].strip()[:200]

    return {
        "classes": classes,
        "functions": functions,
        "imports": [imp.strip() for imp in imports[:10]],
        "docstring": top_docstring,
    }


def extract_javascript_summary(content: str) -> Dict[str, Any]:
    """提取 JavaScript/TypeScript 文件的类名、函数名、导入"""
    classes = re.findall(r"(?:export\s+)?class\s+(\w+)", content)
    functions = re.findall(
        r"(?:export\s+)?(?:async\s+)?function\s+(\w+)", content
    )
    arrow_functions = re.findall(
        r"(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(", content
    )
    imports = re.findall(r"import\s+.*?from\s+['\"](.+?)['\"]", content)
    react_components = re.findall(
        r"(?:export\s+default\s+)?function\s+([A-Z]\w+)", content
    )

    return {
        "classes": classes,
        "functions": functions + arrow_functions,
        "imports": imports[:10],
        "react_components": react_components,
    }


def extract_java_summary(content: str) -> Dict[str, Any]:
    """提取 Java 文件的类名、方法名、导入"""
    classes = re.findall(
        r"(?:public|private|protected)?\s*class\s+(\w+)", content
    )
    interfaces = re.findall(r"interface\s+(\w+)", content)
    methods = re.findall(
        r"(?:public|private|protected)\s+\w+\s+(\w+)\s*\(", content
    )
    imports = re.findall(r"import\s+([\w.]+);", content)
    package_name = re.findall(r"package\s+([\w.]+);", content)

    return {
        "classes": classes,
        "interfaces": interfaces,
        "methods": methods,
        "imports": imports[:10],
        "package": package_name[0] if package_name else "",
    }


def extract_file_summary(file_path: str, content: str) -> Dict[str, Any]:
    """
    根据文件类型提取摘要信息。

    Args:
        file_path: 文件路径
        content: 文件内容

    Returns:
        包含文件摘要信息的字典
    """
    path = Path(file_path)
    suffix = path.suffix.lower()
    line_count = content.count("\n") + 1

    base_summary: Dict[str, Any] = {
        "file_path": file_path,
        "file_name": path.name,
        "extension": suffix,
        "line_count": line_count,
        "is_large": len(content) > MAX_FILE_SIZE_BYTES,
    }

    if suffix == ".py":
        base_summary.update(extract_python_summary(content))
    elif suffix in {".js", ".ts", ".jsx", ".tsx", ".vue", ".svelte"}:
        base_summary.update(extract_javascript_summary(content))
    elif suffix == ".java":
        base_summary.update(extract_java_summary(content))
    else:
        # 通用提取：取前 10 行作为预览
        preview_lines = content.split("\n")[:10]
        base_summary["preview"] = "\n".join(preview_lines)

    return base_summary


def chunk_code(content: str, max_chars: int = MAX_CHUNK_CHARS) -> List[str]:
    """
    将代码内容按逻辑边界分片。
    优先在空行处分割，其次在函数/类定义处分割。

    Args:
        content: 源代码内容
        max_chars: 每个分片的最大字符数

    Returns:
        分片列表
    """
    if len(content) <= max_chars:
        return [content]

    chunks: List[str] = []
    lines = content.split("\n")
    current_chunk_lines: List[str] = []
    current_length = 0

    for line in lines:
        line_length = len(line) + 1  # +1 for newline

        if current_length + line_length > max_chars and current_chunk_lines:
            chunks.append("\n".join(current_chunk_lines))
            current_chunk_lines = []
            current_length = 0

        current_chunk_lines.append(line)
        current_length += line_length

    if current_chunk_lines:
        chunks.append("\n".join(current_chunk_lines))

    return chunks


def scan_project_files(root_dir: str) -> List[Dict[str, Any]]:
    """
    扫描项目目录，提取所有有效文件的摘要。

    Args:
        root_dir: 项目根目录路径

    Returns:
        文件摘要列表
    """
    root_path = Path(root_dir)
    file_summaries: List[Dict[str, Any]] = []

    if not root_path.exists():
        return file_summaries

    for file_path in sorted(root_path.rglob("*")):
        if not file_path.is_file():
            continue

        if should_skip_path(file_path):
            continue

        relative_path = str(file_path.relative_to(root_path))

        if not (is_code_file(file_path) or is_config_file(file_path)):
            continue

        try:
            file_size = file_path.stat().st_size

            # 超大文件只记录元信息
            if file_size > MAX_FILE_SIZE_BYTES:
                file_summaries.append({
                    "file_path": relative_path,
                    "file_name": file_path.name,
                    "extension": file_path.suffix.lower(),
                    "line_count": 0,
                    "is_large": True,
                    "note": f"文件过大（{file_size // 1024}KB），仅记录元信息",
                })
                continue

            content = file_path.read_text(encoding="utf-8", errors="ignore")
            summary = extract_file_summary(relative_path, content)
            file_summaries.append(summary)

        except (PermissionError, OSError):
            continue

    return file_summaries
