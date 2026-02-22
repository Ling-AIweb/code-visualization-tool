"""
向量数据库服务
使用 ChromaDB 存储和检索代码片段的向量表示
"""
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)

class VectorService:
    """向量数据库服务，负责代码片段的存储和语义检索（延迟初始化）"""

    def __init__(self) -> None:
        """仅保存配置，不立即初始化 ChromaDB（延迟到首次使用时）"""
        self.collection_name = "code_fragments"
        self._client = None
        self._collection = None
        self._embedding_function = None
        self._initialized = False

    def _ensure_initialized(self) -> bool:
        """延迟初始化：首次调用时才创建 ChromaDB 客户端和集合"""
        if self._initialized:
            return self._collection is not None

        self._initialized = True

        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings
            from chromadb.utils import embedding_functions

            persist_dir = Path(settings.CHROMA_PERSIST_DIR)
            persist_dir.mkdir(parents=True, exist_ok=True)

            self._client = chromadb.PersistentClient(
                path=str(persist_dir),
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )

            # 使用 OpenAI 嵌入模型；如果 API Key 为空则降级
            if settings.API_KEY:
                try:
                    self._embedding_function = embedding_functions.OpenAIEmbeddingFunction(
                        api_key=settings.API_KEY,
                        api_base=settings.API_BASE,
                        model_name="text-embedding-ada-002"
                    )
                    logger.info("使用 OpenAI 嵌入模型")
                except Exception:
                    self._embedding_function = embedding_functions.DefaultEmbeddingFunction()
                    logger.warning("OpenAI 嵌入模型不可用，降级使用默认嵌入函数")
            else:
                self._embedding_function = embedding_functions.DefaultEmbeddingFunction()
                logger.info("未配置 API Key，使用默认嵌入函数")

            self._initialize_collection()
            return self._collection is not None

        except Exception as error:
            logger.error("ChromaDB 初始化失败: %s", str(error))
            return False

    @property
    def client(self):
        self._ensure_initialized()
        return self._client

    @property
    def collection(self):
        self._ensure_initialized()
        return self._collection

    def _initialize_collection(self) -> None:
        """初始化或获取 ChromaDB 集合"""
        try:
            existing_collections = [col.name for col in self._client.list_collections()]

            if self.collection_name in existing_collections:
                self._collection = self._client.get_collection(
                    name=self.collection_name,
                    embedding_function=self._embedding_function
                )
                logger.info("获取已存在的集合: %s", self.collection_name)
            else:
                self._collection = self._client.create_collection(
                    name=self.collection_name,
                    embedding_function=self._embedding_function,
                    metadata={"description": "代码片段向量存储"}
                )
                logger.info("创建新集合: %s", self.collection_name)
        except Exception as error:
            logger.error("初始化集合失败: %s", str(error))
            raise

    async def add_code_fragments(
        self,
        fragments: List[Dict[str, Any]]
    ) -> int:
        """
        添加代码片段到向量数据库

        Args:
            fragments: 代码片段列表，每个片段包含：
                - id: 唯一标识符
                - content: 代码内容
                - file_path: 文件路径
                - language: 编程语言
                - metadata: 其他元数据（类名、函数名等）

        Returns:
            成功添加的片段数量
        """
        if not self.collection:
            logger.error("集合未初始化")
            return 0
        
        if not fragments:
            logger.warning("没有代码片段需要添加")
            return 0
        
        try:
            # 准备数据
            ids = []
            documents = []
            metadatas = []
            
            for fragment in fragments:
                fragment_id = fragment.get("id", "")
                content = fragment.get("content", "")
                file_path = fragment.get("file_path", "")
                language = fragment.get("language", "unknown")
                additional_metadata = fragment.get("metadata", {})
                
                if not fragment_id or not content:
                    continue
                
                ids.append(fragment_id)
                documents.append(content)
                metadatas.append({
                    "file_path": file_path,
                    "language": language,
                    **additional_metadata
                })
            
            if not ids:
                logger.warning("没有有效的代码片段")
                return 0
            
            # 批量添加到 ChromaDB
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            
            logger.info("成功添加 %d 个代码片段到向量数据库", len(ids))
            return len(ids)
            
        except Exception as error:
            logger.error("添加代码片段失败: %s", str(error))
            return 0

    async def search_similar_code(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        语义搜索相似的代码片段

        Args:
            query: 查询文本（自然语言或代码片段）
            n_results: 返回结果数量
            filters: 元数据过滤条件（如 {"language": "python"}）

        Returns:
            相似代码片段列表，按相似度排序
        """
        if not self.collection:
            logger.error("集合未初始化")
            return []
        
        try:
            # 执行查询
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filters
            )
            
            # 格式化结果
            formatted_results = []
            
            if results and results.get("ids") and results["ids"][0]:
                for i, doc_id in enumerate(results["ids"][0]):
                    formatted_results.append({
                        "id": doc_id,
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "similarity": 1.0 - results["distances"][0][i] if "distances" in results else None
                    })
            
            logger.info("查询 '%s' 找到 %d 个结果", query[:50], len(formatted_results))
            return formatted_results
            
        except Exception as error:
            logger.error("语义搜索失败: %s", str(error))
            return []

    async def get_fragment_by_id(self, fragment_id: str) -> Optional[Dict[str, Any]]:
        """
        根据 ID 获取代码片段

        Args:
            fragment_id: 片段唯一标识符

        Returns:
            代码片段信息，如果不存在则返回 None
        """
        if not self.collection:
            logger.error("集合未初始化")
            return None
        
        try:
            results = self.collection.get(
                ids=[fragment_id],
                include=["documents", "metadatas"]
            )
            
            if results and results.get("ids") and results["ids"]:
                return {
                    "id": results["ids"][0],
                    "content": results["documents"][0] if results.get("documents") else "",
                    "metadata": results["metadatas"][0] if results.get("metadatas") else {}
                }
            
            return None
            
        except Exception as error:
            logger.error("获取代码片段失败: %s", str(error))
            return None

    async def delete_by_file_path(self, file_path: str) -> int:
        """
        删除指定文件路径的所有代码片段

        Args:
            file_path: 文件路径

        Returns:
            删除的片段数量
        """
        if not self.collection:
            logger.error("集合未初始化")
            return 0
        
        try:
            # 查找所有匹配的片段
            results = self.collection.get(
                where={"file_path": file_path},
                include=["documents"]
            )
            
            if not results or not results.get("ids"):
                logger.info("没有找到文件 %s 的代码片段", file_path)
                return 0
            
            # 删除片段
            self.collection.delete(ids=results["ids"])
            
            logger.info("删除文件 %s 的 %d 个代码片段", file_path, len(results["ids"]))
            return len(results["ids"])
            
        except Exception as error:
            logger.error("删除代码片段失败: %s", str(error))
            return 0

    async def get_collection_stats(self) -> Dict[str, Any]:
        """
        获取集合统计信息

        Returns:
            统计信息字典
        """
        if not self.collection:
            return {"error": "集合未初始化"}
        
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "total_fragments": count,
                "persist_directory": settings.CHROMA_PERSIST_DIR
            }
        except Exception as error:
            logger.error("获取统计信息失败: %s", str(error))
            return {"error": str(error)}

    async def reset_collection(self) -> bool:
        """
        重置集合（清空所有数据）

        Returns:
            是否成功
        """
        if not self.collection:
            return False

        try:
            self._client.delete_collection(name=self.collection_name)
            self._collection = None
            self._initialize_collection()
            logger.info("集合 %s 已重置", self.collection_name)
            return True
        except Exception as error:
            logger.error("重置集合失败: %s", str(error))
            return False


# 全局单例
vector_service = VectorService()
