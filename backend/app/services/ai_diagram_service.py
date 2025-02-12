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
            print("response:",response)
            # 解析响应内容
            analysis, drawio_content = self._parse_response(
                response.answer_content,
                current_drawio
            )
            
            print("drawio_content:",drawio_content)

            # 进一步过滤，如果开始出现```xml 结尾出现``` 则去掉
            # if drawio_content.startswith("```xml"):
            #     drawio_content = drawio_content.split("```xml")[1].split("```")[0].strip()

            #  直接截取开头的<mxfile..., 结尾的</mxfile>
            drawio_content = drawio_content.split("<mxfile")[1].split("</mxfile>")[0].strip()
            # 补全<mxfile>...</mxfile>
            drawio_content = "<mxfile" + drawio_content + "</mxfile>"

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
            raise e
            # return {
            #     "analysis": str(e),
            #     "content": current_drawio or "",
            #     "diagram_info": None,
            #     "success": False
            # }

    def _parse_response(
        self,
        response: str,
        current_drawio: Optional[str]
    ) -> tuple[str, str]:
        """解析大模型响应"""
        analysis = ""
        drawio_content = current_drawio or ""
        print("response:",response)
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

    async def stream_generate_diagram(
        self,
        diagram_type: str,
        user_prompt: str,
        current_drawio: Optional[str] = None
    ):
        """流式生成图表的核心逻辑"""
        try:
            # 构造提示词
            prompt = self.prompt_template.format(
                user_prompt=user_prompt,
                current_drawio=current_drawio or "无"
            )
            
            # 调用大模型流式生成
            async for chunk in self.llm.stream_chat(prompt):
                # 如果有思考过程，直接yield
                if chunk.reasoning_content:
                    yield self._format_sse({
                        "reasoning_content": chunk.reasoning_content,
                        "is_answering": False
                    })
                
                # 如果有回答内容，需要解析处理
                if chunk.answer_content:
                    analysis, drawio_content = self._parse_response(
                        chunk.answer_content,
                        current_drawio
                    )
                    
                    if drawio_content and drawio_content.startswith("<mxfile"):
                        drawio_content = drawio_content.split("<mxfile")[1].split("</mxfile>")[0].strip()
                        drawio_content = "<mxfile " + drawio_content + "</mxfile>"
                        
                        # 存储生成的图表
                        diagram = await self.draw_service.create_diagram(
                            diagram_type=diagram_type,
                            content=drawio_content
                        )
                        
                        yield self._format_sse({
                            "analysis": analysis,
                            "content": drawio_content,
                            "diagram_info": diagram,
                            "is_answering": True
                        })
                    else:
                        yield self._format_sse({
                            "analysis": analysis,
                            "is_answering": True
                        })
                
                # 如果有使用量信息，直接yield
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
        """格式化Server-Sent Events (SSE)数据"""
        import json
        return f"data: {json.dumps(data)}\n\n" 