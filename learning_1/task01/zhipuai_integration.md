# 智谱AI接入指南

## 概述
智谱AI提供了兼容OpenAI接口的服务，可以通过OpenAI的SDK快速接入。本文档将指导您如何配置和使用智谱AI的服务。

## 准备工作

### 1. 获取API密钥
1. 访问[智谱开放平台](https://open.bigmodel.cn/usercenter/proj-mgmt/apikeys)
2. 登录/注册账号
3. 在API密钥管理页面创建新的API密钥
4. 保存API密钥（注意：密钥只显示一次）

### 2. 环境配置

```python
# 安装必要的包
pip install openai python-dotenv
```

创建`.env`文件：
```plaintext
ZHIPU_API_KEY=your_api_key_here
```

## 基础配置

```python
import os
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()
api_key = os.getenv('ZHIPU_API_KEY')

# 智谱AI的基础配置
base_url = "https://open.bigmodel.cn/api/paas/v4/"
chat_model = "glm-4-flash"  # 或其他可用模型

# 创建客户端
client = OpenAI(
    api_key=api_key,
    base_url=base_url
)
```

## 模型使用

### 1. 对话完成（Chat Completion）

```python
def get_chat_completion(messages, temperature=0.7):
    try:
        response = client.chat.completions.create(
            model=chat_model,
            messages=messages,
            temperature=temperature,
            stream=False,
            max_tokens=2000,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error: {e}")
        return None
```

### 2. 流式响应

```python
def get_streaming_response(messages, temperature=0.7):
    try:
        response = client.chat.completions.create(
            model=chat_model,
            messages=messages,
            temperature=temperature,
            stream=True,
            max_tokens=2000,
        )
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        print(f"Error: {e}")
        yield None
```

## 最佳实践

### 1. 错误处理
- 实现适当的重试机制
- 处理API限流和超时
- 记录错误日志

```python
import time
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def robust_chat_completion(messages):
    try:
        return get_chat_completion(messages)
    except Exception as e:
        print(f"Retry due to error: {e}")
        raise
```

### 2. 成本优化
- 合理设置max_tokens
- 使用缓存减少重复请求
- 选择合适的模型规格

### 3. 提示词优化
- 使用清晰的指令
- 提供足够的上下文
- 控制提示词长度

## 常见问题

1. **API调用失败**
   - 检查API密钥是否正确
   - 确认网络连接
   - 验证请求参数格式

2. **响应超时**
   - 检查网络状态
   - 调整超时设置
   - 考虑使用流式响应

3. **成本控制**
   - 监控API使用量
   - 设置使用限制
   - 优化提示词长度

## 参考资源

- [智谱AI开发文档](https://open.bigmodel.cn/dev/api/thirdparty-frame/openai-sdk)
- [OpenAI SDK文档](https://github.com/openai/openai-python)