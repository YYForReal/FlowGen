# FlowGen Backend Service

## 项目结构
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

## 安装依赖
```bash
pip install -r requirements.txt
```

## 环境变量配置
创建 `.env` 文件并配置以下环境变量：
```
ZHIPU_API_KEY=your_api_key
BASE_URL=https://open.bigmodel.cn/api/paas/v4/
CHAT_MODEL=glm-4-flash
```

## 启动服务
```bash
uvicorn app.main:app --reload --port 8000
```

## API文档
启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 主要功能
1. 聊天接口
   - 支持多轮对话
   - 意图识别
   - 图表生成

2. 图表生成
   - 支持多种图表类型
   - 实时预览
   - 导出多种格式
