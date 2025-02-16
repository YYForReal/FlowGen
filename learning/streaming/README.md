学习如何进行流式输出，搭配fastapi使用

原始来源：
https://github.com/pinecone-io/examples/blob/master/learn/generation/langchain/handbook/09-langchain-streaming/main.py

优化：
1. CORS跨域
2. 修改流式过滤逻辑
3. 去除agent的封装
4. 添加前端页面

# FastAPI 流式输出集成指南

## 概述
本实现演示如何将ChatOpenAI的流式输出与FastAPI集成，实现实时逐token响应的API接口。基于LangChain的异步回调机制，通过中间件处理模型输出，最终使用FastAPI的StreamingResponse实现数据流式传输。

## 实现原理

### 核心组件
1. **异步回调处理器 (AsyncCallbackHandler)**
   - 继承自`AsyncIteratorCallbackHandler`
   - 通过重写`on_llm_new_token`捕获每个token
   - 使用队列管理输出流
   - 自动识别最终答案阶段，过滤中间思考过程

2. **FastAPI中间件**
   - `/chat`端点接收用户输入
   - 创建异步生成器`create_gen`
   - 使用`StreamingResponse`包装响应流

3. **流式响应流程**
   ```mermaid
   sequenceDiagram
       Client->>API: 发送聊天请求
       API->>CallbackHandler: 初始化流处理器
       API->>LangChain: 启动异步任务
       LangChain->>CallbackHandler: 推送token
       CallbackHandler->>Client: 流式返回token
   ```

## 快速开始

1. 环境配置
```bash
# 设置OpenAI API密钥
export OPENAI_API_KEY="your-api-key"

# 安装依赖
pip install fastapi uvicorn langchain openai
```

2. 启动服务
```bash
uvicorn main_example:app --reload
```

## 接口说明

### 聊天接口
**Endpoint**
```
POST /chat
```

**请求示例**
```json
{
    "text": "请解释量子计算的基本原理"
}
```

**响应特征**
- Media Type: `text/event-stream`
- 实时流式传输
- 自动过滤中间思考过程

### 健康检查
```
GET /health
```

## 注意事项

1. 模型配置要求
```python
ChatOpenAI(
    streaming=True,  # 必须启用流式模式
    callbacks=[handler]  # 需要绑定回调处理器
)
```

2. 中间件处理逻辑
- 需继承实现`AsyncIteratorCallbackHandler`
- 注意处理最终答案的边界条件
- 建议保留原始token处理逻辑

3. 性能建议
- 保持异步调用链完整性
- 合理设置max_iterations限制
- 建议添加超时处理机制

4. 扩展方向
- 添加对话历史管理
- 集成工具调用功能
- 增加速率限制
- 添加鉴权中间件
```



## 前端适配示例

```js
async function streamChat() {
    const response = await fetch('/stream-chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query: "你好" })
    });
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    while(true) {
        const { done, value } = await reader.read();
        if(done) break;
        
        const event = decoder.decode(value);
        // 解析SSE格式：event.data
        const data = event.replace('data: ', '');
        console.log('Received:', data);
    }
}

```