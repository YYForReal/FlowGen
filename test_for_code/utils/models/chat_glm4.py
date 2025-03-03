from langchain_openai import ChatOpenAI
import os
import json


# 读取配置文件
config_path = "config.json"
with open(config_path, "r") as f:
    config = json.load(f)
    model_api_key = config["model_api_key"]
    model_url = config["model_url"]
    model_name = config["model"]

# 选择语言模型
model = ChatOpenAI(
    temperature=0.1,
    model=model_name,
    base_url=model_url,
    openai_api_key=model_api_key,
)
