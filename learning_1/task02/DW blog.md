
# 第04课-用Llama-index创建Agent

首先定义工具函数，用来完成Agent的任务。注意：大模型会根据函数的注释来判断使用哪个函数来完成任务。所以，注释一定要写清楚函数的功能和返回值。

然后把工具函数放入FunctionTool对象中，供Agent能够使用。

用 LlamaIndex 实现一个简单的 agent demo 比较容易，LlamaIndex 实现 Agent 需要导入 ReActAgent 和 Function Tool。

ReActAgent 是什么？

ReActAgent 通过结合推理（Reasoning）和行动（Acting）来创建动态的 LLM Agent 的框架。该方法允许 LLM 模型通过在复杂环境中交替进行推理步骤和行动步骤来更有效地执行任务。ReActAgent 将推理和动作形成了闭环，Agent 可以自己完成给定的任务。

一个典型的 ReActAgent 遵循以下循环：

初始推理：代理首先进行推理步骤，以理解任务、收集相关信息并决定下一步行为。 行动：代理基于其推理采取行动——例如查询API、检索数据或执行命令。 观察：代理观察行动的结果并收集任何新的信息。 优化推理：利用新信息，代理再次进行推理，更新其理解、计划或假设。 重复：代理重复该循环，在推理和行动之间交替，直到达到满意的结论或完成任务。

实现最简单的代码，通过外部工具做算术题，只是一个简单的例子。这个如果不用 Agent，其实大模型也可以回答。看一下具体的代码实现：

首先准备各种key和模型名称
```python
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
# 从环境变量中读取api_key
api_key = os.getenv('ZISHU_API_KEY')
base_url = "http://43.200.7.56:8008/v1"
chat_model = "glm-4-flash"
emb_model = "embedding-3"
然后来构建llm，其实任何能用的llm都行。这里自定义一个。

from openai import OpenAI
from pydantic import Field  # 导入Field，用于Pydantic模型中定义字段的元数据
from llama_index.core.llms import (
    CustomLLM,
    CompletionResponse,
    LLMMetadata,
)
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.llms.callbacks import llm_completion_callback
from typing import List, Any, Generator
# 定义OurLLM类，继承自CustomLLM基类
class OurLLM(CustomLLM):
    api_key: str = Field(default=api_key)
    base_url: str = Field(default=base_url)
    model_name: str = Field(default=chat_model)
    client: OpenAI = Field(default=None, exclude=True)  # 显式声明 client 字段

    def __init__(self, api_key: str, base_url: str, model_name: str = chat_model, **data: Any):
        super().__init__(**data)
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)  # 使用传入的api_key和base_url初始化 client 实例

    @property
    def metadata(self) -> LLMMetadata:
        """Get LLM metadata."""
        return LLMMetadata(
            model_name=self.model_name,
        )

    @llm_completion_callback()
    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        response = self.client.chat.completions.create(model=self.model_name, messages=[{"role": "user", "content": prompt}])
        if hasattr(response, 'choices') and len(response.choices) > 0:
            response_text = response.choices[0].message.content
            return CompletionResponse(text=response_text)
        else:
            raise Exception(f"Unexpected response format: {response}")

    @llm_completion_callback()
    def stream_complete(
        self, prompt: str, **kwargs: Any
    ) -> Generator[CompletionResponse, None, None]:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )

        try:
            for chunk in response:
                chunk_message = chunk.choices[0].delta
                if not chunk_message.content:
                    continue
                content = chunk_message.content
                yield CompletionResponse(text=content, delta=content)

        except Exception as e:
            raise Exception(f"Unexpected response format: {e}")

llm = OurLLM(api_key=api_key, base_url=base_url, model_name=chat_model)
```

测试一下这个llm能用吗？

```python
response = llm.stream_complete("你是谁？")
for chunk in response:
    print(chunk, end="", flush=True)
我是一个人工智能助手，名叫 ChatGLM，是基于清华大学 KEG 实验室和智谱 AI 公司于 2024 年共同训练的语言模型开发的。我的任务是针对用户的问题和要求提供适当的答复和支持。

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool


def multiply(a: float, b: float) -> float:
    """Multiply two numbers and returns the product"""
    return a * b


def add(a: float, b: float) -> float:
    """Add two numbers and returns the sum"""
    return a + b


def main():

    multiply_tool = FunctionTool.from_defaults(fn=multiply)
    add_tool = FunctionTool.from_defaults(fn=add)

    # 创建ReActAgent实例
    agent = ReActAgent.from_tools([multiply_tool, add_tool], llm=llm, verbose=True)

    response = agent.chat("20+（2*4）等于多少？使用工具计算每一步")

    print(response)


if __name__ == "__main__":
    main()
```

