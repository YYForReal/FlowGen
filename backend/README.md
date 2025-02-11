# FlowGen Backend Service

## 项目架构
```
backend/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── chat.py        # 聊天相关接口
│   │   └── diagrams.py    # 图表相关接口
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py      # 配置管理
│   │   └── security.py    # 安全相关
│   ├── models/
│   │   ├── __init__.py
│   │   └── chat.py        # 数据模型
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py  # AI服务
│   │   └── draw_service.py # 绘图服务
│   └── main.py
├── tests/
├── .env
├── requirements.txt
└── README.md
```

## 主要功能
1. 聊天接口
   - 支持WebSocket长连接
   - 集成大语言模型
   - 支持多轮对话
   - 意图识别

2. 图表生成
   - 支持PlantUML和Draw.io格式
   - 实时预览
   - 导出多种格式

## 技术栈
- FastAPI: Web框架
- LlamaIndex: LLM应用框架
- SQLite: 轻量级数据库
- WebSocket: 实时通信
- Python 3.11+

## 依赖安装
```bash
pip install -r requirements.txt
```

## 环境变量配置
创建 `.env` 文件并配置以下环境变量：
```
# LLM配置
ZHIPU_API_KEY=your_api_key
ZHIPU_BASE_URL=https://open.bigmodel.cn/api/paas/v4/
ZHIPU_CHAT_MODEL=glm-4-flash

# 可选：豆包API配置
DOUBAO_API_KEY=your_api_key
DOUBAO_API_BASE_URL=your_base_url
DOUBAO_MODEL=your_model

# 向量嵌入模型配置
JINAAI_API_KEY=your_jina_api_key

# 应用配置
APP_ENV=development
DEBUG=True
```

## 启动服务
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API文档
启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 绘图相关依赖
1. PlantUML

> 暂无python端相关的渲染第三方库，所以可以暂时以生成plantuml文件代码为目标。

2. Draw.io

> 暂无python端相关的渲染第三方库，所以可以暂时以生成drawio文件代码为目标。

## LLM集成
1. 基础依赖：
```bash
pip install llama-index-core
pip install llama-index-llms-openai
pip install llama-index-embeddings-huggingface
```

2. 向量存储：
```bash
pip install faiss-cpu  # CPU版本
# 或
pip install faiss-gpu  # GPU版本，需要CUDA支持
```

3. LLM工具集成：
```python
from llama_index.core import Settings
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool
```

## 开发规范
1. 代码风格
   - 遵循PEP 8规范
   - 使用mypy进行类型检查
   - 使用ruff进行代码检查

2. 文档规范
   - 所有函数必须包含docstring
   - API接口必须包含OpenAPI文档

3. 测试规范
   - 单元测试覆盖率要求>80%
   - 使用pytest进行测试