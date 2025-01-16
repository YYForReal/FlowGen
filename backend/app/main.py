from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat, diagrams

app = FastAPI(
    title="FlowGen API",
    description="科研绘图助手API服务",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(diagrams.router, prefix="/api/v1", tags=["diagrams"])

@app.get("/")
async def root():
    return {"message": "Welcome to FlowGen API"} 