可以看出，它将提问中的计算步骤分别利用了我们自定义的函数 add 和 multiply ，而不是走大模型。挺有意思的吧，我们可以自定义 agent 中的某些处理流程。除了使用 prompt 外，我们的控制权更大了。

当我们问大模型一个天气的问题，当没有工具时，大模型这么回答，作为大语言模型，他不知道天气情况并给出去哪里可以查到天气情况。 现在为我们的 Agent 添加一个查询天气的方法，返回假数据做测试

```python
def get_weather(city: str) -> int:
    """
    Gets the weather temperature of a specified city.

    Args:
    city (str): The name or abbreviation of the city.

    Returns:
    int: The temperature of the city. Returns 20 for 'NY' (New York),
         30 for 'BJ' (Beijing), and -1 for unknown cities.
    """

    # Convert the input city to uppercase to handle case-insensitive comparisons
    city = city.upper()

    # Check if the city is New York ('NY')
    if city == "NY":
        return 20  # Return 20°C for New York

    # Check if the city is Beijing ('BJ')
    elif city == "BJ":
        return 30  # Return 30°C for Beijing

    # If the city is neither 'NY' nor 'BJ', return -1 to indicate unknown city
    else:
        return -1

weather_tool = FunctionTool.from_defaults(fn=get_weather)

agent = ReActAgent.from_tools([multiply_tool, add_tool, weather_tool], llm=llm, verbose=True)

response = agent.chat("纽约天气怎么样?")
```
可以看到模型的推理能力很强，将纽约转成了 NY。可以在 arize_phoenix 中看到 agent 的具体提示词，工具被装换成了提示词。 ReActAgent 使得业务自动向代码转换成为可能，只要有 API 模型就可以调用，很多业务场景都适用，LlamaIndex 提供了一些开源的工具实现，可以到官网查看。

虽然 Agent 可以实现业务功能， 但是一个 Agent 不能完成所有的功能，这也符合软件解耦的设计原则，不同的 Agent 可以完成不同的任务，各司其职，Agent 之间可以进行交互、通信，类似于微服务。



# 第05课-数据库对话Agent

首先我们创建一个数据库：

```python
import sqlite3
# 创建数据库
sqllite_path = 'llmdb.db'
con = sqlite3.connect(sqllite_path)

# 创建表
sql = """
CREATE TABLE `section_stats` (
  `部门` varchar(100) DEFAULT NULL,
  `人数` int(11) DEFAULT NULL
);
"""
c = con.cursor()
cursor = c.execute(sql)
c.close()
con.close()
```

然后给数据库填充一些数据：

```python
con = sqlite3.connect(sqllite_path)
c = con.cursor()
data = [
    ["专利部",22],
    ["商标部",25],
]
for item in data:
    sql = """
    INSERT INTO section_stats (部门,人数) 
    values('%s','%d')
    """%(item[0],item[1])
    c.execute(sql)
    con.commit()
c.close()
con.close()
```

然后配置对话模型。可以直接用第03课用OurLLM创建的llm，这里采用了本地模型。

```python
from llama_index.llms.ollama import Ollama
llm = Ollama(base_url="http://192.168.0.123:11434", model="qwen2:7b")
```

导入Llama-index相关的库，并配置对话模型和嵌入模型。

```python
from llama_index.core.agent import ReActAgent  
from llama_index.core.tools import FunctionTool  
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings  
from llama_index.core.tools import QueryEngineTool   
from llama_index.core import SQLDatabase  
from llama_index.core.query_engine import NLSQLTableQueryEngine  
from sqlalchemy import create_engine, select  


# 配置本地大模型  
Settings.llm = llm
## 创建数据库查询引擎  
engine = create_engine("sqlite:///llmdb.db")  
# prepare data  
sql_database = SQLDatabase(engine, include_tables=["section_stats"])  
query_engine = NLSQLTableQueryEngine(  
    sql_database=sql_database,   
    tables=["section_stats"],   
    llm=Settings.llm  
)
# 创建工具函数  
def multiply(a: float, b: float) -> float:  
    """将两个数字相乘并返回乘积。"""  
    return a * b  

multiply_tool = FunctionTool.from_defaults(fn=multiply)  

def add(a: float, b: float) -> float:  
    """将两个数字相加并返回它们的和。"""  
    return a + b

add_tool = FunctionTool.from_defaults(fn=add)

# 把数据库查询引擎封装到工具函数对象中  
staff_tool = QueryEngineTool.from_defaults(
    query_engine,
    name="section_staff",
    description="查询部门的人数。"  
)
# 构建ReActAgent
agent = ReActAgent.from_tools([multiply_tool, add_tool, staff_tool], verbose=True)  
# 通过agent给出指令
response = agent.chat("请从数据库表中获取`专利部`和`商标部`的人数，并将这两个部门的人数相加！")  
```

