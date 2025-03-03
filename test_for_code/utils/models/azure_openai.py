import os
import json

def load_config(config_path="../config/config.json"):
    with open(config_path, "r") as f:
        config = json.load(f)
    return config

# 加载配置
config = load_config()

# 设置环境变量
os.environ["AZURE_OPENAI_KEY"] = config.get("AZURE_OPENAI_KEY", "default_key")
os.environ["AZURE_OPENAI_ENDPOINT"] = config.get("AZURE_OPENAI_ENDPOINT", "https://lechuang.openai.azure.com/")
os.environ["AZURE_API_VERSION"] = config.get("AZURE_API_VERSION", "2023-05-15")

from openai import AzureOpenAI

client = AzureOpenAI(
    # azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2023-05-15",
    azure_endpoint="https://lechuang.openai.azure.com",
    azure_deployment="lechuang-gpt-35-bak"
)


import time

def get_openai_response(messages, api_key, model="", temperature=0, max_tokens=1024, n=1, patience=200, sleep_time=30):
    while patience > 0:
        patience -= 1
        try:
            client = AzureOpenAI(
                # This is the default and can be omitted
                api_key=api_key,
                api_version="2023-05-15",
                azure_endpoint="https://lechuang.openai.azure.com",
                azure_deployment="lechuang-gpt-35-bak",
            )
            response = client.chat.completions.create(model=model,
                                                      messages=messages,
                                                      temperature=temperature,
                                                      max_tokens=max_tokens,
                                                      n=n)
            
            if n == 1:
                prediction = response.choices[0].message.content
                if prediction != "" and prediction is not None:
                    return prediction.strip()

        except Exception as e:
            print(e)
            if sleep_time > 0:
                time.sleep(sleep_time)
    return ""


def test():
    message = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": """summary this article! """}
    ]
    response = get_openai_response(message, os.getenv("AZURE_OPENAI_KEY"), model="gpt-35-turbo", temperature=0, max_tokens=1024, n=1, patience=200, sleep_time=30)
    print(response)

    return response

if __name__ == "__main__":
    test()