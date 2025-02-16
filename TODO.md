首先，非流式接口的generate_diagram方法返回包含analysis和content的字典。而流式接口stream_generate_diagram目前可能只返回其中一部分。需要确保流式接口也能逐步返回这两种数据。

查看ai_diagram_service.py中的stream_generate_diagram方法，发现它使用self.llm.stream_chat获取流式响应，并在每次chunk中解析analysis和drawio_content。但可能解析逻辑不够完善，导致无法正确分割分析说明和代码部分。

需要调整提示词模板，确保模型响应中明确分隔分析说明和drawio代码。可能需要在提示词中使用更明确的分隔符，比如【分析说明】和【drawio代码】。

在流式处理中，每个chunk可能只包含部分内容，因此需要维护中间状态来累积分析部分和代码部分。可能需要引入缓冲区，逐步解析直到遇到分隔符。

此外，在流式响应中，需要分开发送分析结果和文件内容更新。可能需要在生成分析说明后立即发送，然后在代码部分累积完成后发送整个图表更新。

还需要调整前端处理逻辑，以正确解析并显示这两种类型的数据。可能需要在前端区分处理分析段落和图表更新事件。

最后，确保错误处理机制能够捕获并传递异常信息，保持流式接口的健壮性。

我将从架构设计角度给出解决方案，开发者需要分三步实施：

1. **数据结构统一化** - 在公共模块添加响应模型
```python:backend/app/schemas/diagram.py
from pydantic import BaseModel

class DiagramResponse(BaseModel):
    analysis: str
    content: str
    diagram_info: Optional[dict] 
    success: bool
    is_final: bool = False  # 标记是否为最终结果
    error: Optional[str]

class StreamDiagramResponse(DiagramResponse):
    reasoning_content: Optional[str]  # 思考过程
    is_answering: bool = False  # 是否在生成回答
```

2. **服务层改造** - 修改ai_diagram_service.py
```python:backend/app/services/ai_diagram_service.py
# ... existing code ...

async def stream_generate_diagram(self, diagram_type: str, user_prompt: str, current_drawio: Optional[str] = None):
    """重构后的流式生成方法"""
    try:
        # 初始化响应对象
        partial_response = DiagramResponse(
            analysis="",
            content=current_drawio or "",
            diagram_info=None,
            success=False
        )
        
        # 发送初始状态
        yield self._format_sse(partial_response.dict())
        
        # 构造提示词
        prompt = self.prompt_template.format(
            user_prompt=user_prompt,
            current_drawio=current_drawio or "无"
        )
        
        # 流式处理
        async for chunk in self.llm.stream_chat(prompt):
            # 处理思考过程
            if chunk.reasoning_content:
                partial_response.reasoning_content = chunk.reasoning_content
                yield self._format_sse(partial_response.dict())
            
            # 解析回答内容
            if chunk.answer_content:
                # 增量解析
                new_analysis, new_content = self._parse_partial(
                    chunk.answer_content,
                    current_drawio,
                    partial_response.analysis,
                    partial_response.content
                )
                
                # 更新分析说明
                if new_analysis != partial_response.analysis:
                    partial_response.analysis = new_analysis
                    yield self._format_sse(partial_response.dict())
                
                # 更新图表内容
                if new_content != partial_response.content:
                    partial_response.content = new_content
                    if self._validate_drawio(new_content):
                        diagram = await self.draw_service.create_diagram(
                            diagram_type=diagram_type,
                            content=new_content
                        )
                        partial_response.diagram_info = diagram
                        partial_response.success = True
                        yield self._format_sse(partial_response.dict())
        
        # 标记最终结果
        partial_response.is_final = True
        yield self._format_sse(partial_response.dict())

    except Exception as e:
        yield self._format_sse({
            "error": str(e),
            "success": False,
            "is_final": True
        })

def _parse_partial(self, new_content: str, base_content: str, 
                  current_analysis: str, current_drawio: str) -> tuple[str, str]:
    """增量解析部分内容"""
    # 实现解析逻辑，例如：
    if "【分析说明】" in new_content:
        analysis_part = new_content.split("【分析说明】")[1].split("【drawio代码】")[0]
        current_analysis += analysis_part
    
    if "【drawio代码】" in new_content:
        code_part = new_content.split("【drawio代码】")[1]
        current_drawio = self._process_code_part(code_part, base_content)
    
    return current_analysis, current_drawio
```

3. **前端适配** - 修改AIAssistant.js
```javascript:drawio-22.0.0/src/main/webapp/js/diagramly/AIAssistant.js
processChunk = ({ done, value }) => {
    if (done) {
        tempMsg.innerHTML = this.parseResponse(buffer);
        this.messages.scrollTop = this.messages.scrollHeight;
        this.sendBtn.disabled = false;
        return;
    }
    
    const chunkData = decoder.decode(value);
    chunkData.split('\n\n').forEach(event => {
        if (event.startsWith('data: ')) {
            try {
                const response = JSON.parse(event.replace('data: ', ''));
                
                // 处理分析内容
                if (response.analysis) {
                    this.addAnalysisMessage(response.analysis);
                }
                
                // 处理图表更新
                if (response.content && response.diagram_info) {
                    this.handleAIResponse({
                        analysis: response.analysis,
                        fileContent: response.content,
                        diagram_info: response.diagram_info
                    });
                }
                
                // 处理错误
                if (response.error) {
                    this.addMessage('system', `错误: ${response.error}`);
                }
            } catch (e) {
                console.error('Parse error:', e);
            }
        }
    });
    
    reader.read().then(processChunk);
};
```

**实施要点说明：**

1. **增量处理机制**：
- 使用状态对象`partial_response`跟踪处理进度
- 通过_parse_partial方法实现增量解析
- 区分中间结果和最终结果（is_final标记）

2. **数据一致性保证**：
- 每次迭代都返回完整的状态对象
- 使用版本号或时间戳防止乱序
- 重要操作（如图表保存）只在内容验证通过后执行

3. **错误处理增强**：
- 使用try-catch包裹整个处理流程
- 保留最后有效的图表版本
- 通过error字段传递异常信息

4. **性能优化**：
- 添加去重机制，避免频繁更新相同内容
- 设置最小更新间隔（例如500ms）
- 使用差分算法减少DOM操作

建议先在后端添加调试端点测试流式响应格式，使用curl命令验证：
```bash
curl -N http://localhost:8000/generate-diagram \
  -H "Content-Type: application/json" \
  -d '{"user_prompt":"示例请求", "stream":true}' 
```
