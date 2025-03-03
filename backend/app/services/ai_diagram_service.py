from typing import Optional, Dict, Any
from app.llm.deepseek import DeepseekLLM
from app.services.draw_service import DrawService
from app.utils.drawio_xml_processor import DrawIOXMLProcessor
import tempfile
import os

class AIDiagramService:
    """AI图表生成服务"""
    
    def __init__(self, draw_service: DrawService, llm: DeepseekLLM):
        self.draw_service = draw_service
        self.llm = llm
        self.xml_processor = DrawIOXMLProcessor(llm_service=llm)
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
        current_drawio: Optional[str] = None,
        output_strategy: str = "v2"
    ) -> Dict[str, Any]:
        """生成图表核心逻辑"""
        try:
            if output_strategy == "v2" and current_drawio:
                # 使用drawio_xml_processor进行增量处理
                # 创建临时文件用于处理
                with tempfile.NamedTemporaryFile(suffix='.drawio', delete=False) as temp_input:
                    temp_input.write(current_drawio.encode('utf-8'))
                    temp_input_path = temp_input.name
                
                with tempfile.NamedTemporaryFile(suffix='.drawio', delete=False) as temp_output:
                    temp_output_path = temp_output.name

                try:
                    # 提取XML元素
                    xml_content = self.xml_processor.extract_xml_by_level(temp_input_path)
                    # 生成优化后的XML
                    optimized_xml = self.xml_processor.generate_optimized_xml(xml_content, user_prompt)
                    # 替换元素
                    result = self.xml_processor.replace_elements_by_id(temp_input_path, optimized_xml, temp_output_path)

                    if result["success"]:
                        with open(temp_output_path, 'r', encoding='utf-8') as f:
                            drawio_content = f.read()
                        
                        # 存储生成的图表
                        diagram = await self.draw_service.create_diagram(
                            diagram_type=diagram_type,
                            content=drawio_content
                        )
                        
                        return {
                            "analysis": result["message"],
                            "content": drawio_content,
                            "diagram_info": diagram,
                            "success": True
                        }
                finally:
                    # 清理临时文件
                    if os.path.exists(temp_input_path):
                        os.unlink(temp_input_path)
                    if os.path.exists(temp_output_path):
                        os.unlink(temp_output_path)
            
            # 使用原始全量输出模式
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
            
            #  直接截取开头的<mxfile..., 结尾的</mxfile>
            drawio_content = drawio_content.split("<mxfile")[1].split("</mxfile>")[0].strip()
            # 补全<mxfile>...</mxfile>
            drawio_content = "<mxfile " + drawio_content + "</mxfile>"

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
            # 初始化状态对象
            partial_response = {
                "analysis": "",
                "content": current_drawio or "",
                "diagram_info": None,
                "success": False,
                "is_final": False
            }
            
            # 构造提示词
            prompt = self.prompt_template.format(
                user_prompt=user_prompt,
                current_drawio=current_drawio or "无"
            )
            
            # 用于累积内容的缓冲区
            analysis_buffer = ""
            drawio_buffer = ""
            is_in_analysis = False
            is_in_drawio = False
            
            # 调用大模型流式生成
            async for chunk in self.llm.stream_chat(prompt):
                # 处理思考过程
                if chunk.reasoning_content:
                    yield self._format_sse({
                        "type": "reasoning",
                        "content": chunk.reasoning_content
                    })
                    continue
                
                if chunk.answer_content:
                    content = chunk.answer_content
                    
                    # 检测分隔符
                    if "【分析说明】" in content:
                        is_in_analysis = True
                        is_in_drawio = False
                        content = content.split("【分析说明】")[1]
                    elif "【drawio代码】" in content:
                        is_in_analysis = False
                        is_in_drawio = True
                        content = content.split("【drawio代码】")[1]
                    
                    # 根据当前状态累积内容
                    if is_in_analysis:
                        analysis_buffer += content
                        partial_response["analysis"] = analysis_buffer.strip()
                        yield self._format_sse({
                            "type": "analysis",
                            "content": partial_response["analysis"]
                        })
                    
                    if is_in_drawio:
                        drawio_buffer += content
                        if "<mxfile" in drawio_buffer and "</mxfile>" in drawio_buffer:
                            # 提取完整的drawio内容
                            drawio_content = drawio_buffer.split("<mxfile")[1].split("</mxfile>")[0].strip()
                            drawio_content = "<mxfile " + drawio_content + "</mxfile>"
                            
                            if self._validate_drawio(drawio_content):
                                partial_response["content"] = drawio_content
                                # 创建图表
                                diagram = await self.draw_service.create_diagram(
                                    diagram_type=diagram_type,
                                    content=drawio_content
                                )
                                partial_response["diagram_info"] = diagram
                                partial_response["success"] = True
                                
                                yield self._format_sse({
                                    "type": "diagram",
                                    "content": partial_response["content"],
                                    "diagram_info": diagram
                                })
                
                # 处理使用量信息
                if chunk.usage:
                    yield self._format_sse({
                        "type": "usage",
                        "content": chunk.usage
                    })
            
            # 标记最终结果
            partial_response["is_final"] = True
            yield self._format_sse({
                "type": "final",
                "response": partial_response
            })
                    
        except Exception as e:
            yield self._format_sse({
                "type": "error",
                "content": str(e)
            })

    def _validate_drawio(self, content: str) -> bool:
        """验证drawio内容是否有效"""
        return (
            content 
            and content.startswith("<mxfile") 
            and content.endswith("</mxfile>")
            and len(content) > 20  # 简单的长度检查
        )

    def _format_sse(self, data: dict) -> str:
        """格式化Server-Sent Events (SSE)数据"""
        import json
        return f"data: {json.dumps(data)}\n\n"