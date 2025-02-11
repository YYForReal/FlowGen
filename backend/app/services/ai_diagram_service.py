from typing import Optional, Dict, Any
from app.llm.deepseek import DeepseekLLM
from app.services.draw_service import DrawService

class AIDiagramService:
    """AI图表生成服务"""
    
    def __init__(self, draw_service: DrawService, llm: DeepseekLLM):
        self.draw_service = draw_service
        self.llm = llm
        self.prompt_template = """
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

    async def generate_diagram(
        self,
        diagram_type: str,
        user_prompt: str,
        current_drawio: Optional[str] = None
    ) -> Dict[str, Any]:
        """生成图表核心逻辑"""
        try:
            # 构造提示词
            prompt = self.prompt_template.format(
                user_prompt=user_prompt,
                current_drawio=current_drawio or "无"
            )
            
            # 调用大模型生成
            response = self.llm.chat(prompt)
            
            # 解析响应内容
            analysis, drawio_content = self._parse_response(
                response.answer_content,
                current_drawio
            )
            
            # 存储生成的图表
            diagram = None
            if drawio_content:
                diagram = await self.draw_service.create_diagram(
                    diagram_type=diagram_type,
                    content=drawio_content
                )
            
            return {
                "analysis": analysis,
                "content": drawio_content,
                "diagram_info": diagram,
                "success": True
            }
            
        except Exception as e:
            return {
                "analysis": str(e),
                "content": current_drawio or "",
                "diagram_info": None,
                "success": False
            }

    def _parse_response(
        self,
        response: str,
        current_drawio: Optional[str]
    ) -> tuple[str, str]:
        """解析大模型响应"""
        analysis = ""
        drawio_content = current_drawio or ""
        
        if "【分析说明】" in response:
            parts = response.split("【drawio代码】")
            analysis_part = parts[0].replace("【分析说明】", "").strip()
            
            analysis = analysis_part
            if len(parts) > 1:
                code_part = parts[1].strip()
                drawio_content = code_part 
                # if "<mxfile>" in code_part:
                #     drawio_content = code_part.split("<mxfile>")[1].split("</mxfile>")[0].strip()
        
        return analysis, drawio_content 