import sqlite3
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv,find_dotenv

load_dotenv(find_dotenv())
# from llama_index.llms.ollama import Ollama
# from llama_index.embeddings.ollama import OllamaEmbedding

# !pip install llama-index-embeddings-jinaai
# 可以来这里领一个免费的api key：https://jina.ai/embeddings/
from llama_index.embeddings.jinaai import JinaEmbedding
# embedding = JinaEmbedding(api_key=os.getenv('JINAAI_API_KEY'))



from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool, QueryEngineTool
from llama_index.core import SQLDatabase
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.core import Settings
import matplotlib.pyplot as plt
# 在绘图前设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 显示中文
plt.rcParams['axes.unicode_minus'] = False     # 正常显示负号

# =======================
# 1. 创建数据库及填充数据
# =======================
sqllite_path = 'llmdb.db'
con = sqlite3.connect(sqllite_path)

# 创建表
sql = """
CREATE TABLE IF NOT EXISTS `section_stats` (
  `部门` varchar(100) DEFAULT NULL,
  `人数` int(11) DEFAULT NULL,
  `location` varchar(100) DEFAULT NULL,
  `budget` float DEFAULT NULL,
  `projects` int(11) DEFAULT NULL
);
"""
con.execute(sql)

# 填充数据
data = [
    ["专利部", 22, "深圳", 500000.0, 3],
    ["商标部", 25, "北京", 700000.0, 5]
]
for item in data:
    sql = """
    INSERT INTO section_stats (部门, 人数, location, budget, projects) 
    VALUES ('%s', '%d', '%s', '%f', '%d')
    """ % (item[0], item[1], item[2], item[3], item[4])
    con.execute(sql)
con.commit()
con.close()

# =======================
# 2. 配置对话模型和嵌入模型
# =======================

api_key = os.getenv('ZHIPU_API_KEY')
base_url = "https://open.bigmodel.cn/api/paas/v4/"
chat_model = "glm-4-flash"

# llm = Ollama(base_url="http://192.168.0.123:11434", model="qwen2:7b")
# 改成自定义的大模型
from llm import OurLLM,OurDouBaoLLM
# llm = OurLLM(api_key=api_key, base_url=base_url, model_name=chat_model)
llm = OurDouBaoLLM()
# print("llm",llm)


# embedding = OllamaEmbedding(base_url="http://192.168.0.123:11434", model_name="qwen2:7b")
embedding = JinaEmbedding(api_key=os.getenv('JINAAI_API_KEY'))

# 测试对话模型
response = llm.complete("你是谁？")
print("对话模型测试：", response)

# 测试嵌入模型
emb = embedding.get_text_embedding("你好呀呀")
print("嵌入模型测试：", len(emb), type(emb))

Settings.llm = llm
Settings.embed_model = embedding

# =======================
# 3. 创建数据库查询引擎
# =======================
engine = create_engine("sqlite:///llmdb.db")
sql_database = SQLDatabase(engine, include_tables=["section_stats"])
query_engine = NLSQLTableQueryEngine(
    sql_database=sql_database,
    tables=["section_stats"],
    llm=Settings.llm
)

# =======================
# 4. 定义工具函数
# =======================
def multiply(a: float, b: float) -> float:
    """将两个数字相乘并返回乘积。"""
    return a * b

def add(a: float, b: float) -> float:
    """将两个数字相加并返回它们的和。"""
    return a + b

def calculate_average(values: list) -> float:
    """计算给定数值的平均值。"""
    return sum(values) / len(values)

def get_highest(data: list, field: str) -> dict:
    """获取数据中某字段的最高值记录。"""
    return max(data, key=lambda x: x[field])

def compare(value1: float, value2: float) -> str:
    """比较两个值并返回结果。"""
    if value1 > value2:
        return "第一个值更大"
    elif value1 < value2:
        return "第二个值更大"
    else:
        return "两个值相等"

# 转换为工具函数
multiply_tool = FunctionTool.from_defaults(fn=multiply)
add_tool = FunctionTool.from_defaults(fn=add)
average_tool = FunctionTool.from_defaults(fn=calculate_average)
compare_tool = FunctionTool.from_defaults(fn=compare)

# 把数据库查询引擎封装到工具函数对象中
staff_tool = QueryEngineTool.from_defaults(
    query_engine,
    name="section_staff",
    description="查询部门的详细信息。字段为'部门'、'人数'、'location'、'budget'、'projects'"
)

# =======================
# 5. 构建ReActAgent
# =======================
agent = ReActAgent.from_tools(
    [multiply_tool, add_tool, average_tool, compare_tool, staff_tool],
    verbose=True
)

# =======================
# 6. 测试Agent
# =======================
response = agent.chat("请找出预算最高的部门，并告诉我它的名字和人数！")
print("Agent对话结果：", response)

# =======================
# 7. 可视化结果
# =======================
con = sqlite3.connect(sqllite_path)
cursor = con.cursor()
cursor.execute("SELECT 部门, 人数 FROM section_stats")
rows = cursor.fetchall()
con.close()

departments = [row[0] for row in rows]
staff_counts = [row[1] for row in rows]

plt.bar(departments, staff_counts, color=['blue', 'orange'])
plt.xlabel('部门')
plt.ylabel('人数')
plt.title('部门人数分布')
plt.show()
