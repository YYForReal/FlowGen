from pydantic import BaseModel
from typing import Optional, List, Dict

class ChatMessage(BaseModel):
    """聊天消息模型"""
    content: str
    type: Optional[str] = "text"  # text, diagram_request
    metadata: Optional[Dict] = {}

class DiagramRequest(BaseModel):
    """图表请求模型"""
    type: str  # flow_chart, experiment_flow, system_arch, etc.
    prompt: str
    style: Optional[Dict] = {}
    content: Optional[str] = None  # 用于更新时传入drawio内容

class ChatResponse(BaseModel):
    """聊天响应模型"""
    message: str
    diagram: Optional[Dict] = None
    suggestions: Optional[List[str]] = None

class DiagramResponse(BaseModel):
    """图表响应模型"""
    id: str
    type: str
    content: str
    preview_url: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None 