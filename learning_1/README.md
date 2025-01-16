<<<<<<< HEAD:learning/README.md





=======
# 智能客服助手的设计与优化实践

本篇笔记经过学习Datawhale的课程2所作。原课程链接：[@Datawhale课程](https://www.datawhale.cn/learn/content/86/3057)

## 1. Prompt设计心得

### 1.1 结构化设计的重要性

在实践中，我发现良好的prompt结构设计对于AI助手的表现至关重要。基于LangGPT的思想，我们采用了以下核心原则：

1. **模块化组织**：
   - 将不同功能的prompt分离（注册、查询、删除等）
   - 使用统一的消息状态管理
   - 便于维护和扩展

2. **语义一致性**：
   - 使用统一的令牌系统（如 "registered workers", "query workers"）
   - 保持状态转换的清晰性
   - 确保错误处理的一致性

3. **上下文管理**：
   - 实现了用户画像系统
   - 保持对话历史
   - 支持个性化服务

### 1.2 实践中的改进

从最初的基础版本改进到当前版本，主要做了以下优化：

```python
# 优化前：所有prompt混在一起
sys_prompt = """你是一个聪明的客服..."""

# 优化后：模块化管理
SYSTEM_PROMPT = """..."""
REGISTERED_PROMPT = """..."""
QUERY_PROMPT = """..."""
```

## 2. 智谱API集成简介

智谱AI提供了与OpenAI兼容的接口，集成过程相对简单：

```python
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv('ZHIPU_API_KEY'),
    base_url="https://open.bigmodel.cn/api/paas/v4/"
)
```

关键配置：
- base_url: 智谱AI的API地址
- chat_model: "glm-4-flash"
- API密钥管理：使用.env文件存储

## 3. Demo优化实践

### 3.1 数据持久化

最重要的优化是添加了数据持久化层：

```python
class DataManager:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.users_file = self.data_dir / "users.json"
        self.conversations_file = self.data_dir / "conversations.json"
        self.reminders_file = self.data_dir / "reminders.json"
```

主要改进：
1. 用户数据持久化
2. 对话历史记录
3. 提醒事项管理

### 3.2 用户体验优化

增加了更多人性化的功能：

```python
class SmartAssistantV2:
    def __init__(self, current_user_id=None):
        self.user_profile = {
            "preferences": {},  # 用户偏好
            "reminders": [],    # 提醒事项
            "history": []       # 历史交互
        }
```

关键特性：
1. 用户画像系统
2. 个性化回复
3. 任务提醒功能

### 3.3 代码架构优化

1. **模块化设计**：
   - prompts.py：提示词管理
   - data_manager.py：数据管理
   - smart_assistant_v2.py：核心业务逻辑

2. **状态管理改进**：
   - 清晰的状态转换机制
   - 完整的错误处理
   - 会话上下文保持

3. **可扩展性**：
   - 易于添加新功能
   - 支持多种数据存储方式
   - 灵活的配置管理

## 总结与展望

当前的实现已经具备了基础的智能客服功能，并通过数据持久化和用户画像提供了个性化服务。未来可以考虑：

1. 添加数据库支持，替代JSON文件存储
2. 实现多轮对话的上下文理解
3. 增加更多的个性化特征
4. 添加性能监控和日志系统

通过这次优化实践，我们不仅提升了系统的功能性，也增强了代码的可维护性和可扩展性。这为后续的功能迭代打下了良好的基础。 
>>>>>>> 053a15bda010ac30e0db366f1b842cd613d4d6d1:learning_1/README.md
