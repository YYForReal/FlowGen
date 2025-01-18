import os
from dotenv import load_dotenv
from zigent.llm.agent_llms import LLM
from typing import List, Dict
from zigent.actions import BaseAction, ThinkAct, FinishAct
from zigent.agents import BaseAgent
from zigent.commons import TaskPackage, AgentAct
from zigent.actions.InnerActions import INNER_ACT_KEY
from datetime import datetime
import json

# 加载环境变量
load_dotenv()

# 从环境变量中读取api_key
api_key = os.getenv('ZISHU_API_KEY')
base_url = "http://43.200.7.56:8008/v1"
chat_model = "glm-4-flash"

# 配置 LLM
llm = LLM(api_key=api_key, base_url=base_url, model_name=chat_model)


class WriteDirectoryAction(BaseAction):
    """生成教程目录结构的动作"""

    def __init__(self):
        action_name = "WriteDirectory"
        action_desc = "生成教程目录结构"
        params_doc = {
            "topic": "(Type: string): 教程主题名称",
            "language": "(Type: string): 输出语言（默认：'Chinese'）"
        }
        super().__init__(action_name, action_desc, params_doc)

    def __call__(self, **kwargs):
        topic = kwargs.get("topic", "")
        language = kwargs.get("language", "Chinese")

        directory_prompt = f"""
        请为主题"{topic}"生成教程目录结构，要求：
        1. 输出语言必须是{language}
        2. 严格按照以下字典格式输出: {{
            "title": "xxx", 
            "directory": [
                {{"章节1": ["小节1", "小节2"]}}, 
                {{"章节2": ["小节3", "小节4"]}}
            ]
        }}
        3. 目录层次要合理，包含主目录和子目录
        4. 每个目录标题要有实际意义
        5. 不要有多余的空格或换行
        """

        # 调用 LLM 生成目录
        directory_data = llm.run(directory_prompt)
        # directory_data = llm.llm_chain.invoke({"prompt": directory_prompt})

        try:
            directory_data = json.loads(directory_data)
        except:
            directory_data = {"title": topic, "directory": []}

        return {
            "topic": topic,
            "language": language,
            "directory_data": directory_data
        }


class WriteContentAction(BaseAction):
    """生成教程内容的动作"""

    def __init__(self):
        action_name = "WriteContent"
        action_desc = "根据目录结构生成详细的教程内容"
        params_doc = {
            "title": "(Type: string): 小节标题",
            "chapter": "(Type: string): 章节标题",
            "directory_data": "(Type: dict): 完整的目录结构",
            "language": "(Type: string): 输出语言（默认：'Chinese'）"
        }
        super().__init__(action_name, action_desc, params_doc)

    def __call__(self, **kwargs):
        title = kwargs.get("title", "")
        chapter = kwargs.get("chapter", "")
        directory_data = kwargs.get("directory_data", {})
        language = kwargs.get("language", "Chinese")

        content_prompt = f"""
        请为教程章节生成详细内容：
        教程标题: {directory_data.get('title', '')}
        章节: {chapter}
        小节: {title}
        
        要求：
        1. 内容要详细且准确
        2. 如果需要代码示例，请按标准规范提供
        3. 使用 Markdown 格式
        4. 输出语言必须是{language}
        5. 内容长度适中，通常在500-1000字之间
        """

        # 调用 LLM 生成内容 （哪来的llm_chain）
        content = llm.run(content_prompt)
        # content = llm.llm_chain.invoke({"prompt": content_prompt})

        return content


