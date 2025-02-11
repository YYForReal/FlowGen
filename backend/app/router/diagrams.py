from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from app.models.chat import DiagramRequest, DiagramGenerationRequest, DiagramGenerationResponse
from app.llm.deepseek import DeepseekLLM
from app.services.draw_service import DrawService
from app.services.ai_diagram_service import AIDiagramService

router = APIRouter()
deepseek_llm = DeepseekLLM()
draw_service = DrawService()

PROMPT_TEMPLATE = """
你是一个专业的图表生成助手，请根据以下需求生成或修改drawio图表：

用户需求：
{user_prompt}

当前图表内容（可选）：
{current_drawio}

请按以下格式响应：
【分析说明】
你的分析说明

【drawio代码】
<mxfile>
生成的drawio代码
</mxfile>
"""

def get_ai_diagram_service():
    return AIDiagramService(
        draw_service=DrawService(),
        llm=DeepseekLLM()
    )

@router.post("/diagrams")
async def create_diagram(request: DiagramRequest) -> Dict[str, Any]:
    """
    创建图表
    
    Args:
        request: 图表请求对象
        
    Returns:
        Dict[str, Any]: 图表信息
    """
    try:
        # TODO: 实现图表生成逻辑
        return {
            "id": "test-diagram-001",
            "type": request.type,
            "content": "图表内容",
            "preview_url": "/diagrams/test-diagram-001.png"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-diagram", response_model=DiagramGenerationResponse)
async def generate_diagram(
    request: DiagramGenerationRequest,
    service: AIDiagramService = Depends(get_ai_diagram_service)
):
    return await service.generate_diagram(
        diagram_type=request.type,
        user_prompt=request.user_prompt,
        current_drawio=request.current_drawio
    ) 