import os
import asyncio
from typing import Any

import uvicorn
from fastapi import FastAPI, Body
from fastapi.responses import StreamingResponse
from queue import Queue
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from langchain.chat_models import ChatOpenAI
from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler
from langchain.callbacks.streaming_stdout_final_only import FinalStreamingStdOutCallbackHandler
from langchain.schema import LLMResult, HumanMessage

from dotenv import load_dotenv,find_dotenv

load_dotenv(find_dotenv())

app = FastAPI()

# 添加CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# initialize the agent (we need to do this for the callbacks)
llm = ChatOpenAI(
    openai_api_key=os.getenv("ZHIPUAI_API_KEY"),
    base_url=os.getenv("ZHIPU_BASE_URL"),
    temperature=0.2,
    model_name="glm-4-flash",
    streaming=True,
    callbacks=[]
)

class AsyncCallbackHandler(AsyncIteratorCallbackHandler):
    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        self.queue.put_nowait(token)  # 直接传递token
    
    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        self.done.set()

async def run_call(query: str, stream_it: AsyncCallbackHandler):
    llm.callbacks = [stream_it]
    async for chunk in llm.astream([HumanMessage(content=query)]):
        pass  # 回调处理器会自动处理token

# request input format
class Query(BaseModel):
    text: str

async def create_gen(query: str, stream_it: AsyncCallbackHandler):
    task = asyncio.create_task(run_call(query, stream_it))
    async for token in stream_it.aiter():
        yield token
    await task

@app.post("/chat")
async def chat(
    query: Query = Body(...),
):
    stream_it = AsyncCallbackHandler()
    gen = create_gen(query.text, stream_it)
    return StreamingResponse(gen, media_type="text/event-stream")

@app.get("/health")
async def health():
    """Check the api is running"""
    return {"status": "🤙"}
    

if __name__ == "__main__":
    uvicorn.run(
        "main_example:app",
        host="localhost",
        port=8000,
        reload=True
    )