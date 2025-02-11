from fastapi import APIRouter, WebSocket
from typing import Dict, Any
from app.llm.deepseek import DeepseekLLM
from pydantic import BaseModel

router = APIRouter()
llm = DeepseekLLM()

class ChatRequest(BaseModel):
    """聊天请求模型"""
    content: str
    include_usage: bool = False

@router.websocket("/ws/deepseek")
async def websocket_endpoint(websocket: WebSocket):
    """
    Deepseek WebSocket流式问答接口
    """
    await websocket.accept()
    try:
        while True:
            # 接收消息
            data = await websocket.receive_json()
            request = ChatRequest(**data)
            
            # 流式处理消息
            for response in llm.stream_chat(request.content, request.include_usage):
                await websocket.send_json(response.model_dump())
    except Exception as e:
        await websocket.send_json({
            "status": "error",
            "message": str(e),
            "type": "error"
        })

@router.post("/deepseek/chat")
async def chat(request: ChatRequest) -> Dict[str, Any]:
    """
    Deepseek HTTP问答接口
    
    Args:
        request: 聊天请求对象
        
    Returns:
        Dict[str, Any]: 响应结果
    """
    response = llm.chat(request.content)
    return response.model_dump() 