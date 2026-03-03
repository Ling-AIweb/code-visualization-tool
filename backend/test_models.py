"""
测试不同的模型名称
"""
import asyncio
import httpx
import json

async def test_model(model_name):
    """测试单个模型"""
    api_key = "sk-sp-1a49b02548a34b948ec5fd4dddb69266"
    api_base = "https://coding.dashscope.aliyuncs.com/v1"
    
    url = f"{api_base}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model_name,
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
                print(f"✅ {model_name:30s} - 成功！响应: {result['choices'][0]['message']['content'][:50]}")
                return True, model_name
            else:
                print(f"❌ {model_name:30s} - 失败: {result.get('msg', 'Unknown error')}")
                return False, None
    except Exception as e:
        print(f"❌ {model_name:30s} - 异常: {str(e)[:50]}")
        return False, None

async def main():
    """测试常见模型名称"""
    print("=" * 60)
    print("🔍 测试不同的模型名称")
    print("=" * 60)
    
    # 常见的模型名称列表
    models_to_test = [
        # OpenAI 系列
        "gpt-3.5-turbo",
        "gpt-4",
        "gpt-4-turbo",
        "gpt-4o",
        "gpt-4o-mini",
        
        # 阿里云通义千问系列
        "qwen-turbo",
        "qwen-plus",
        "qwen-max",
        "qwen-max-longcontext",
        
        # 其他常见名称
        "claude-3-sonnet",
        "claude-3-opus",
        "deepseek-chat",
        "deepseek-coder",
        
        # 特殊格式
        "model-qwen",
        "model-gpt4",
    ]
    
    working_models = []
    
    for model in models_to_test:
        success, working_model = await test_model(model)
        if success:
            working_models.append(working_model)
        await asyncio.sleep(0.5)  # 避免请求过快
    
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    if working_models:
        print(f"\n✅ 发现可用模型: {', '.join(working_models)}")
        print(f"\n💡 建议在 .env 文件中设置:")
        print(f"   MODEL_NAME={working_models[0]}")
    else:
        print("\n❌ 未找到可用模型，请确认 API Key 是否正确或联系 API 提供商")

if __name__ == "__main__":
    asyncio.run(main())
