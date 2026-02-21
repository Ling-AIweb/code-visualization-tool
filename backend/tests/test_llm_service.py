"""LLM 服务的单元测试（测试 JSON 校验逻辑，不依赖外部 API）"""
import pytest
from app.services.llm_service import validate_and_parse_json, LLMError


class TestValidateAndParseJson:
    """测试 JSON 校验与解析"""

    def test_parses_valid_json(self) -> None:
        raw = '{"key": "value", "number": 42}'
        result = validate_and_parse_json(raw)
        assert result["key"] == "value"
        assert result["number"] == 42

    def test_parses_json_with_whitespace(self) -> None:
        raw = '  \n  {"key": "value"}  \n  '
        result = validate_and_parse_json(raw)
        assert result["key"] == "value"

    def test_strips_markdown_code_block(self) -> None:
        raw = '```json\n{"key": "value"}\n```'
        result = validate_and_parse_json(raw)
        assert result["key"] == "value"

    def test_strips_markdown_code_block_without_language(self) -> None:
        raw = '```\n{"key": "value"}\n```'
        result = validate_and_parse_json(raw)
        assert result["key"] == "value"

    def test_extracts_json_from_surrounding_text(self) -> None:
        raw = 'Here is the result: {"key": "value"} Hope this helps!'
        result = validate_and_parse_json(raw)
        assert result["key"] == "value"

    def test_handles_nested_json(self) -> None:
        raw = '{"outer": {"inner": [1, 2, 3]}}'
        result = validate_and_parse_json(raw)
        assert result["outer"]["inner"] == [1, 2, 3]

    def test_handles_json_array_wrapped_in_object(self) -> None:
        raw = '[{"id": 1}, {"id": 2}]'
        result = validate_and_parse_json(raw)
        assert "items" in result
        assert len(result["items"]) == 2

    def test_raises_error_for_invalid_json(self) -> None:
        raw = "This is not JSON at all"
        with pytest.raises(LLMError):
            validate_and_parse_json(raw)

    def test_raises_error_for_empty_string(self) -> None:
        with pytest.raises(LLMError):
            validate_and_parse_json("")

    def test_parses_script_json_structure(self) -> None:
        """测试符合 TECH_DESIGN.md 剧本 JSON 结构的解析"""
        raw = """
{
  "scenario": "用户登录流程",
  "characters": [
    {"id": "fe", "name": "网页小美", "role": "Frontend", "personality": "急躁但专业"}
  ],
  "dialogues": [
    {"from": "fe", "to": "be", "content": "有人要登录！", "code_ref": "login.js:L45"}
  ]
}
"""
        result = validate_and_parse_json(raw)
        assert result["scenario"] == "用户登录流程"
        assert len(result["characters"]) == 1
        assert len(result["dialogues"]) == 1
        assert result["dialogues"][0]["code_ref"] == "login.js:L45"