Thought: 首先我需要使用section_staff工具来获取“专利部”和“商标部”的人数。 Action: section_staff Action Input: {'input': '专利部'} Observation: 根据查询结果，部门为“专利部”的统计数据共有22条。 Thought: 我还需要获取“商标部”的人数，我将再次使用section_staff工具。 Action: section_staff Action Input: {'input': '商标部'} Observation: 根据查询结果，部门为"商标部"的统计数据共有25条。 Thought: 我现在有了两个部门的人数：“专利部”有22人，“商标部”有25人。下一步我需要将这两个数字相加。 Action: add Action Input: {'a': 22, 'b': 25} Observation: 47 Thought: 我可以回答这个问题了，两个部门的人数之和是47人。 Answer: 专利部和商标部的总人数为47人。
最后response：专利部和商标部的总人数为47人。

注：目前这个功能不太稳定，上面这个结果看起来不错，但是是运行了好几次才得到这个结果的。或许是因为本地模型不够强大。换个更强的模型会更好。


# 第06课-RAG接入Agent

我们可以把RAG当作Agent可以调用的一个工具。

先配置对话模型和嵌入模型。模型的构建可以参考wow-rag课程的第二课（https://github.com/datawhalechina/wow-rag/tree/main/tutorials），里面介绍了非常多配置对话模型和嵌入模型的方式。这里采用了本地Ollama的对话模型和嵌入模型。各种配置方式都可以，只要能有个能用的llm和embedding就行。

如果运行还算顺利，可以顺便给wow-rag和wow-agent项目都点个小星星吗？谢谢！！！

```python
# 配置chat模型
from llama_index.llms.ollama import Ollama
llm = Ollama(base_url="http://192.168.0.123:11434", model="qwen2:7b")

# 配置Embedding模型
from llama_index.embeddings.ollama import OllamaEmbedding
embedding = OllamaEmbedding(base_url="http://192.168.0.123:11434", model_name="qwen2:7b")
上边这个llm和embedding有很多方法可以构建。详情参见wow-rag的第二课。

# 测试对话模型
response = llm.complete("你是谁？")
print(response)
```
我是一个人工智能助手，专门设计来帮助用户解答问题、提供信息以及执行各种任务。我的目标是成为您生活中的助手，帮助您更高效地获取所需信息。有什么我可以帮您的吗？

```python
# 测试嵌入模型
emb = embedding.get_text_embedding("你好呀呀")
len(emb), type(emb)
输出 (1024, list)
```

说明配置成功。

然后构建索引

```python
# 从指定文件读取，输入为List
from llama_index.core import SimpleDirectoryReader,Document
documents = SimpleDirectoryReader(input_files=['../docs/问答手册.txt']).load_data()

# 构建节点
from llama_index.core.node_parser import SentenceSplitter
transformations = [SentenceSplitter(chunk_size = 512)]

from llama_index.core.ingestion.pipeline import run_transformations
nodes = run_transformations(documents, transformations=transformations)

# 构建索引
from llama_index.vector_stores.faiss import FaissVectorStore
import faiss
from llama_index.core import StorageContext, VectorStoreIndex

emb = embedding.get_text_embedding("你好呀呀")
vector_store = FaissVectorStore(faiss_index=faiss.IndexFlatL2(len(emb)))
storage_context = StorageContext.from_defaults(vector_store=vector_store)

index = VectorStoreIndex(
    nodes = nodes,
    storage_context=storage_context,
    embed_model = embedding,
)
```python

然后构建问答引擎

```python
# 构建检索器
from llama_index.core.retrievers import VectorIndexRetriever
# 想要自定义参数，可以构造参数字典
kwargs = {'similarity_top_k': 5, 'index': index, 'dimensions': len(emb)} # 必要参数
retriever = VectorIndexRetriever(**kwargs)

# 构建合成器
from llama_index.core.response_synthesizers  import get_response_synthesizer
response_synthesizer = get_response_synthesizer(llm=llm, streaming=True)

# 构建问答引擎
from llama_index.core.query_engine import RetrieverQueryEngine
engine = RetrieverQueryEngine(
      retriever=retriever,
      response_synthesizer=response_synthesizer,
        )
```

