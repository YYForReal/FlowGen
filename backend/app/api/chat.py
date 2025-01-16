from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.models.chat import ChatMessage
from app.services.ai_service import AIService

router = APIRouter()
ai_service = AIService()

@router.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            response = await ai_service.process_message(data)
            await websocket.send_json(response)
    except WebSocketDisconnect:
        print("Client disconnected")

@router.post("/chat")
async def chat(message: ChatMessage):
    """
    聊天接口 - 用于测试，生产环境建议使用WebSocket
    """
    # 测试用的硬编码drawio字符串
    test_drawio = """
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="2" value="开始" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="360" y="80" width="120" height="60" as="geometry"/>
        </mxCell>
        <mxCell id="3" value="处理" style="rounded=0;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="360" y="200" width="120" height="60" as="geometry"/>
        </mxCell>
        <mxCell id="4" value="结束" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="360" y="320" width="120" height="60" as="geometry"/>
        </mxCell>
        <mxCell id="5" value="" style="endArrow=classic;html=1;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="2" target="3">
          <mxGeometry width="50" height="50" relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="6" value="" style="endArrow=classic;html=1;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="3" target="4">
          <mxGeometry width="50" height="50" relative="1" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
    """
    
    return {
        "message": "这是一个简单的流程图示例",
        "drawio_content": test_drawio
    } 