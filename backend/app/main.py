from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import uvicorn
import os
from dotenv import load_dotenv

# 导入服务和模型
from app.services.ai_service import AIService
from app.models.chat import ChatMessage, DiagramRequest

# 加载环境变量
load_dotenv()

# 创建FastAPI应用
app = FastAPI(
    title="FlowGen API",
    description="FlowGen - 科研绘图助手API文档",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI 地址
    redoc_url="/redoc",  # ReDoc 地址
    openapi_url="/openapi.json"  # OpenAPI 文档地址
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建AI服务实例
ai_service = AIService()

@app.get("/")
async def root():
    """
    根路由，返回API基本信息
    """
    return {
        "name": "FlowGen API",
        "version": "1.0.0",
        "status": "running"
    }

@app.websocket("/ws/chat")
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

@app.post("/chat")
async def chat(message: ChatMessage) -> Dict[str, Any]:
    """
    聊天接口 - 用于测试，生产环境建议使用WebSocket
    
    Args:
        message: 聊天消息对象
        
    Returns:
        Dict[str, Any]: 响应结果
    """
    return await ai_service.process_message(message.content)

@app.post("/diagrams")
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

if __name__ == "__main__":
    # 启动服务
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # 开发环境启用热重载
    ) 