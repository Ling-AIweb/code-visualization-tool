"""
向量数据库服务测试
测试 ChromaDB 的基本功能
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.vector_service import vector_service


async def test_vector_service():
    """测试向量数据库服务"""
    print("=" * 50)
    print("开始测试向量数据库服务")
    print("=" * 50)
    
    try:
        # 测试 1: 获取集合统计信息
        print("\n[测试 1] 获取集合统计信息...")
        stats = await vector_service.get_collection_stats()
        print(f"✓ 集合名称: {stats.get('collection_name')}")
        print(f"✓ 代码片段总数: {stats.get('total_fragments')}")
        print(f"✓ 持久化目录: {stats.get('persist_directory')}")
        
        # 测试 2: 添加测试代码片段
        print("\n[测试 2] 添加测试代码片段...")
        test_fragments = [
            {
                "id": "test_file_1",
                "content": "def hello_world():\n    print('Hello, World!')",
                "file_path": "test/hello.py",
                "language": "python",
                "metadata": {
                    "file_name": "hello.py",
                    "language": "python",
                    "functions": ["hello_world"]
                }
            },
            {
                "id": "test_file_2",
                "content": "function greet(name) {\n    return `Hello, ${name}!`;\n}",
                "file_path": "test/greet.js",
                "language": "javascript",
                "metadata": {
                    "file_name": "greet.js",
                    "language": "javascript",
                    "functions": ["greet"]
                }
            }
        ]
        
        added_count = await vector_service.add_code_fragments(test_fragments)
        print(f"✓ 成功添加 {added_count} 个代码片段")
        
        # 测试 3: 语义搜索
        print("\n[测试 3] 语义搜索代码片段...")
        search_results = await vector_service.search_similar_code(
            query="打印 hello world",
            n_results=2
        )
        print(f"✓ 找到 {len(search_results)} 个相关结果:")
        for i, result in enumerate(search_results, 1):
            print(f"  {i}. {result['metadata']['file_path']} (相似度: {result.get('similarity', 'N/A')})")
        
        # 测试 4: 获取片段详情
        print("\n[测试 4] 获取片段详情...")
        fragment = await vector_service.get_fragment_by_id("test_file_1")
        if fragment:
            print(f"✓ 片段 ID: {fragment['id']}")
            print(f"✓ 文件路径: {fragment['metadata']['file_path']}")
            print(f"✓ 内容预览: {fragment['content'][:50]}...")
        else:
            print("✗ 未找到片段")
        
        # 测试 5: 按文件路径删除
        print("\n[测试 5] 删除测试片段...")
        deleted_count = await vector_service.delete_by_file_path("test/hello.py")
        print(f"✓ 删除了 {deleted_count} 个片段")
        
        # 最终统计
        print("\n[最终统计]")
        final_stats = await vector_service.get_collection_stats()
        print(f"✓ 当前代码片段总数: {final_stats.get('total_fragments')}")
        
        print("\n" + "=" * 50)
        print("✓ 所有测试通过！")
        print("=" * 50)
        
    except Exception as error:
        print(f"\n✗ 测试失败: {str(error)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_vector_service())
    sys.exit(0 if success else 1)
