from langchain_openai import ChatOpenAI
import json

# 读取配置文件
config_path = "../config/config.json"
with open(config_path, "r") as f:
    config = json.load(f)
    model_api_key = config["lechuang_model_api_key"]
    model_url = config["lechuang_model_url"]
    model_name = config["lechuang_model_name"]

# 选择语言模型
# model = ChatOpenAI(
#     temperature=0.1,
#     model=model_name,
#     openai_api_base=model_url,
#     openai_api_key=model_api_key,
# )

from azure_openai import  get_openai_response

print(get_openai_response([{"role": "user", "content": "你好"}],model_api_key,model_name,0.1))

# llm = ChatOpenAI(

#     temperature=0.1,

#     model="glm-4",

#     openai_api_key="6261e44ee59f6268cac4062244a68968.4pJstkR68lob2Z4k",

#     openai_api_base="https://open.bigmodel.cn/api/paas/v4/",

# )


# def openai_completion(messages):
#     response = model.invoke(messages)
#     print("response",response)
#     text = response['choices'][0]['message']['content']
#     return text

# openai_completion("你好")