用RAG回答一下试试效果：

```python
# 提问
question = "What are the applications of Agent AI systems ?"
response = engine.query(question)
for text in response.response_gen:
    print(text, end="")
```

这会输出

```bash
Agent AI systems have a variety of applications, which include:

Interactive AI: Enhancing user interactions and providing personalized experiences.
Content Generation: Assisting in the creation of content for bots and AI agents, which can be used in various applications such as customer service or storytelling.
Productivity: Improving productivity in applications by enabling tasks like replaying events, paraphrasing information, predicting actions, and synthesizing scenarios (both 3D and 2D).
Healthcare: Ethical deployment in sensitive domains like healthcare, which could potentially improve diagnoses and patient care while also addressing health disparities.
Gaming Industry: Transforming the role of developers by shifting focus from scripting non-player characters to refining agent learning processes.
Robotics and Manufacturing: Redefining manufacturing roles and requiring new skill sets, rather than replacing human workers, as adaptive robotic systems are developed.
Simulation: Learning collaboration policies within simulated environments, which can be applied to the real world with careful consideration and safety measures.
```

我们可以把这个RAG当作一个工具给Agent调用，让它去思考。 先来配置问答工具
```python
# 配置查询工具
from llama_index.core.tools import QueryEngineTool
from llama_index.core.tools import ToolMetadata
query_engine_tools = [
    QueryEngineTool(
        query_engine=engine,
        metadata=ToolMetadata(
            name="RAG工具",
            description=(
                "用于在原文中检索相关信息"
            ),
        ),
    ),
]
```

创建ReAct Agent

```python
# 创建ReAct Agent
from llama_index.core.agent import ReActAgent
agent = ReActAgent.from_tools(query_engine_tools, llm=llm, verbose=True)
```

调用Agent

```python
# 让Agent完成任务
# response = agent.chat("请问商标注册需要提供哪些文件？")
response = agent.chat("What are the applications of Agent AI systems ?")
print(response)
```

输出

```bash
Thought: 我需要使用工具来获取关于商标注册所需文件的信息。 Action: RAG Action Input: {'input': '商标注册需要提供哪些文件'} Observation: 商标注册通常需要以下文件：

企业：申请人为企业的，则需提供：

营业执照复印件
授权委托书（如果由代理人提交）
商标图案电子档
具体商品或服务的名称
国内自然人：以个人名义申请时，需要提供：

个体工商户档案（如有营业执照）
自然人身份证复印件
授权委托书（如果由代理人提交）
商标图案电子档
具体商品或服务的名称
国外自然人：申请商标时，通常需要：

护照复印件（作为身份证明文件）
授权委托书（如果由代理人提交）
商标图案电子档
具体商品或服务的名称
请注意，具体要求可能会因国家和地区政策的不同而有所变化。在实际申请前，请咨询当地的知识产权局或专业代理机构以获取最准确的信息。 Thought: 我可以使用这些信息来回答问题。 Answer: 商标注册通常需要以下文件：

企业：营业执照复印件、授权委托书（如果由代理人提交）、商标图案电子档以及具体商品或服务的名称。
国内自然人：个体工商户档案（如有）、自然人身份证复印件、授权委托书（如果由代理人提交）、商标图案电子档和具体商品或服务的名称。
国外自然人：护照复印件作为身份证明文件、授权委托书（如果由代理人提交）、商标图案电子档以及具体商品或服务的名称。
请注意，具体的申请要求可能会因国家和地区政策的不同而有所变化。在实际申请前，请咨询当地的知识产权局或专业代理机构以获取最准确的信息。 商标注册通常需要以下文件：

企业：营业执照复印件、授权委托书（如果由代理人提交）、商标图案电子档以及具体商品或服务的名称。
国内自然人：个体工商户档案（如有）、自然人身份证复印件、授权委托书（如果由代理人提交）、商标图案电子档和具体商品或服务的名称。
国外自然人：护照复印件作为身份证明文件、授权委托书（如果由代理人提交）、商标图案电子档以及具体商品或服务的名称。
请注意，具体的申请要求可能会因国家和地区政策的不同而有所变化。在实际申请前，请咨询当地的知识产权局或专业代理机构以获取最准确的信息。
```
看起来这个回答比单纯使用RAG的效果好很多。

