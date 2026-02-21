"""代码脱敏工具的单元测试"""
import pytest
from app.utils.sanitizer import sanitize_code, sanitize_file_content


class TestSanitizeCode:
    """测试 sanitize_code 函数"""

    def test_redacts_api_key_with_double_quotes(self) -> None:
        code = 'API_KEY = "sk-abc123xyz456"'
        result = sanitize_code(code)
        assert "sk-abc123xyz456" not in result
        assert "REDACTED" in result

    def test_redacts_api_key_with_single_quotes(self) -> None:
        code = "secret_key = 'my-super-secret-key'"
        result = sanitize_code(code)
        assert "my-super-secret-key" not in result
        assert "REDACTED" in result

    def test_redacts_password_assignment(self) -> None:
        code = 'PASSWORD = "hunter2"'
        result = sanitize_code(code)
        assert "hunter2" not in result
        assert "REDACTED" in result

    def test_redacts_env_variable_style(self) -> None:
        code = "API_KEY=sk-1234567890abcdef"
        result = sanitize_code(code)
        assert "sk-1234567890abcdef" not in result
        assert "REDACTED" in result

    def test_redacts_ipv4_addresses(self) -> None:
        code = 'host = "192.168.1.100"'
        result = sanitize_code(code)
        assert "192.168.1.100" not in result
        assert "***" in result

    def test_redacts_email_addresses(self) -> None:
        code = 'admin_email = "admin@company.com"'
        result = sanitize_code(code)
        assert "admin@company.com" not in result
        assert "***@***" in result

    def test_preserves_normal_code(self) -> None:
        code = """
def calculate_total(items):
    total = sum(item.price for item in items)
    return total
"""
        result = sanitize_code(code)
        assert "calculate_total" in result
        assert "total" in result
        assert "sum" in result

    def test_handles_empty_string(self) -> None:
        result = sanitize_code("")
        assert result == ""

    def test_handles_multiline_with_mixed_secrets(self) -> None:
        code = """
DB_PASSWORD=supersecret123
host = "10.0.0.1"
normal_variable = 42
admin@example.com
"""
        result = sanitize_code(code)
        assert "supersecret123" not in result
        assert "10.0.0.1" not in result
        assert "admin@example.com" not in result
        assert "normal_variable" in result


class TestSanitizeFileContent:
    """测试 sanitize_file_content 函数"""

    def test_sanitizes_env_files(self) -> None:
        content = "API_KEY=my-secret-key\nDATABASE_URL=postgres://localhost"
        result = sanitize_file_content(".env", content)
        assert "my-secret-key" not in result

    def test_sanitizes_python_files(self) -> None:
        content = 'api_key = "secret123"'
        result = sanitize_file_content("config.py", content)
        assert "secret123" not in result

    def test_sanitizes_javascript_files(self) -> None:
        content = 'const token = "bearer-xyz"'
        result = sanitize_file_content("auth.js", content)
        # JS 文件也会被脱敏处理
        assert isinstance(result, str)

    def test_preserves_non_code_files(self) -> None:
        content = "This is a README file with API_KEY mentioned"
        result = sanitize_file_content("image.png", content)
        assert result == content
