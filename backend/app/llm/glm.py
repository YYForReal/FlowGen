# glm-zero-preview
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

class GLMLLM:
    """GLM大语言模型工具类"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: str = "glm-4"
    ):
        """
        初始化GLM客户端
        
        Args:
            api_key: API密钥，默认从环境变量ZHIPUAI_API_KEY获取
            base_url: API基础URL，默认https://open.bigmodel.cn/api/paas/v4/
            model_name: 模型名称，默认为glm-4
        """
        self.api_key = api_key or os.getenv("ZHIPUAI_API_KEY")
        self.base_url = base_url or "https://open.bigmodel.cn/api/paas/v4/"
        self.model_name = model_name
        
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

# client = OpenAI(
#     api_key="your zhipuai api key",
#     base_url="https://open.bigmodel.cn/api/paas/v4/"
# ) 

# completion = client.chat.completions.create(
#     model="glm-4",  
#     messages=[    
#         {"role": "system", "content": "你是一个聪明且富有创造力的小说作家"},    
#         {"role": "user", "content": "请你作为童话故事大王，写一篇短篇童话故事，故事的主题是要永远保持一颗善良的心，要能够激发儿童的学习兴趣和想象力，同时也能够帮助儿童更好地理解和接受故事中所蕴含的道理和价值观。"} 
#     ],
#     top_p=0.7,
#     temperature=0.9
#  ) 
 
# print(completion.choices[0].message)