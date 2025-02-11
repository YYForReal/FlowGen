from fastapi import APIRouter, WebSocket, HTTPException
from typing import Dict, Any
from app.services.ai_service import AIService
from app.models.chat import ChatMessage

router = APIRouter()
ai_service = AIService()

@router.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket聊天接口
    """
    await websocket.accept()
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            
            # 流式处理消息
            async for response in ai_service.stream_message(data):
                await websocket.send_json(response)
    except Exception as e:
        await websocket.send_json({
            "status": "error",
            "message": str(e),
            "type": "error"
        })

@router.post("/chat")
async def chat(message: ChatMessage) -> Dict[str, Any]:
    """
    聊天接口 - 用于测试，生产环境建议使用WebSocket
    
    Args:
        message: 聊天消息对象
        
    Returns:
        Dict[str, Any]: 响应结果
    """
    return await ai_service.process_message(message.content) 