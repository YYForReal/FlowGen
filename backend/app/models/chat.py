from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ChatMessage(BaseModel):
    """聊天消息模型"""
    content: str = Field(..., description="消息内容")
    type: str = Field(default="text", description="消息类型，如text、image等")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="额外的元数据")

class DiagramRequest(BaseModel):
    """图表请求模型"""
    type: str = Field(..., description="图表类型，如plantuml、drawio等")
    content: Optional[str] = Field(default=None, description="图表内容，如果是修改现有图表")
    style: Optional[Dict[str, Any]] = Field(default=None, description="样式配置")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="额外的元数据")

class ChatResponse(BaseModel):
    """聊天响应模型"""
    message: str
    diagram: Optional[Dict] = None
    suggestions: Optional[List[str]] = None

class DiagramResponse(BaseModel):
    """图表响应模型"""
    id: str = Field(..., description="图表ID")
    type: str = Field(..., description="图表类型")
    content: str = Field(..., description="图表内容")
    preview_url: Optional[str] = Field(default=None, description="预览图片URL")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="额外的元数据") 