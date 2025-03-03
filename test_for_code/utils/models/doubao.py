
import os
from openai import OpenAI
import json

# 读取配置文件
config_path = "../config/config.json"
with open(config_path, "r") as f:
    config = json.load(f)
    model_api_key = config["doubao_api_key"]
    model_url = config["doubao_api_base"]
    model_name = config["doubao_model"]

def get_doubao_client():
    return OpenAI(api_key=model_api_key, base_url=model_url)


def test_doubao_client():
    client = get_doubao_client()
    # Non-streaming:
    print("----- standard request -----")
    completion = client.chat.completions.create(
        model = model_name,  # your model endpoint ID
        messages = [
            {"role": "system", "content": "你是豆包，是由字节跳动开发的 AI 人工智能助手"},
            {"role": "user", "content": "讲述下《A Christmas Carol》是由查尔斯·狄更斯（Charles Dickens）创作的一本经典小说的剧情。"},
        ],
    )
    print(completion.choices[0].message.content)

    return client



# Streaming:
# print("----- streaming request -----")
# stream = client.chat.completions.create(
#     model = "ep-20240715143919-smxc6",  # your model endpoint ID
#     messages = [
#         {"role": "system", "content": "你是豆包，是由字节跳动开发的 AI 人工智能助手"},
#         {"role": "user", "content": "常见的十字花科植物有哪些？"},
#     ],
#     stream=True
# )

# for chunk in stream:
#     if not chunk.choices:
#         continue
#     print(chunk.choices[0].delta.content, end="")
# print()
def get_doubao_model():

    from langchain_experimental.graph_transformers import LLMGraphTransformer
    from langchain_openai import ChatOpenAI
    # from graphrag.query.llm.oai.chat_openai import ChatOpenAI
    from langchain_core.prompts import (
        ChatPromptTemplate,
        # HumanMessagePromptTemplate,
        # PromptTemplate,
    )

    import os
    # from graphrag.query.llm.oai.typing import OpenaiApiType

    # llm = ChatOpenAI(temperature=0, model_name="gpt-4o")
    api_key = os.environ["DOUBAO_API_KEY"]
    llm_model = os.environ["DOUBAO_MODEL"]
    api_base = os.environ["DOUBAO_API_BASE_URL"]

    llm = ChatOpenAI(
        api_key=api_key,
        model=llm_model,
        # api_type=OpenaiApiType.OpenAI,
        max_retries=20,
        base_url= api_base
        # model_kwargs = {"api_base":api_base},
    )

    # print(llm("你好"))

    return llm