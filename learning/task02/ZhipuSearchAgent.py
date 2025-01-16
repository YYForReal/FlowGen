import os
import json
import requests
from dotenv import load_dotenv
from typing import List
from zigent.agents import BaseAgent, ABCAgent
from zigent.llm.agent_llms import LLM
from zigent.commons import TaskPackage
from zigent.actions.BaseAction import BaseAction
from zhipuai import ZhipuAI
from datetime import datetime

# 加载环境变量
load_dotenv()
api_key = os.getenv('ZISHU_API_KEY')
base_url = "http://43.200.7.56:8008/v1"
chat_model = "Qwen2.5-72B"
ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY')

# 配置LLM
llm = LLM(api_key=api_key, base_url=base_url, model_name=chat_model)

# 定义Zhipu Web Search工具
def zhipu_web_search_tool(query: str) -> str:
    """
    使用智谱AI的GLM-4模型进行联网搜索，返回搜索结果的字符串。
    
    参数:
    - query: 搜索关键词

    返回:
    - 搜索结果的字符串形式
    """
    # 初始化客户端
    client = ZhipuAI(api_key=ZHIPU_API_KEY)

    # 获取当前日期
    current_date = datetime.now().strftime("%Y-%m-%d")

    print("current_date:", current_date)
    
    # 设置工具
    tools = [{
        "type": "web_search",
        "web_search": {
            "enable": True
        }
    }]

    # 系统提示模板，包含时间信息
    system_prompt = f"""你是一个具备网络访问能力的智能助手，在适当情况下，优先使用网络信息（参考信息）来回答，
    以确保用户得到最新、准确的帮助。当前日期是 {current_date}。"""
        
    # 构建消息
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query}
    ]
        
    # 调用API
    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=messages,
        tools=tools
    )
    
    # 返回结果
    return response.choices[0].message.content

class ZhipuSearchAction(BaseAction):
    def __init__(self) -> None:
        action_name = "Zhipu_Search"
        action_desc = "Using this action to search online content."
        params_doc = {"query": "the search string. be simple."}
        super().__init__(
            action_name=action_name,
            action_desc=action_desc,
            params_doc=params_doc,
        )

    def __call__(self, query):
        results = zhipu_web_search_tool(query)
        return results

class ZhipuSearchAgent(BaseAgent):
    def __init__(
        self,
        llm: LLM,
        actions: List[BaseAction] = [ZhipuSearchAction()],
        manager: ABCAgent = None,
        **kwargs
    ):
        name = "zhiu_search_agent"
        role = "You can answer questions by using Zhipu search content."
        super().__init__(
            name=name,
            role=role,
            llm=llm,
            actions=actions,
            manager=manager,
        )

def do_search_agent():
    # 创建代理实例
    search_agent = ZhipuSearchAgent(llm=llm)

    # 创建任务
    task = "2025年支付宝P0事故"
    task_pack = TaskPackage(instruction=task)

    # 执行任务并获取响应
    response = search_agent(task_pack)
    print(response)

if __name__ == "__main__":
    do_search_agent()