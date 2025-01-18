# 导入必要的库
import os
from dotenv import load_dotenv,find_dotenv
from typing import List
import json
# 从 zigent 导入相关组件
# 降级 pip install setuptools==65.5.1
# pip install wikipedia -i https://pypi.tuna.tsinghua.edu.cn/simple
from zigent.agents import ABCAgent, BaseAgent
from zigent.llm.agent_llms import LLM
from zigent.commons import TaskPackage
from zigent.actions.BaseAction import BaseAction

# 从 duckduckgo_search 导入 DDGS
from duckduckgo_search import DDGS

# 加载环境变量
load_dotenv(find_dotenv())

# 从环境变量中读取 api_key
api_key = os.getenv('ZISHU_API_KEY')
base_url = "http://43.200.7.56:8008/v1"
chat_model = "glm-4-flash"

# 配置 LLM
llm = LLM(api_key=api_key, base_url=base_url, model_name=chat_model)

# 定义 DuckSearchAction 类
class DuckSearchAction(BaseAction):
    def __init__(self):
        action_name = "DuckDuckGo_Search"
        action_desc = "Using this action to search online content."
        params_doc = {"query": "the search string. be simple."}
        self.ddgs = DDGS()
        super().__init__(action_name=action_name, action_desc=action_desc, params_doc=params_doc)

    def __call__(self, query):
        results = self.ddgs.chat(query)
        return results

# 定义 DuckSearchAgent 类
class DuckSearchAgent(BaseAgent):
    def __init__(self, llm: LLM, actions: List[BaseAction] = [DuckSearchAction()], manager: ABCAgent = None, **kwargs):
        name = "duck_search_agent"
        role = "You can answer questions by using duck duck go search content."
        # 注意这里没有agent_logger
        super().__init__(name=name, role=role, llm=llm, actions=actions, manager=manager)

# 编写执行函数
def do_search_agent():
    # 创建代理实例
    search_agent = DuckSearchAgent(llm=llm)

    # 创建任务
    task = "what is the found date of microsoft"
    task_pack = TaskPackage(instruction=task)

    # 执行任务并获取响应
    response = search_agent(task_pack)
    print("response:", response)

# 可选：定义 BochaSearchAction 类
class BochaSearchAction(BaseAction):
    def __init__(self):
        action_name = "Bocha_Search"
        action_desc = "Using this action to search online content."
        params_doc = {"query": "the search string. be simple."}
        super().__init__(action_name=action_name, action_desc=action_desc, params_doc=params_doc)

    def __call__(self, query):
        BOCHA_API_KEY = os.getenv('BOCHA_API_KEY')
        results = bocha_web_search_tool(query, BOCHA_API_KEY)
        rst = json.loads(results)
        result = ""
        for item in rst["data"]["webPages"]["value"]:
            result += item["summary"]
        return result

# 可选：定义 BochaSearchAgent 类
class BochaSearchAgent(BaseAgent):
    def __init__(self, llm: LLM, actions: List[BaseAction] = [BochaSearchAction()], manager: ABCAgent = None, **kwargs):
        name = "bocha_search_agent"
        role = "You can answer questions by using bocha search content."
        super().__init__(name=name, role=role, llm=llm, actions=actions, manager=manager, logger=agent_logger)

# 主执行块
if __name__ == "__main__":
    do_search_agent()