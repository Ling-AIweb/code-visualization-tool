"""
测试 API 连接和模型调用
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from app.services.llm_service import llm_service, LLMError

async def test_api_connection():
    """测试 API 连接和基本调用"""
    print("=" * 60)
    print("🧪 开始测试 API 连接...")
    print("=" * 60)
    
    # 1. 检查配置
    print("\n📋 配置信息:")
    print(f"  API Base: {llm_service.api_base}")
    print(f"  Model: {llm_service.model_name}")
    print(f"  API Key: {llm_service.api_key[:20]}...{llm_service.api_key[-4:]}")
    print(f"  已配置: {llm_service.is_configured}")
    
    if not llm_service.is_configured:
        print("\n❌ API Key 未正确配置！")
        return False
    
    # 2. 测试简单对话
    print("\n🔍 测试 1: 简单对话...")
    try:
        messages = [
            {"role": "system", "content": "你是一个助手。"},
            {"role": "user", "content": "你好，请用一句话介绍你自己。"}
        ]
        response = await llm_service.chat_completion(messages, max_tokens=100)
        print(f"  ✅ 成功！响应: {response}")
    except LLMError as e:
        print(f"  ❌ 失败: {e}")
        return False
    
    # 3. 测试 JSON 输出（用于验证代码分析功能）
    print("\n🔍 测试 2: JSON 格式输出...")
    try:
        system_prompt = "你是一个代码分析助手。"
        user_prompt = "请分析以下代码片段：\n\ndef add(a, b):\n    return a + b\n\n返回 JSON 格式：{\"function_name\": \"函数名\", \"description\": \"功能描述\"}"
        
        result = await llm_service.generate_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=200
        )
        print(f"  ✅ 成功！JSON 结果: {result}")
    except LLMError as e:
        print(f"  ❌ 失败: {e}")
        return False
    
    # 4. 测试代码摘要功能
    print("\n🔍 测试 3: 代码摘要生成...")
    try:
        code = """
class UserController:
    def __init__(self, user_service):
        self.user_service = user_service
    
    def create_user(self, user_data):
        # 验证用户数据
        if not user_data.get('email'):
            raise ValueError('Email is required')
        
        # 创建用户
        user = self.user_service.create(user_data)
        return user
"""
        summary = await llm_service.summarize_code(code, "user_controller.py")
        print(f"  ✅ 成功！摘要: {summary}")
    except LLMError as e:
        print(f"  ❌ 失败: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 所有测试通过！API 配置正确，可以正常使用。")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(test_api_connection())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 发生未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
