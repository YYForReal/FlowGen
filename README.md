# 科研绘图助手 FlowGen

> 目标：本项目将实现一个自动帮助科研er绘图的agent，通过对话的形式生成各类实验数据的绘图文件，可编辑的流程图。

> 顺便存储基于Datawhale的课程wow agent所作的笔记。

> 原课程链接：[@Datawhale课程](https://www.datawhale.cn/learn/summary/86)

> 始于 2025-01-13



## 目录

- [Datawhale课程笔记](./learning)
- [绘图助手](./drawing_assistant)



### 通信协议规范：

```
// 请求格式
{
    message: "用户输入内容",
    fileContent: "<mxfile>...</mxfile>" // 当前文件XML内容
}

// 响应格式
{
    analysis: "文本分析结果", 
    fileContent: "<mxfile>...</mxfile>" // 修改后的文件内容
}
```


### 核心交互流程：

用户输入消息 → 获取当前文件内容 → 发送模拟请求
接收响应 → 更新聊天记录 → 应用文件修改



背景资料参考：
1. plantUML入门：
https://zhuanlan.zhihu.com/p/1158714578
2. https://uqoo.cc/plantuml-jian-jie-ji-webduan-xuan-ran-fang-fa/
