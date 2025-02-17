from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from app.models.chat import DiagramRequest, DiagramGenerationRequest, DiagramGenerationResponse
from app.llm.deepseek import DeepseekLLM
from app.services.draw_service import DrawService
from app.services.ai_diagram_service import AIDiagramService
from fastapi.responses import StreamingResponse
import json
from app.llm.glm import GLMLLM

router = APIRouter()
deepseek_llm = DeepseekLLM()
draw_service = DrawService()

def get_ai_diagram_service(model_name: str = "deepseek-r1"):
    """根据模型名称返回对应的服务实例"""
    llm = DeepseekLLM(model_name=model_name) if model_name.startswith("deepseek") else GLMLLM(model_name=model_name )
    return AIDiagramService(
        draw_service=DrawService(),
        llm=llm
    )

@router.post("/generate-diagram")
async def generate_diagram(
    request: DiagramGenerationRequest,
):
    service = get_ai_diagram_service(request.model_name)
    if request.stream:
        return StreamingResponse(
            service.stream_generate_diagram(
                diagram_type=request.type,
                user_prompt=request.user_prompt,
                current_drawio=request.current_drawio
            ),
            media_type="text/event-stream",
            headers={
                "X-Accel-Buffering": "no",  # 禁用Nginx缓冲
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Max-Age": "86400"
            }
        )
    else:
        return await service.generate_diagram(
            diagram_type=request.type,
            user_prompt=request.user_prompt,
            current_drawio=request.current_drawio
        )

async def stream_generate_diagram(self, diagram_type, user_prompt, current_drawio):
    try:
        full_prompt = self._build_prompt(diagram_type, user_prompt, current_drawio)
        
        async for chunk in self.llm.stream_chat(full_prompt):
            # 先发送思考过程
            if chunk.reasoning_content:
                yield self._format_sse({
                    "reasoning_content": chunk.reasoning_content,
                    "is_answering": False
                })
            
            # 发送正式回答
            if chunk.answer_content:
                yield self._format_sse({
                    "answer_content": chunk.answer_content,
                    "is_answering": chunk.is_answering
                })
            
            # 最后发送使用量
            if chunk.usage:
                yield self._format_sse({
                    "usage": chunk.usage,
                    "is_answering": False
                })
                
    except Exception as e:
        yield self._format_sse({
            "error": str(e),
            "is_answering": False
        })

def _format_sse(self, data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n" 