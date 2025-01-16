# Task 02 - LLM 工具调用与 RAG 实践

本任务主要探索了基于 LLM 的工具调用和 RAG (检索增强生成) 的实践应用。通过实现多个示例，我们深入理解了如何将大语言模型与外部工具和知识库结合使用。

博客地址：[blog.md](./blog.md)


## 主要内容

### 1. LLM 工具调用

我们实现了基于 ReAct 范式的工具调用代理，主要包含以下示例：

- 基础数学运算工具 (`tool_agent_demo.ipynb`)
  - 实现了加法、乘法等基础运算工具
  - 通过 ReActAgent 实现了多步计算的推理过程
  - 支持中文自然语言输入和结果输出

- 天气查询工具
  - 实现了简单的城市天气查询功能
  - 支持多城市温度查询（如纽约、北京等）

### 2. 数据库交互

在 `chat_database_demo.py` 中，我们实现了：

- SQLite 数据库的创建和基础数据填充
- 基于自然语言的数据库查询引擎
- 数据可视化展示
- 部门统计数据的分析工具

### 3. 联网搜索能力

通过 `ZhipuSearchAgent.py`，我们实现了：

- 基于智谱 AI 的联网搜索功能
- 支持实时信息获取和更新
- 结构化的搜索结果处理

### 4. RAG 实践

在 Markdown 文件解析和检索方面：

- 实现了 Markdown 文档的结构化解析
- 使用 LlamaIndex 构建文档索引
- 支持基于语义的文档检索和问答

## 技术栈

- LLM 框架：LlamaIndex
- 数据库：SQLite
- 可视化：Matplotlib
- API 集成：智谱 AI、OpenAI 接口
- 开发语言：Python 3.11

## 项目结构

```
task02/
├── README.md                    # 本文档
├── tool_agent_demo.ipynb        # 工具调用示例
├── chat_database_demo.py        # 数据库交互示例
├── ZhipuSearchAgent.py          # 联网搜索代理
├── markdown文件解析.py           # Markdown 解析工具
├── llm.py                       # LLM 基础类实现
└── data/                        # 数据文件目录
    └── plantuml.md             # 示例 Markdown 文档
```

## 主要发现与思考

1. **工具调用的灵活性**
   - ReAct 范式能有效地处理多步推理任务
   - 工具的抽象定义对于扩展性至关重要

2. **RAG 系统的优势**
   - 通过检索增强可以显著提升回答的准确性
   - 文档结构化处理对于检索效果有重要影响

3. **实践中的挑战**
   - 中文分词和语义理解需要特别处理
   - 工具调用的错误处理和恢复机制很重要
   - 检索结果的相关性评估需要优化

## 后续改进方向

1. 优化中文文档的解析和索引效果
2. 增强工具调用的错误处理机制
3. 改进搜索结果的相关性排序
4. 添加更多实用工具和集成能力
5. 优化代码结构和文档组织

## 参考资料

- LlamaIndex 官方文档
- ReAct: Synergizing Reasoning and Acting in Language Models
- 智谱 AI 开发文档
