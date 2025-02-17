# 科研绘图助手 FlowGen



> 目标：本项目将实现一个自动帮助科研er绘图的agent，通过对话的形式生成各类实验数据的绘图文件，可编辑的流程图。

> 顺便存储基于Datawhale的课程wow agent所作的笔记。

> 原课程链接：[@Datawhale课程](https://www.datawhale.cn/learn/summary/86)




## 效果

![image](./assets/before_1.png)

![image](./assets/after_1.png)


## 目录

- [相关笔记](./learning)
- [绘图助手后端](./backend)
- [绘图助手前端](./drawio-22.0.0)

## 更新日志

- 2025-01-13 项目启动！开始调研drawio等绘图实现。
- 2025-02-11 添加了绘图助手聊天窗口，可以通过对话即时生成`可编辑的绘图文件`。

## TODO

- 前端
    - 优化绘图文件的保存（or 转移到后端）
    - 绘图助手聊天窗口优化
        - 可拖拽
        - 可调整大小
        - 可隐藏/显示
        - 可调整模型参数
- 后端
    - 绘图助手服务优化（流式输出）
    - 应用类似Git diff算法，输出局部代码，最大匹配插入已有内容，优化绘图文件的修改（最重要！）

业务扩展侧：
    - 用户注册登录。
    - 用户绘图文件管理。
    - 多模态图片传入识别，立即架构再生成。
    - 模型能力（造更多精美的drawio图进行微调 or RAG，规范化 & 扩展单次输出token上限。）


另外一条技术路线（设想，但是预计更加繁琐）:
- 前端整合绘图的原子操作，插入、图标选择、拖拽、调整大小、隐藏、显示...
- 后端提供绘图的api，通过api调用，输出原子操作的绘图文件。



### 通信协议规范：

非流式：
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

流式（待设计）

...


### 核心交互流程：

用户输入消息 → 获取当前文件内容 → 发送模拟请求
接收响应 → 更新聊天记录 → 应用文件修改



背景资料参考：
1. plantUML入门：
https://zhuanlan.zhihu.com/p/1158714578
2. https://uqoo.cc/plantuml-jian-jie-ji-webduan-xuan-ran-fang-fa/
