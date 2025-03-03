from typing import Generator, Optional, Dict, Any
import os
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
from pydantic import BaseModel

load_dotenv(find_dotenv())

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
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        self.base_url = base_url or os.getenv("DASHSCOPE_API_BASE")
        self.model_name = model_name or os.getenv("DASHSCOPE_MODEL")
        # "deepseek-r1"

        # self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        # self.base_url = base_url or os.getenv("DEEPSEEK_API_BASE")
        # self.model_name = model_name # "deepseek-r1"

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def stream_chat(
        self,
        prompt: str,
        include_usage: bool = False
    ) -> Generator[DeepseekResponse, None, None]:
        """
        流式对话
        
        Args:
            prompt: 用户输入
            include_usage: 是否包含token使用情况
            
        Yields:
            DeepseekResponse: 包含思考过程和回答内容的响应对象
        """
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            stream_options={"include_usage": include_usage} if include_usage else None
        )

        response = DeepseekResponse()
        
        for chunk in completion:
            # 处理token使用情况
            if chunk.choices == []:
                if hasattr(chunk, 'usage'):
                    response.usage = chunk.usage.model_dump()
                yield response
                continue
                
            # 处理思考过程和回答
            if not hasattr(chunk.choices[0].delta, 'reasoning_content'):
                continue
                
            if (chunk.choices[0].delta.reasoning_content == "" and 
                chunk.choices[0].delta.content == ""):
                continue
                
            # 开始回答
            if (chunk.choices[0].delta.reasoning_content == "" and 
                not response.is_answering):
                response.is_answering = True
                
            # 更新思考内容
            if chunk.choices[0].delta.reasoning_content != "":
                response.reasoning_content += chunk.choices[0].delta.reasoning_content
                
            # 更新回答内容
            elif chunk.choices[0].delta.content != "":
                response.answer_content += chunk.choices[0].delta.content
                
            yield response

    def chat(self, prompt: str) -> DeepseekResponse:
        """
        单次对话
        
        Args:
            prompt: 用户输入
            
        Returns:
            DeepseekResponse: 包含思考过程和回答内容的响应对象
        """
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            timeout=300.0
        )
        
        result = DeepseekResponse()
        if hasattr(response.choices[0].message, 'reasoning_content'):
            result.reasoning_content = response.choices[0].message.reasoning_content
        result.answer_content = response.choices[0].message.content
        result.is_answering = True
        
        if hasattr(response, 'usage'):
            result.usage = response.usage.model_dump()
            
        return result