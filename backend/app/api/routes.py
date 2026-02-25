import logging

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from app.services.project_service import project_service
from app.services.script_service import script_service
from app.services.explain_service import explain_service
from app.services.architecture_service import architecture_service
from app.services.vector_service import vector_service
from app.services.llm_service import LLMError

logger = logging.getLogger(__name__)

api_router = APIRouter()

# Pydantic 模型
class GenerateScriptRequest(BaseModel):
    scenario: str
    task_id: str

class ExplainTermRequest(BaseModel):
    code_snippet: str

class UploadResponse(BaseModel):
    task_id: str
    status: str
    message: str
    file_list: list[str] = []

class ProjectStructureResponse(BaseModel):
    tree: dict
    mermaid_diagram: str

class ScriptResponse(BaseModel):
    scenario: str
    characters: list
    dialogues: list

class ExplainTermResponse(BaseModel):
    term: str
    plain_explanation: str
    analogy: str

class ArchitectureVisualizationResponse(BaseModel):
    layers: list
    scenarios: list
    techTerms: list

class ProjectDetailsResponse(BaseModel):
    taskId: str
    fileName: str
    structure: dict | None = None
    architecture: dict | None = None
    chatScript: dict | None = None
    termDictionary: list | None = None
    status: str
    progress: int

class SearchCodeRequest(BaseModel):
    query: str
    n_results: int = 5
    language: str | None = None

class SearchResult(BaseModel):
    id: str
    content: str
    metadata: dict
    similarity: float | None = None

class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
    total: int

class HistoryItemResponse(BaseModel):
    task_id: str
    file_name: str
    created_at: str
    status: str
    file_count: int | None = None

class HistoryListResponse(BaseModel):
    items: list[HistoryItemResponse]

@api_router.get("/history/list", response_model=HistoryListResponse)
async def get_history_list():
    """
    获取历史记录列表
    """
    # 调用服务层获取历史记录
    history_data = project_service.get_history_list()
    
    # 将时间戳转换为 ISO 格式字符串
    items = []
    for item in history_data:
        from datetime import datetime
        created_at_str = datetime.fromtimestamp(item["created_at"]).isoformat()
        
        items.append(HistoryItemResponse(
            task_id=item["task_id"],
            file_name=item["file_name"],
            created_at=created_at_str,
            status=item["status"],
            file_count=item.get("file_count")
        ))
    
    return HistoryListResponse(items=items)


@api_router.post("/upload", response_model=UploadResponse)
async def upload_project(file: UploadFile = File(...)):
    """
    上传 ZIP 包，返回任务 ID 和文件列表
    """
    file_content = await file.read()

    try:
        result = await project_service.upload_and_parse(file_content, file.filename)
    except ValueError as validation_error:
        raise HTTPException(status_code=400, detail=str(validation_error))

    return UploadResponse(
        task_id=result["task_id"],
        status="success",
        message="项目上传成功",
        file_list=result.get("file_list", [])
    )


@api_router.get("/project/structure", response_model=ProjectStructureResponse)
async def get_project_structure(task_id: str):
    """
    获取项目白话版的目录树
    """
    # 获取项目数据
    project_data = project_service.get_project_data(task_id)
    
    if not project_data:
        raise HTTPException(status_code=404, detail="项目未找到或未完成解析")
    
    return ProjectStructureResponse(
        tree=project_data["tree"],
        mermaid_diagram=project_data["mermaid_diagram"]
    )


@api_router.post("/chat/generate", response_model=ScriptResponse)
async def generate_script(request: GenerateScriptRequest):
    """
    输入业务场景关键词，获取拟人化群聊剧本
    """
    # 调用服务层生成剧本
    script = await script_service.generate_chat_script(request.scenario, request.task_id)
    
    return ScriptResponse(
        scenario=script["scenario"],
        characters=script["characters"],
        dialogues=script["dialogues"]
    )


@api_router.get("/explain/term", response_model=ExplainTermResponse)
async def explain_term(code_snippet: str):
    """
    传入代码片段，返回小白版的术语解释
    """
    # 调用服务层解释术语
    explanation = await explain_service.explain_term(code_snippet)
    
    return ExplainTermResponse(
        term=explanation["term"],
        plain_explanation=explanation["plain_explanation"],
        analogy=explanation["analogy"]
    )


@api_router.get("/task/status")
async def get_task_status(task_id: str):
    """
    获取任务解析状态
    """
    # 调用服务层获取任务状态
    task_info = project_service.get_task_status(task_id)
    
    return task_info

