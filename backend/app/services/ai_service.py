from typing import Any, Dict, Generator, List, Optional
from pydantic import Field
from llama_index.core.llms import (
    CustomLLM,
    CompletionResponse,
    LLMMetadata,
)
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool, QueryEngineTool
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.readers.file import MarkdownReader
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.embeddings.jinaai import JinaEmbedding
from openai import OpenAI
import faiss
import os
from dotenv import load_dotenv
from typing import AsyncGenerator
from openai import AsyncOpenAI
import json

# 加载环境变量
load_dotenv()

class OurLLM(CustomLLM):
    """自定义LLM封装类，支持智谱AI"""
    
    api_key: str = Field(default=os.getenv('ZHIPU_API_KEY') or '')
    base_url: str = Field(default=os.getenv('ZHIPU_BASE_URL') or '')
    model_name: str = Field(default=os.getenv('ZHIPU_CHAT_MODEL') or '')
    client: OpenAI = Field(default=None, exclude=True)

    def __init__(self, api_key: str = os.getenv('ZHIPU_API_KEY') or '',
                 base_url: str = os.getenv('ZHIPU_BASE_URL') or '',
                 model_name: str = os.getenv('ZHIPU_CHAT_MODEL') or '',
                 **data: Any):
        super().__init__(**data)
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    @property
    def metadata(self) -> LLMMetadata:
        """获取LLM元数据"""
        return LLMMetadata(model_name=self.model_name)

    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        """完成单次对话"""
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )
        if hasattr(response, 'choices') and len(response.choices) > 0:
            response_text = response.choices[0].message.content
            return CompletionResponse(text=response_text)
        else:
            raise Exception(f"Unexpected response format: {response}")

    def stream_complete(
        self, prompt: str, **kwargs: Any
    ) -> Generator[CompletionResponse, None, None]:
        """流式完成对话"""
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


class OurDouBaoLLM(CustomLLM):
    """自定义LLM封装类，支持豆包API"""
    
    api_key: str = Field(default=os.getenv('DOUBAO_API_KEY') or '')
    base_url: str = Field(default=os.getenv('DOUBAO_API_BASE_URL') or '')
    model_name: str = Field(default=os.getenv('DOUBAO_MODEL') or '')
    client: OpenAI = Field(default=None, exclude=True)

    def __init__(self, api_key: str = os.getenv('DOUBAO_API_KEY') or '',
                 base_url: str = os.getenv('DOUBAO_API_BASE_URL') or '',
                 model_name: str = os.getenv('DOUBAO_MODEL') or '',
                 **data: Any):
        super().__init__(**data)
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    @property
    def metadata(self) -> LLMMetadata:
        """获取LLM元数据"""
        return LLMMetadata(model_name=self.model_name)

    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        """完成单次对话"""
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )
        if hasattr(response, 'choices') and len(response.choices) > 0:
            response_text = response.choices[0].message.content
            return CompletionResponse(text=response_text)
        else:
            raise Exception(f"Unexpected response format: {response}")

    def stream_complete(
        self, prompt: str, **kwargs: Any
    ) -> Generator[CompletionResponse, None, None]:
        """流式完成对话"""
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


