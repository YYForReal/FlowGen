import os
from typing import Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class AIService:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv('ZHIPU_API_KEY'),
            base_url=os.getenv('BASE_URL', "https://open.bigmodel.cn/api/paas/v4/")
        )
        self.chat_model = os.getenv('CHAT_MODEL', "glm-4-flash")
        
        # 系统提示词
        self.system_prompt = """你是一个专业的科研绘图助手。你可以：
1. 理解用户的图表需求
2. 提供合适的图表建议
3. 生成符合学术规范的图表

当用户描述需求时，你应该：
1. 分析用户意图
2. 确定图表类型
3. 收集必要的数据
4. 生成图表描述或代码
"""
        
        # 消息历史
        self.messages = [{"role": "system", "content": self.system_prompt}]
    
    async def process_message(self, message: str) -> Dict[str, Any]:
        """处理用户消息"""
        # 添加用户消息
        self.messages.append({"role": "user", "content": message})
        
        try:
            # 调用AI获取响应
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=self.messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            # 获取AI响应
            ai_response = response.choices[0].message.content
            self.messages.append({"role": "assistant", "content": ai_response})
            
            # 测试用的drawio字符串
            test_drawio = """
            <mxGraphModel>
                <root>
                    <mxCell id="0"/>
                    <mxCell id="1" parent="0"/>
                    <mxCell id="2" value="测试节点" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
                        <mxGeometry x="360" y="80" width="120" height="60" as="geometry"/>
                    </mxCell>
                </root>
            </mxGraphModel>
            """
            
            # 返回响应
            return {
                "message": ai_response,
                "diagram": {
                    "type": "flow_chart",
                    "content": test_drawio
                },
                "suggestions": [
                    "添加更多节点",
                    "修改样式",
                    "导出图片"
                ]
            }
            
        except Exception as e:
            print(f"Error in AI service: {e}")
            return {
                "message": "抱歉，处理您的请求时出现错误。",
                "error": str(e)
            } 