@api_router.get("/architecture/visualization", response_model=ArchitectureVisualizationResponse)
async def get_architecture_visualization(task_id: str):
    """
    获取架构可视化数据（分层、场景、术语）。
    需要项目解析完成后才能调用，否则返回 404。
    """
    # 先检查任务状态
    task_status = project_service.get_task_status(task_id)
    if task_status["status"] == "not_found":
        raise HTTPException(status_code=404, detail="任务不存在，请先上传代码文件")
    if task_status["status"] == "processing":
        raise HTTPException(status_code=202, detail="项目正在解析中，请稍后再试")
    if task_status["status"] == "failed":
        raise HTTPException(
            status_code=400,
            detail=task_status.get("message", "项目解析失败，请重新上传"),
        )

    try:
        visualization = await architecture_service.generate_architecture_visualization(
            task_id
        )
    except ValueError as validation_error:
        raise HTTPException(status_code=404, detail=str(validation_error))
    except LLMError as llm_error:
        logger.error("LLM 调用失败: %s", str(llm_error))
        raise HTTPException(
            status_code=502,
            detail="AI 大模型调用失败，请检查 API Key 配置后重试",
        )

    return ArchitectureVisualizationResponse(
        layers=visualization["layers"],
        scenarios=visualization["scenarios"],
        techTerms=visualization["techTerms"],
    )


@api_router.get("/project/{task_id}", response_model=ProjectDetailsResponse)
async def get_project_details(task_id: str):
    """
    获取项目的聚合详情数据，包括结构、架构、群聊剧本和术语词典。
    解析未完成时返回当前进度，解析完成后返回完整数据。
    """
    task_status = project_service.get_task_status(task_id)

    if task_status["status"] == "not_found":
        raise HTTPException(status_code=404, detail="任务不存在，请先上传代码文件")

    # 基础响应（解析中或失败时也能返回进度信息）
    response_data: dict = {
        "taskId": task_id,
        "fileName": "",
        "structure": None,
        "architecture": None,
        "chatScript": None,
        "termDictionary": None,
        "status": task_status["status"],
        "progress": task_status.get("progress", 0),
    }

    # 从任务数据中获取文件名
    task_data = project_service.tasks.get(task_id, {})
    file_list = task_data.get("file_list", [])
    response_data["fileName"] = file_list[0] if file_list else "未知项目"

    if task_status["status"] != "completed":
        return ProjectDetailsResponse(**response_data)

    # 解析完成，填充完整数据
    project_data = project_service.get_project_data(task_id)
    if project_data:
        response_data["structure"] = project_data.get("tree")
        response_data["architecture"] = {
            "mermaidCode": project_data.get("mermaid_diagram", ""),
        }

    # 获取架构可视化数据（包含群聊剧本和术语词典）
    try:
        visualization = await architecture_service.generate_architecture_visualization(
            task_id
        )
        # 取第一个场景作为默认群聊剧本
        scenarios = visualization.get("scenarios", [])
        if scenarios:
            first_scenario = scenarios[0]
            response_data["chatScript"] = {
                "scenario": first_scenario.get("title", ""),
                "characters": first_scenario.get("characters", []),
                "dialogues": first_scenario.get("messages", []),
            }

        # 术语词典
        tech_terms = visualization.get("techTerms", [])
        if tech_terms:
            response_data["termDictionary"] = [
                {
                    "term": term.get("term", ""),
                    "laymanExplanation": term.get("plainExplanation", ""),
                    "technicalExplanation": term.get("description", ""),
                    "examples": term.get("examples", []),
                }
                for term in tech_terms
            ]
    except (ValueError, LLMError) as error:
        logger.warning("架构可视化数据获取失败: %s", str(error))

    return ProjectDetailsResponse(**response_data)

@api_router.post("/search/code", response_model=SearchResponse)
async def search_code(request: SearchCodeRequest):
    """
    语义搜索代码片段
    """
    # 构建过滤条件
    filters = {}
    if request.language:
        filters["language"] = request.language
    
    # 调用向量服务进行语义搜索
    results = await vector_service.search_similar_code(
        query=request.query,
        n_results=request.n_results,
        filters=filters if filters else None
    )
    
    # 格式化结果
    formatted_results = [
        SearchResult(
            id=result["id"],
            content=result["content"],
            metadata=result["metadata"],
            similarity=result.get("similarity")
        )
        for result in results
    ]
    
    return SearchResponse(
        query=request.query,
        results=formatted_results,
        total=len(formatted_results)
    )

@api_router.get("/database/stats")
async def get_database_stats():
    """
    获取向量数据库统计信息
    """
    stats = await vector_service.get_collection_stats()
    return stats