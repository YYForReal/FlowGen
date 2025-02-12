from typing import Generator, Optional, Dict, Any
import os
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
from pydantic import BaseModel

load_dotenv(find_dotenv())

class GLMResponse(BaseModel):
    """GLM响应模型"""
    answer_content: str = ""
    is_answering: bool = False
    usage: Optional[Dict[str, Any]] = None

class DeepseekResponse(BaseModel):
    """Deepseek响应模型"""
    reasoning_content: str = ""
    answer_content: str = ""
    is_answering: bool = False
    usage: Optional[Dict[str, Any]] = None

class DeepseekLLM:
    """Deepseek LLM工具类"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: str = "deepseek-reasoner"
    ):
        """
        初始化Deepseek LLM客户端
        
        Args:
            api_key: API密钥，默认从环境变量DASHSCOPE_API_KEY获取
            base_url: API基础URL，默认从环境变量DASHSCOPE_API_BASE获取
            model_name: 模型名称，默认为deepseek-r1
        """
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.base_url = base_url or os.getenv("DEEPSEEK_API_BASE")
        self.model_name = model_name # "deepseek-reasoner | deepseek-chat"

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def stream_chat(
        self,
        messages: list[dict[str, str]],
        include_usage: bool = False
    ) -> Generator[GLMResponse, None, None]:
        """
        流式对话
        
        Args:
            messages: 消息列表（需包含role和content）
            include_usage: 是否包含token使用情况
            
        Yields:
            GLMResponse: 包含回答内容的响应对象
        """
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            stream=True,
            stream_options={"include_usage": include_usage} if include_usage else None
        )

        response = GLMResponse()
        
        for chunk in completion:
            if chunk.choices == []:
                if hasattr(chunk, 'usage'):
                    response.usage = chunk.usage.model_dump()
                yield response
                continue
                
            delta = chunk.choices[0].delta
            if not delta.content:
                continue
                
            # 开始回答
            if not response.is_answering:
                response.is_answering = True
                
            # 更新回答内容
            response.answer_content += delta.content
            yield response

    def chat(self, prompt: str) -> GLMResponse:
        """
        单次对话
        
        Args:
            messages: 消息列表（需包含role和content）
            
        Returns:
            GLMResponse: 包含回答内容的响应对象
        """
        messages = [
            {"role": "user", "content": prompt}
        ]
        print("prompt len",len(prompt))
        print("model",self.model_name)
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            timeout=300.0
        )
        
        result = GLMResponse()
        result.answer_content = response.choices[0].message.content
        result.is_answering = True
        
        if hasattr(response, 'usage'):
            result.usage = response.usage.model_dump()
            
        return result
