import os
import json
import re

# openai 接口
def openai_completion(messages):
    import openai

    openai.api_type = "azure"
    openai.api_base = "https://lechuang.openai.azure.com"
    openai.api_key = "bc709d6234e04a80ab2d744eb2434086"
    openai.api_version = "2023-05-15"
    deployment_name = 'lechuang-gpt-35-bak'

    response = openai.ChatCompletion.create(
        engine="lechuang-gpt-35-bak",  # engine = "deployment_name".
        messages=messages,
        timeout=5 * 60,
        temperature = 0.1,
        max_tokens = 512
    )

    # print(response)
    text = response['choices'][0]['message']['content']
    return text


def erniebot_completion(messages):
    import erniebot

    erniebot.api_type = 'aistudio'
    # erniebot.access_token = '8c6abae9ba5c8f98d0de90381333ff7ee684dd0e'
    erniebot.access_token = '6ba65323de91f44039d5b89eb7c001e4bac85cac'
# 
    response = erniebot.ChatCompletion.create(
        # model='ernie-3.5',
        model='ernie-speed',
        
        messages=messages,
        temperature = 0.1,
    )
    result = response.get_result()
    return result


def glm4_completion(message):
    from zhipuai import ZhipuAI
    # client = ZhipuAI(api_key="fcea89cfd8a3249e207787d51f911ef6.0Hm07tsjksYPh5Et") # YY1的APIKey
    # client = ZhipuAI(api_key="6ef0040dd66c53d01737f5ef83f73de9.2YdehCzULcAQ4zdS") # YY2的APIKey
    client = ZhipuAI(api_key="9ddb3bc3b65eb442c1e5b13eee489e41.rTCBmTHsydcRuRft")
    # ZhipuAI.chat.Completions.create

    response = client.chat.completions.create(
        model="glm-4",  # 填写需要调用的模型名称
        messages = message,
        stream=False,
        temperature = 0.1,
        max_tokens= 512
    )
    # messages=[
    #     {"role": "user", "content": "你好"},
    #     {"role": "assistant", "content": "我是人工智能助手"},
    #     {"role": "user", "content": "你叫什么名字"},
    #     {"role": "assistant", "content": "我叫chatGLM"},
    #     {"role": "user", "content": "你都可以做些什么事"}
    # ],
    res = response.choices[0].message.content

    return res




def post(question):
    choice_example1 = """选择题格式如下：{"question":"xxx","options":[],"answer":"xxx"}, 
例如: 如果一个产生式的左部或右部含有无用符号,则此产生式称为()产生式。
A.非法
B.多余
C.非确定
D.无用
答案: D
输出为单行的JSON：
=====
{"question": "如果一个产生式的左部或右部含有无用符号,则此产生式称为()产生式。", "options": ["A.非法", "B.多余", "C.非确定", "D.无用"], "answer": "D.无用"},
=====
"""
    judge_example1 = """判断题格式：{"question":"xxx","answer":"xxx"},
例如：高级语言程序必须经过编译程序的翻译才能被计算机识别和执行。
A.错误
B.正确
答案: B
输出为单行的JSON：
======
{"question": "高级语言程序必须经过编译程序的翻译才能被计算机识别和执行。", "answer": "true"},
=====
"""

    fill_example1 = """填空题格式：{"question":"xxx","answer":"xxx"},提炼的问题需要以括号()表示,若存在多个答案，答案则是英文逗号分隔的字符串。
例如：扫描器的任务是从 __源程序___ 中识别出一个个_单词符号___ 。
输出为单行的JSON：
======
{"question": "扫描器的任务是从 ( ) 中识别出一个个 ( )。", "answer": "源程序,单词符号"},
======
"""

    choice_example2 = """选择题格式如下：{"question":"xxx","options":[],"answer":"xxx"}, 
例如: 如果一个产生式的左部或右部含有无用符号,则此产生式称为无用产生式。
输出为单行的JSON：
=====
{"question": "如果一个产生式的左部或右部含有无用符号,则此产生式称为()产生式。", "options": ["A.非法", "B.多余", "C.非确定", "D.无用"], "answer": "D.无用"},
=====
"""
    judge_example2 = """判断题格式：{"question":"xxx","answer":"xxx"},
例如：高级语言程序必须经过编译程序的翻译才能被计算机识别和执行。
输出为单行的JSON：
======
{"question": "高级语言程序必须经过编译程序的翻译才能被计算机识别和执行。", "answer": "true"},
=====
"""

    fill_example2 = """填空题格式：{"question":"xxx","answer":"xxx"},提炼的问题需要以括号()表示,若存在多个答案，答案则是英文逗号分隔的字符串。
例如：扫描器的任务是从源程序中识别出一个个单词符号。
输出为单行的JSON：
======
{"question": "扫描器的任务是从 ( ) 中识别出一个个 ( )。", "answer": "源程序,单词符号"},
======
"""

