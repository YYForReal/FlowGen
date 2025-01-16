from fastapi import APIRouter, HTTPException
from app.models.chat import DiagramRequest
from app.services.draw_service import DrawService

router = APIRouter()
draw_service = DrawService()

@router.post("/diagrams")
async def create_diagram(request: DiagramRequest):
    """
    创建新的图表
    """
    try:
        # 测试用的硬编码drawio字符串 - 一个简单的实验流程图
        test_drawio = """
        <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169">
          <root>
            <mxCell id="0"/>
            <mxCell id="1" parent="0"/>
            <mxCell id="2" value="实验准备" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
              <mxGeometry x="360" y="80" width="120" height="60" as="geometry"/>
            </mxCell>
            <mxCell id="3" value="数据收集" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="1">
              <mxGeometry x="360" y="200" width="120" height="60" as="geometry"/>
            </mxCell>
            <mxCell id="4" value="数据分析" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;" vertex="1" parent="1">
              <mxGeometry x="360" y="320" width="120" height="60" as="geometry"/>
            </mxCell>
            <mxCell id="5" value="结论总结" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;" vertex="1" parent="1">
              <mxGeometry x="360" y="440" width="120" height="60" as="geometry"/>
            </mxCell>
            <mxCell id="6" value="" style="endArrow=classic;html=1;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="2" target="3">
              <mxGeometry width="50" height="50" relative="1" as="geometry"/>
            </mxCell>
            <mxCell id="7" value="" style="endArrow=classic;html=1;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="3" target="4">
              <mxGeometry width="50" height="50" relative="1" as="geometry"/>
            </mxCell>
            <mxCell id="8" value="" style="endArrow=classic;html=1;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="4" target="5">
              <mxGeometry width="50" height="50" relative="1" as="geometry"/>
            </mxCell>
          </root>
        </mxGraphModel>
        """
        
        return {
            "id": "test-diagram-001",
            "type": "experiment_flow",
            "content": test_drawio,
            "preview_url": "/diagrams/test-diagram-001.png"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/diagrams/{diagram_id}")
async def get_diagram(diagram_id: str):
    """
    获取图表详情
    """
    return {
        "id": diagram_id,
        "type": "experiment_flow",
        "created_at": "2023-12-01T12:00:00Z",
        "content": "...",  # drawio内容
        "preview_url": f"/diagrams/{diagram_id}.png"
    }

@router.put("/diagrams/{diagram_id}")
async def update_diagram(diagram_id: str, request: DiagramRequest):
    """
    更新图表
    """
    return {
        "id": diagram_id,
        "type": request.type,
        "updated_at": "2023-12-01T12:00:00Z",
        "content": request.content
    }

@router.delete("/diagrams/{diagram_id}")
async def delete_diagram(diagram_id: str):
    """
    删除图表
    """
    return {"status": "success", "message": f"Diagram {diagram_id} deleted"} 