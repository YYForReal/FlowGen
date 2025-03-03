# 读取examples/rag_advanced.drawio文件代码，然后利用工具类读取第5 level开始的代码
# 设计prompts，让大模型生成代码块包裹的优化后的drawio代码，但是要保持相同的id。
# 然后完善工具类，能够实现基于prompts的代码块提取对应的xml元素，根据id进行替换。
# 如果出现了新的id，则表示新增。
