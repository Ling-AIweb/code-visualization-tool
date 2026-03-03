"""
调试 API 响应格式
"""
import asyncio
import httpx
import json

async def debug_api():
    """直接调用 API 查看原始响应"""
    api_key = "sk-sp-1a49b02548a34b948ec5fd4dddb69266"
    api_base = "https://coding.dashscope.aliyuncs.com/v1"
    model = "qwen3.5-plus"
    
    url = f"{api_base}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是一个助手。"},
            {"role": "user", "content": "你好"}
        ],
        "temperature": 0.7,
        "max_tokens": 100,
    }
    
    print("=" * 60)
    print("🔍 调试 API 响应格式")
    print("=" * 60)
    print(f"\n请求 URL: {url}")
    print(f"请求参数: {json.dumps(payload, indent=2, ensure_ascii=False)}\n")
    
    try:
        async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
            response = await client.post(url, json=payload, headers=headers)
            print(f"响应状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}\n")
            
            # 尝试解析 JSON
            try:
                result = response.json()
                print("响应内容 (JSON):")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            except Exception as e:
                print(f"无法解析为 JSON: {e}")
                print(f"原始响应内容:\n{response.text}")
                
    except Exception as e:
        print(f"请求失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_api())