class RAGService:
    """RAG服务类，处理知识库检索和问答"""

    def __init__(self, markdown_files: List[str], llm: Optional[CustomLLM] = None):
        """
        初始化RAG服务
        
        Args:
            markdown_files: Markdown文件路径列表
            llm: 可选的LLM实例，如果不提供则使用默认的OurLLM
        """
        self.llm = llm or OurLLM()
        self.query_engine = self._setup_rag_system(markdown_files)
        self.rag_agent = self._setup_rag_agent()

    def _setup_rag_system(self, markdown_files: List[str]) -> RetrieverQueryEngine:
        """设置RAG系统"""
        # 初始化解析器和Reader
        parser = MarkdownNodeParser()
        reader = MarkdownReader()
        
        # 读取并解析所有Markdown文件
        all_docs = []
        for file_path in markdown_files:
            docs = reader.load_data(file=file_path)
            all_docs.extend(docs)
        
        nodes = parser.get_nodes_from_documents(all_docs)
        
        # 初始化嵌入模型
        embedding = JinaEmbedding(api_key=os.getenv('JINAAI_API_KEY'),dimensions=1024)
        emb_dimension = len(embedding.get_text_embedding("test"))
        
        # 创建向量存储和索引
        vector_store = FaissVectorStore(faiss_index=faiss.IndexFlatL2(emb_dimension))
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        index = VectorStoreIndex(
            nodes=nodes,
            storage_context=storage_context,
            embed_model=embedding,
        )
        
        # 构建检索器
        retriever = VectorIndexRetriever(
            index=index,
            similarity_top_k=3,
            embed_model=embedding,
        )
        
        # 构建响应合成器
        response_synthesizer = get_response_synthesizer(
            llm=self.llm,
            response_mode="compact"
        )
        
        return RetrieverQueryEngine(
            retriever=retriever,
            response_synthesizer=response_synthesizer,
        )

    def _setup_rag_agent(self) -> ReActAgent:
        """设置RAG Agent"""
        retriever_tool = QueryEngineTool.from_defaults(
            self.query_engine,
            name="knowledge_base",
            description="查询知识库中的信息"
        )
        
        return ReActAgent.from_tools(
            [retriever_tool],
            llm=self.llm,
            verbose=True,
            max_iterations=5,
            max_execution_time=10
        )

    async def query(self, question: str, use_agent: bool = True) -> str:
        """
        查询知识库
        
        Args:
            question: 用户问题
            use_agent: 是否使用RAG Agent
            
        Returns:
            str: 回答内容
        """
        try:
            if use_agent:
                response = self.rag_agent.query(question)
            else:
                response = self.query_engine.query(question)
            return str(response.response)
        except Exception as e:
            raise Exception(f"查询失败: {str(e)}")


class AIService:
    """AI服务类，处理对话和工具调用"""
    
    def __init__(self,using_rag = False):
        # 使用AsyncOpenAI客户端
        self.async_client = AsyncOpenAI(
            api_key=os.getenv('ZHIPU_API_KEY'),
            base_url=os.getenv('ZHIPU_BASE_URL')
        )
        self.llm = OurLLM()
        if using_rag:
            print("Using RAG Service...")
            # 初始化RAG服务，指定知识库文件
            self.rag_service = RAGService(
                markdown_files=[
                    "docs/knowledge_base/plantuml.md",
                    "docs/knowledge_base/drawio.md",
                    # 添加更多知识库文件
                ],
                llm=self.llm
            )
        self.agent = self._create_agent()

    def _create_agent(self) -> ReActAgent:
        """创建ReAct Agent"""
        tools = self._get_tools()
        return ReActAgent.from_tools(tools, llm=self.llm, verbose=True)

    def _get_tools(self) -> List[FunctionTool]:
        """获取工具列表"""
        tools = []
        
        # 添加RAG查询工具
        async def query_knowledge_base(question: str) -> str:
            """查询知识库"""
            return await self.rag_service.query(question)
        
        tools.append(FunctionTool.from_defaults(
            fn=query_knowledge_base,
            name="query_knowledge_base",
            description="查询知识库获取信息"
        ))
        
        # 添加其他工具...
        
        return tools

    async def process_message(self, message: str) -> Dict[str, Any]:
        """处理用户消息"""
        try:
            # 使用Agent处理消息
            response = self.agent.chat(message)
            return {
                "status": "success",
                "message": str(response),
                "type": "text"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "type": "error"
            }

    async def stream_message(self, message: str) -> AsyncGenerator[Dict[str, Any], None]:
        """流式处理用户消息"""
        try:
            response = self.llm.stream_complete(message)
            for chunk in response:
                yield {
                    "status": "success",
                    "message": chunk.text,
                    "type": "text",
                    "is_chunk": True
                }
        except Exception as e:
            yield {
                "status": "error",
                "message": str(e),
                "type": "error"
            }

    async def stream_generate(self, query: str) -> AsyncGenerator[str, None]:
        """修复后的异步流式生成方法"""
        try:
            # 使用异步create方法
            response = await self.async_client.chat.completions.create(
                model=os.getenv('ZHIPU_CHAT_MODEL'),
                messages=[{"role": "user", "content": query}],
                stream=True
            )
            
            # 使用异步迭代器
            async for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    yield f"data: {json.dumps({'content': content})}\n\n"
                    
        except Exception as e:
            error_msg = f"data: {json.dumps({'error': str(e)})}\n\n"
            yield error_msg