class TutorialAssistant(BaseAgent):
    """管理目录和内容创建的教程生成助手"""

    def __init__(self, llm: LLM, language: str = "Chinese"):
        name = "TutorialAssistant"
        role = """你是一个专业的教程编写者。你可以创建结构良好、内容全面的教程，逻辑清晰，能够将复杂概念解释得通俗易懂。"""

        super().__init__(name=name, role=role, llm=llm)

        self.language = language
        self.directory_action = WriteDirectoryAction()
        self.content_action = WriteContentAction()

        # 添加一个示例任务
        self._add_tutorial_example()

    def _generate_tutorial(self, directory_data: Dict) -> str:
        """根据目录结构生成完整的教程内容"""
        full_content = []
        title = directory_data["title"]
        full_content.append(f"# {title}\n")

        # 生成目录
        full_content.append("## 目录\n")
        for idx, chapter in enumerate(directory_data["directory"], 1):
            for chapter_title, sections in chapter.items():
                full_content.append(f"{idx}. {chapter_title}\n")
                for section_idx, section in enumerate(sections, 1):
                    full_content.append(f"   {idx}.{section_idx}. {section}\n")
        full_content.append("---\n")

        # 生成每个部分的内容
        for chapter in directory_data["directory"]:
            for chapter_title, sections in chapter.items():
                for section in sections:
                    content = self.content_action(
                        title=section,
                        chapter=chapter_title,
                        directory_data=directory_data,
                        language=self.language
                    )
                    full_content.append(content)
                    full_content.append("---\n")

        return "\n".join(full_content)

    def __call__(self, task: TaskPackage):
        """处理生成教程的任务"""
        # 从任务中提取主题
        topic = task.instruction.split("Create a ")[-1].split(" tutorial")[0]

        # 生成目录结构
        directory_result = self.directory_action(
            topic=topic,
            language=self.language
        )

        print(directory_result)

        # 生成完整的教程
        tutorial_content = self._generate_tutorial(
            directory_result["directory_data"])

        # 保存结果
        task.answer = tutorial_content
        task.completion = "completed"

        return task

    def _add_tutorial_example(self):
        """添加一个示例任务以展示如何生成一个Python教程的目录和内容"""
        exp_task = "Create a Python tutorial for beginners"
        exp_task_pack = TaskPackage(instruction=exp_task)
        topic = "Python基础教程"

        act_1 = AgentAct(
            name=ThinkAct.action_name,
            params={INNER_ACT_KEY: "首先，我将为Python教程创建一个目录结构，然后生成每个部分的详细内容。"}
        )
        obs_1 = "好的，我将从目录结构开始。"

        act_2 = AgentAct(
            name=self.directory_action.action_name,
            params={
                "topic": topic,
                "language": self.language
            }
        )
        obs_2 = """{"title": "Python基础教程", "directory": [
            {"第一章：Python介绍": ["1.1 什么是Python", "1.2 环境搭建"]},
            {"第二章：基础语法": ["2.1 变量和数据类型", "2.2 控制流"]}
        ]}"""

        act_3 = AgentAct(
            name=self.content_action.action_name,
            params={
                "title": "什么是Python",
                "chapter": "第一章：Python介绍",
                "directory_data": json.loads(obs_2),
                "language": self.language
            }
        )
        obs_3 = """# 第一章：Python介绍

## 什么是Python

Python是一种高级编程语言，设计哲学强调代码的可读性和简洁明了的语法。它支持多种编程范式，包括面向对象、命令式、函数式和过程式编程。Python由Guido van Rossum于1991年创建，并继续发展至今。

..."""

        act_4 = AgentAct(
            name=FinishAct.action_name,
            params={INNER_ACT_KEY: "教程结构和内容生成成功。"}
        )
        obs_4 = "教程生成任务成功完成。"

        exp_act_obs = [(act_1, obs_1), (act_2, obs_2),
                       (act_3, obs_3), (act_4, obs_4)]

        self.prompt_gen.add_example(
            task=exp_task_pack,
            action_chain=exp_act_obs
        )


if __name__ == "__main__":
    assistant = TutorialAssistant(llm=llm)

    # 交互式生成教程
    FLAG_CONTINUE = True
    while FLAG_CONTINUE:
        input_text = input("你想创建什么教程？\n")
        task = TaskPackage(instruction=input_text)
        result = assistant(task)
        print("\n生成的教程：\n")
        print(result.answer)

        # 创建输出目录
        output_dir = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        os.makedirs(output_dir, exist_ok=True)

        # 保存文件
        output_file = os.path.join(output_dir, f"{input_text}.md")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result.answer)

        if input("你想再创建一个教程吗？(y/n)：").lower() != "y":
            FLAG_CONTINUE = False
