"""
LLM 调用服务
封装与大模型的交互，支持 OpenAI 兼容 API。
强制 JSON 格式输出，长代码先摘要再处理。
"""
import json
import logging
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """大模型调用服务，支持 OpenAI 兼容 API"""

    def __init__(self) -> None:
        self.api_key: str = settings.API_KEY
        self.api_base: str = settings.API_BASE.rstrip("/")
        self.model_name: str = settings.MODEL_NAME
        self.timeout: float = 60.0
        self.max_retries: int = 1

    @property
    def is_configured(self) -> bool:
        """检查 API Key 是否已配置为真实值"""
        placeholder_keys = {"", "your_api_key_here", "demo_key_for_testing", "sk-xxx"}
        result = self.api_key not in placeholder_keys
        logger.info("LLM 配置检查: API_KEY=%s..., configured=%s", self.api_key[:10] if self.api_key else "None", result)
        return result

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """
        调用 LLM 的 chat completion 接口。

        Args:
            messages: 消息列表，格式为 [{"role": "system", "content": "..."}, ...]
            temperature: 生成温度
            max_tokens: 最大生成 token 数

        Returns:
            模型返回的文本内容

        Raises:
            LLMError: 当 API 调用失败时
        """
        if not self.is_configured:
            raise LLMError(
                "API Key 未配置。请在 backend/.env 文件中设置真实的 API_KEY"
            )

        url = f"{self.api_base}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        logger.info("LLM 请求: URL=%s, Model=%s, MaxTokens=%d", url, self.model_name, max_tokens)

        last_error: Optional[Exception] = None

        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout, verify=False) as client:
                    response = await client.post(url, json=payload, headers=headers)
                    logger.info("LLM 响应: Status=%d", response.status_code)
                    response.raise_for_status()
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
            except httpx.HTTPStatusError as error:
                last_error = error
                response_body = error.response.text[:500] if error.response else "N/A"
                logger.warning(
                    "LLM API HTTP error (attempt %d/%d): %s\n响应体: %s",
                    attempt + 1,
                    self.max_retries + 1,
                    str(error),
                    response_body,
                )
            except (httpx.RequestError, KeyError, IndexError) as error:
                last_error = error
                logger.warning(
                    "LLM API request error (attempt %d/%d): %s, type=%s",
                    attempt + 1,
                    self.max_retries + 1,
                    str(error),
                    type(error).__name__,
                )

        raise LLMError(f"LLM API 调用失败（已重试 {self.max_retries} 次）: {last_error}")

    async def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> Dict[str, Any]:
        """
        调用 LLM 并强制返回合法 JSON。
        会自动在 system prompt 中追加 JSON 格式要求。

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            temperature: 生成温度
            max_tokens: 最大 token 数

        Returns:
            解析后的 JSON 字典

        Raises:
            LLMError: 当 API 调用失败或 JSON 解析失败时
        """
        json_instruction = (
            "\n\n【重要】你必须且只能返回合法的 JSON 格式，不要包含 markdown 代码块标记、"
            "注释或任何其他非 JSON 内容。确保 JSON 可以被 json.loads() 直接解析。"
        )
        full_system_prompt = system_prompt + json_instruction

        messages = [
            {"role": "system", "content": full_system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        raw_response = await self.chat_completion(
            messages, temperature=temperature, max_tokens=max_tokens
        )

        return validate_and_parse_json(raw_response)

    async def summarize_code(self, code_content: str, file_path: str) -> str:
        """
        对长代码文件生成白话摘要。
        遵循 AGENTS.md 要求：长代码必须先摘要再处理。

        Args:
            code_content: 源代码内容
            file_path: 文件路径

        Returns:
            白话摘要文本
        """
        system_prompt = (
            "你是一个代码解读专家。你的任务是用通俗易懂的大白话解释代码的功能。"
            "禁止使用技术黑话，必须转化为生活化类比。"
            "例如：数据库 = 档案室，API = 传声筒，Controller = 前台接待。"
            "请用 3-5 句话概括这个文件的核心功能。"
        )
        user_prompt = f"文件路径：{file_path}\n\n代码内容：\n{code_content[:3000]}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        return await self.chat_completion(messages, temperature=0.5, max_tokens=500)


def validate_and_parse_json(raw_text: str) -> Dict[str, Any]:
    """
    校验并解析 AI 生成的 JSON 文本。
    会尝试多种方式提取合法 JSON。

    Args:
        raw_text: AI 返回的原始文本

    Returns:
        解析后的字典

    Raises:
        LLMError: 当无法解析为合法 JSON 时
    """
    cleaned = raw_text.strip()

    # 尝试直接解析
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 尝试去除 markdown 代码块标记
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        # 找到第一个非 ``` 行
        start_index = 0
        for i, line in enumerate(lines):
            if not line.strip().startswith("```"):
                start_index = i
                break
        # 找到最后一个非 ``` 行
        end_index = len(lines)
        for i in range(len(lines) - 1, -1, -1):
            if not lines[i].strip().startswith("```"):
                end_index = i + 1
                break
        if start_index < end_index:
            json_text = "\n".join(lines[start_index:end_index])
            try:
                return json.loads(json_text.strip())
            except json.JSONDecodeError:
                pass

    # 尝试提取第一个 { 到最后一个 } 之间的内容
    first_brace = cleaned.find("{")
    last_brace = cleaned.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        json_candidate = cleaned[first_brace : last_brace + 1]
        try:
            return json.loads(json_candidate)
        except json.JSONDecodeError:
            pass

    # 尝试提取第一个 [ 到最后一个 ] 之间的内容
    first_bracket = cleaned.find("[")
    last_bracket = cleaned.rfind("]")
    if first_bracket != -1 and last_bracket != -1 and last_bracket > first_bracket:
        json_candidate = cleaned[first_bracket : last_bracket + 1]
        try:
            parsed = json.loads(json_candidate)
            return {"items": parsed}
        except json.JSONDecodeError:
            pass

    raise LLMError(
        f"无法将 AI 返回内容解析为合法 JSON。原始内容前 200 字符：{cleaned[:200]}"
    )


class LLMError(Exception):
    """LLM 服务相关错误"""
    pass


llm_service = LLMService()