# {choice_example}
# {judge_example}
# {fill_example}

    addition_prompt = """1. 需要保证question里面不出现答案。若出现类似“_B____”这种，需将内部的答案字母删除。若出现“(√)”这种，也需要在question中去除。"""

    # 定义API接口的URL
    content = f"""你是一个精通编译原理的题目生成器，我需要你理解我发给你的相关内容,为我构造出特定格式的问答对并以JSON格式返回。后续直接以JSON格式返回问答对。
{judge_example2}
{choice_example2}
{fill_example2}
### 请注意:
1. 若片段残缺，则依据你的知识推理剩余的问题或选项内容。并且给出正确答案。保证选择题有4个选项options。判断题只需提供answer。
2. 若可以解析出多个问答对则返回多行JSON数据即可，不需要有任何额外的输出。
3. 若此页内容与编译原理专业知识完全无关，则输出空内容即可。不需要输出“本书xxx”。
4. 生成的问答对必须是独立的内容,而没有其他内容的关联。比如不需要引用图片等。
下面是你需要构造问答对的相关内容：
""" + question

    try:
        response = openai_completion(content)
        print(response)
        return response
    except Exception as e:
        print("error", str(e))


def post2(ask_question, type,mode = "openai"):

    choice_q1 = "语法分析是依据语言的什么规则进行的()。['A.语法', 'B.语义', 'C.语用', 'D.运行']"
    choice_a1 = "A.语法"
    choice_q2 = "32.词法分析器的输入是什么()。['A.单词串', 'B.源程序', 'C.语法单位', 'D.目标程序']"
    choice_a2 = "B.源程序"
    choice_example = [(choice_q1,choice_a1),(choice_q2,choice_a2)]

    judge_q1 = "编译程序与具体的机器有关,与具体的语言无关。"
    judge_a1 = "false"
    judge_q2 = "递归下降分析法是自顶向下分析方法。"
    judge_a2 = "true"
    judge_example = [(judge_q1,judge_a1),(judge_q2,judge_a2)]

    fill_example = [
        ("语法分析的方法大致可分为两类，一类是 ( )分析法，另一类是 ( )分析法。", "自上而下, 自下而上"),
        ("如果一个文法存在某个句子对应两棵不同的语法树， 则称这个文法是( )。", "二义性文法")
    ]

    short_example = [
        ("编译方式与解释方式的根本区别为什么？", "编译方式与解释方式的根本区别在于是否生成目标代码。"),
        ("词法分析器是用于做什么的？", "词法分析器是用于识别单词的。")
    ]

    # 根据type映射题目
    question_type_dict = {
        "choice": {
            "type": "选择题",
            "require": "你的答案必须提供一个完整的选项比如A.XXXXX或者B.XXXXX，而不可以是除了选项之外的其他回答。注意：你给出的答案只能是选项列表中的其中一个，不需要给出解释，必须用中文回复，请务必必须认真、仔细思考问题，回答必须符合题目要求。",
            "example": choice_example
        },
        "judge": {
            "type": "判断题",
            "require": "你必须对题目进行分析，只需要回答'true;或者'false'，不要跑题，不要有任何额外回答。注意：你的回答只能是'true'或者'false'，不能是其他回答。必须认真、仔细思考问题，回答必须符合题目要求。",
            "example": judge_example
        },
        "blank": {
            "type": "填空题",
            "require":  "你必须对题目进行分析，只需要回答题目空缺的部分，不要跑题，不要有任何额外回答。注意：你的回答只能是填空题中“( )”里面的内容，不要回答其他无关内容。请务必认真、仔细思考问题，回答必须符合题目要求。",
            "example": fill_example
        },
        "short":{
            "type": "简答题",
            "require":  "你必须对简答题进行分析作答，不要跑题，不需要任何额外的回答。注意：你必须用中文回复，必须认真、仔细思考问题，回答必须符合题目要求。",
            "example": short_example            
        }
    }
    question = question_type_dict[type]


    first_chat = f"""你是最棒的编译原理教师，你精通编译原理。现在我给你一道{question["type"]}。{question["require"]}"""


    his = [
        # 考虑点:回答的时候要不要加上FINAL ANSWER
        # 定义+提问示例1
        {'role': 'user', 'content': first_chat + "\nQUESTION: " + question["example"][0][0]},
        {'role': 'assistant', 'content': f"" + question["example"][0][1]}, # FINAL ANSWER: 
        # 提问示例2
        {'role': 'user', 'content': "QUESTION: " + question["example"][1][0]},
        {'role': 'assistant', 'content': f"" + question["example"][1][1]},
        # 提问
        {'role': 'user', 'content': f"QUESTION: {ask_question}"},
    ]
    # print(his)
    # input("--------------")
    try:
        if mode == "erniebot":
            # 这里是调文心一言的
            response = erniebot_completion(his)
        elif mode == "openai":
            # 这里是调GPT的
            response = openai_completion(his)
        elif mode == "glm4":
            # 调ChatGLM4的
            response = glm4_completion(his)
        else:
            raise Exception("mode error")
        return response
    except Exception as e:
        print("error", str(e))



# post2("词法特性是什么意思？","short",mode="erniebot")