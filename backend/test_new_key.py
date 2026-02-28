"""
测试新的 API Key
"""
import asyncio
import httpx
import json

async def test_new_api_key():
    """测试新的 API Key"""
    from dotenv import load_dotenv
    import os
    load_dotenv()
    
    api_key = os.getenv("API_KEY")
    api_base = os.getenv("API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    
    print("=" * 60)
    print("🧪 测试新的 API Key")
    print("=" * 60)
    print(f"\nAPI Key: {api_key[:20]}...{api_key[-4:]}")
    
    # 先测试一些可能的模型名称
    models_to_try = [
        "qwen3.5-plus",
        "qwen-plus",
        "qwen-max",
        "qwen-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
    ]
    
    url = f"{api_base}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    for model in models_to_try:
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": "你好"}
            ],
            "max_tokens": 50,
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
                response = await client.post(url, json=payload, headers=headers)
                result = response.json()
                
                if response.status_code == 200 and "choices" in result:
                    print(f"\n✅ 模型 '{model}' 可用！")
                    print(f"   响应: {result['choices'][0]['message']['content']}")
                    
                    # 更新 .env 文件建议
                    print(f"\n💡 建议在 .env 文件中设置:")
                    print(f"   API_KEY={api_key}")
                    print(f"   API_BASE={api_base}")
                    print(f"   MODEL_NAME={model}")
                    return True
                else:
                    print(f"❌ 模型 '{model}' 不可用: {result.get('msg', 'Unknown error')}")
        except Exception as e:
            print(f"❌ 模型 '{model}' 请求异常: {str(e)[:50]}")
        
        await asyncio.sleep(0.3)
    
    print("\n" + "=" * 60)
    print("⚠️  所有测试模型均不可用")
    print("=" * 60)
    print("\n可能的原因:")
    print("1. API Key 不正确或已过期")
    print("2. 该 API 提供商使用特殊的模型名称")
    print("3. 需要额外的认证参数")
    print(f"\n当前配置:")
    print(f"- API_KEY: {api_key[:20]}...{api_key[-4:]}")
    print(f"- API_BASE: {api_base}")
    print("\n建议:")
    print("- 检查 .env 文件中的配置是否正确")
    print("- 联系 API 提供商获取正确的模型名称列表")
    return False

if __name__ == "__main__":
    asyncio.run(test_new_api_key())
