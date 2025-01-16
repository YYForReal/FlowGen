from llama_index.core.node_parser import MarkdownNodeParser
# 导入 Markdown Reader
from llama_index.readers.file import MarkdownReader
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.embeddings.jinaai import JinaEmbedding
# pip install faiss-cpu
import faiss
import os
from dotenv import load_dotenv
from llama_index.core import Settings

# 加载环境变量
load_dotenv()

# 创建 Markdown 解析器实例
parser = MarkdownNodeParser()

# 创建 Markdown Reader 实例
reader = MarkdownReader()

# 读取并解析 Markdown 文件
markdown_docs = reader.load_data(file="data/plantuml.md")
nodes = parser.get_nodes_from_documents(markdown_docs)

# 初始化嵌入模型
embedding = JinaEmbedding(api_key=os.getenv('JINAAI_API_KEY'))

# 获取嵌入维度
emb_dimension = len(embedding.get_text_embedding("test"))

# 创建 FAISS 向量存储
vector_store = FaissVectorStore(faiss_index=faiss.IndexFlatL2(emb_dimension))
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# 构建向量索引
index = VectorStoreIndex(
    nodes=nodes,
    storage_context=storage_context,
    embed_model=embedding,
)

# 构建检索器
retriever_kwargs = {
    'similarity_top_k': 3,  # 检索最相关的3个文档片段
    'index': index,
    'embed_model': embedding,
}
retriever = VectorIndexRetriever(**retriever_kwargs)

# 从环境变量获取 LLM 配置
from llm import OurLLM,OurDouBaoLLM
llm = OurLLM(
    api_key=os.getenv('ZHIPU_API_KEY'),
    base_url=os.getenv('ZHIPU_BASE_URL'),
    model_name=os.getenv('ZHIPU_CHAT_MODEL')
)
llm = OurDouBaoLLM()



# 构建响应合成器
response_synthesizer = get_response_synthesizer(
    llm=llm,
    response_mode="compact"  # 使用紧凑模式，将检索到的内容整合成简洁的回答
)

# 设置 RAG Agent 的配置
Settings.llm = llm
Settings.verbose = True
Settings.max_iterations = 5
Settings.max_execution_time = 10


# 构建问答引擎
query_engine = RetrieverQueryEngine(
    retriever=retriever,
    response_synthesizer=response_synthesizer,
)

def query_rag(question: str) -> str:
    """
    使用 RAG 系统回答问题
    
    Args:
        question: 用户的问题
        
    Returns:
        str: RAG 系统的回答
    """
    response = query_engine.query(question)
    return response.response


def query_rag_agent(question: str) -> str:
    """
    使用 RAG Agent回答问题
    
    Args:
        question: 用户的问题
        
    Returns:
        str: RAG Agent的回答
    """
    from llama_index.core.agent import ReActAgent
    from llama_index.core.tools import FunctionTool, QueryEngineTool

    retriever_tool = QueryEngineTool.from_defaults(
        query_engine,
        name="retriever_tool",
        description="查询plantuml相关信息"
    )


    # 构建 RAG Agent
    rag_agent = ReActAgent.from_tools([retriever_tool], llm=Settings.llm, verbose=Settings.verbose, max_iterations=Settings.max_iterations, max_execution_time=Settings.max_execution_time)

    # 使用 RAG Agent 回答问题
    response = rag_agent.query(question)
    return response.response

if __name__ == "__main__":
    # 测试 RAG 系统
    test_questions = [
        "什么是用例图？",
        "如何改变角色的样式？",
        "如何在用例图中添加注释？"
    ]
    
    # print("RAG 系统测试：")
    # print("-" * 50)
    # for question in test_questions:
    #     print(f"问题：{question}")
    #     print(f"回答：{query_rag(question)}")
    #     print("-" * 50)

    # 测试 RAG Agent
    print("RAG Agent 测试：")
    print("-" * 50)
    for question in test_questions:
        print(f"问题：{question}")
        print(f"回答：{query_rag_agent(question)}")
        print("-" * 50)
