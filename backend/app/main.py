from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# 导入路由
from app.router import chat, diagrams, deepseek

# 加载环境变量
load_dotenv()

# 创建FastAPI应用
app = FastAPI(
    title="FlowGen API",
    description="FlowGen - 科研绘图助手API文档",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI 地址
    redoc_url="/redoc",  # ReDoc 地址
    openapi_url="/openapi.json"  # OpenAPI 文档地址
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat.router, tags=["聊天"])
app.include_router(diagrams.router, tags=["图表"])
app.include_router(deepseek.router, tags=["Deepseek"])

@app.get("/")
async def root():
    """
    根路由，返回API基本信息
    """
    return {
        "name": "FlowGen API",
        "version": "1.0.0",
        "status": "running"
    } 