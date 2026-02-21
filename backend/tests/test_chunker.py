"""代码分片与摘要提取工具的单元测试"""
import os
import tempfile
import pytest
from pathlib import Path

from app.utils.chunker import (
    should_skip_path,
    is_code_file,
    is_config_file,
    extract_python_summary,
    extract_javascript_summary,
    extract_java_summary,
    extract_file_summary,
    chunk_code,
    scan_project_files,
)


class TestShouldSkipPath:
    """测试路径过滤逻辑"""

    def test_skips_node_modules(self) -> None:
        assert should_skip_path(Path("node_modules/package/index.js"))

    def test_skips_git_directory(self) -> None:
        assert should_skip_path(Path(".git/config"))

    def test_skips_pycache(self) -> None:
        assert should_skip_path(Path("__pycache__/module.cpython-311.pyc"))

    def test_skips_venv(self) -> None:
        assert should_skip_path(Path("venv/lib/python3.11/site.py"))

    def test_skips_min_js(self) -> None:
        assert should_skip_path(Path("dist/bundle.min.js"))

    def test_skips_image_files(self) -> None:
        assert should_skip_path(Path("assets/logo.png"))

    def test_allows_normal_source_files(self) -> None:
        assert not should_skip_path(Path("src/main.py"))

    def test_allows_nested_source_files(self) -> None:
        assert not should_skip_path(Path("app/services/user_service.py"))


class TestFileTypeDetection:
    """测试文件类型检测"""

    def test_python_is_code_file(self) -> None:
        assert is_code_file(Path("main.py"))

    def test_javascript_is_code_file(self) -> None:
        assert is_code_file(Path("app.js"))

    def test_typescript_is_code_file(self) -> None:
        assert is_code_file(Path("component.tsx"))

    def test_java_is_code_file(self) -> None:
        assert is_code_file(Path("Main.java"))

    def test_json_is_config_file(self) -> None:
        assert is_config_file(Path("package.json"))

    def test_yaml_is_config_file(self) -> None:
        assert is_config_file(Path("docker-compose.yml"))

    def test_image_is_neither(self) -> None:
        assert not is_code_file(Path("logo.png"))
        assert not is_config_file(Path("logo.png"))


class TestExtractPythonSummary:
    """测试 Python 文件摘要提取"""

    def test_extracts_classes(self) -> None:
        code = "class UserService:\n    pass\n\nclass AuthService:\n    pass"
        summary = extract_python_summary(code)
        assert "UserService" in summary["classes"]
        assert "AuthService" in summary["classes"]

    def test_extracts_functions(self) -> None:
        code = "def calculate_total():\n    pass\n\nasync def fetch_data():\n    pass"
        summary = extract_python_summary(code)
        assert "calculate_total" in summary["functions"]
        assert "fetch_data" in summary["functions"]

    def test_extracts_imports(self) -> None:
        code = "import os\nfrom typing import Dict\nimport json"
        summary = extract_python_summary(code)
        assert len(summary["imports"]) >= 2

    def test_extracts_docstring(self) -> None:
        code = '"""This is a module docstring."""\n\ndef main():\n    pass'
        summary = extract_python_summary(code)
        assert "module docstring" in summary["docstring"]

    def test_handles_empty_file(self) -> None:
        summary = extract_python_summary("")
        assert summary["classes"] == []
        assert summary["functions"] == []


class TestExtractJavaScriptSummary:
    """测试 JavaScript/TypeScript 文件摘要提取"""

    def test_extracts_classes(self) -> None:
        code = "export class UserComponent {}\nclass AuthHelper {}"
        summary = extract_javascript_summary(code)
        assert "UserComponent" in summary["classes"]

    def test_extracts_functions(self) -> None:
        code = "function handleClick() {}\nexport async function fetchData() {}"
        summary = extract_javascript_summary(code)
        assert "handleClick" in summary["functions"]
        assert "fetchData" in summary["functions"]

    def test_extracts_arrow_functions(self) -> None:
        code = "const processData = async (data) => {}"
        summary = extract_javascript_summary(code)
        assert "processData" in summary["functions"]

    def test_extracts_imports(self) -> None:
        code = "import React from 'react'\nimport axios from 'axios'"
        summary = extract_javascript_summary(code)
        assert "react" in summary["imports"]
        assert "axios" in summary["imports"]


class TestExtractJavaSummary:
    """测试 Java 文件摘要提取"""

    def test_extracts_classes(self) -> None:
        code = "public class UserController {}"
        summary = extract_java_summary(code)
        assert "UserController" in summary["classes"]

    def test_extracts_methods(self) -> None:
        code = "public String getUserById(int id) {}\nprivate void validate() {}"
        summary = extract_java_summary(code)
        assert "getUserById" in summary["methods"]
        assert "validate" in summary["methods"]

    def test_extracts_package(self) -> None:
        code = "package com.example.service;\n\npublic class Main {}"
        summary = extract_java_summary(code)
        assert summary["package"] == "com.example.service"


class TestChunkCode:
    """测试代码分片"""

    def test_short_code_returns_single_chunk(self) -> None:
        code = "x = 1\ny = 2"
        chunks = chunk_code(code, max_chars=100)
        assert len(chunks) == 1

    def test_long_code_splits_into_multiple_chunks(self) -> None:
        code = "\n".join([f"line_{i} = {i}" for i in range(200)])
        chunks = chunk_code(code, max_chars=500)
        assert len(chunks) > 1

    def test_empty_code_returns_single_empty_chunk(self) -> None:
        chunks = chunk_code("")
        assert len(chunks) == 1
        assert chunks[0] == ""

    def test_all_content_preserved_after_chunking(self) -> None:
        code = "\n".join([f"variable_{i} = {i}" for i in range(100)])
        chunks = chunk_code(code, max_chars=300)
        reassembled = "\n".join(chunks)
        assert reassembled == code


class TestScanProjectFiles:
    """测试项目文件扫描"""

    def test_scans_python_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            py_file = Path(temp_dir) / "main.py"
            py_file.write_text("def hello():\n    print('hello')")

            summaries = scan_project_files(temp_dir)
            assert len(summaries) == 1
            assert summaries[0]["file_name"] == "main.py"

    def test_skips_node_modules(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            nm_dir = Path(temp_dir) / "node_modules" / "package"
            nm_dir.mkdir(parents=True)
            (nm_dir / "index.js").write_text("module.exports = {}")

            src_file = Path(temp_dir) / "app.js"
            src_file.write_text("console.log('hello')")

            summaries = scan_project_files(temp_dir)
            file_names = [s["file_name"] for s in summaries]
            assert "app.js" in file_names
            assert "index.js" not in file_names

    def test_handles_empty_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            summaries = scan_project_files(temp_dir)
            assert summaries == []

    def test_handles_nonexistent_directory(self) -> None:
        summaries = scan_project_files("/nonexistent/path")
        assert summaries == []

    def test_marks_large_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            large_file = Path(temp_dir) / "big.py"
            large_file.write_text("x = 1\n" * 100000)

            summaries = scan_project_files(temp_dir)
            assert len(summaries) == 1
            assert summaries[0]["is_large"] is True
