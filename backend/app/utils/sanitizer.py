"""
代码脱敏工具
在发送给大模型之前，通过正则过滤 API_KEY、PASSWORD、IP 地址等敏感信息。
"""
import re
from typing import List, Tuple

# 脱敏规则：(正则模式, 替换文本, 描述)
SANITIZE_RULES: List[Tuple[re.Pattern, str, str]] = [
    # API Key / Secret / Token — 双引号赋值
    (
        re.compile(
            r'(?i)(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token|private[_-]?key)'
            r'(\s*[:=]\s*)"[^"]*"',
            re.MULTILINE,
        ),
        r'\1\2"***REDACTED***"',
        "API Key (double-quoted)",
    ),
    # API Key / Secret / Token — 单引号赋值
    (
        re.compile(
            r"(?i)(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token|private[_-]?key)"
            r"(\s*[:=]\s*)'[^']*'",
            re.MULTILINE,
        ),
        r"\1\2'***REDACTED***'",
        "API Key (single-quoted)",
    ),
    # Password / Credential — 双引号赋值
    (
        re.compile(
            r'(?i)(password|passwd|pwd|secret|token|credential)'
            r'(\s*[:=]\s*)"[^"]*"',
            re.MULTILINE,
        ),
        r'\1\2"***REDACTED***"',
        "Password (double-quoted)",
    ),
    # Password / Credential — 单引号赋值
    (
        re.compile(
            r"(?i)(password|passwd|pwd|secret|token|credential)"
            r"(\s*[:=]\s*)'[^']*'",
            re.MULTILINE,
        ),
        r"\1\2'***REDACTED***'",
        "Password (single-quoted)",
    ),
    # 无引号的简单赋值（如 .env 文件）
    (
        re.compile(
            r"(?im)^((?:API_KEY|SECRET_KEY|PASSWORD|DB_PASSWORD|AUTH_TOKEN|ACCESS_TOKEN|PRIVATE_KEY)\s*=\s*)(.+)$"
        ),
        r"\1***REDACTED***",
        "Env variable secret",
    ),
    # IPv4 地址
    (
        re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
        "***.***.***.***",
        "IPv4 Address",
    ),
    # 邮箱地址
    (
        re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
        "***@***.***",
        "Email Address",
    ),
]

def sanitize_code(source_code: str) -> str:
    """
    对源代码进行脱敏处理，过滤敏感信息。

    Args:
        source_code: 原始源代码字符串

    Returns:
        脱敏后的源代码
    """
    sanitized = source_code
    for pattern, replacement, _description in SANITIZE_RULES:
        sanitized = pattern.sub(replacement, sanitized)
    return sanitized


def sanitize_file_content(file_path: str, content: str) -> str:
    """
    根据文件类型决定是否需要脱敏。
    配置文件（.env, .yml, .yaml, .ini, .cfg, .conf）始终脱敏。
    源代码文件也进行脱敏。

    Args:
        file_path: 文件路径
        content: 文件内容

    Returns:
        脱敏后的内容
    """
    config_extensions = {".env", ".yml", ".yaml", ".ini", ".cfg", ".conf", ".toml"}
    lower_path = file_path.lower()

    # 配置文件始终脱敏
    if any(lower_path.endswith(ext) for ext in config_extensions):
        return sanitize_code(content)

    # .env 文件（无扩展名但文件名匹配）
    if lower_path.endswith(".env") or "/.env" in lower_path:
        return sanitize_code(content)

    # 源代码文件也脱敏
    code_extensions = {".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rb", ".php"}
    if any(lower_path.endswith(ext) for ext in code_extensions):
        return sanitize_code(content)

    return content
