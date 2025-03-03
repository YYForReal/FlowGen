import base64
import json
import requests
import logging

# 设置日志配置
logging.basicConfig(
    filename="output/output.log",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s:%(message)s",
)


def load_config(config_path="config.json"):
    with open(config_path, "r") as f:
        config = json.load(f)
    return config


def encode_image_to_base64(image_path):
    logging.debug(f"Encoding image at path: {image_path}")
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def glm4v_summarize_image(image_path):
    config = load_config()
    model_api_key = config["vllm_model_api_key"]
    model_url = config["vllm_model_url"]
    model_name = config["vllm_model"]

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {model_api_key}",
    }

    # 将图像编码为base64字符串
    image_base64 = encode_image_to_base64(image_path)

    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "解释一下图中的现象"},
                    {"type": "image_url", "image_url": {"url": image_base64}},
                ],
            }
        ],
        "stream": False,
    }

    logging.debug(
        f"Sending request to GLM-4V model at {model_url} with payload: {payload}"
    )
    response = requests.post(model_url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        summary = response.json().get("choices")[0].get("message").get("content")
        logging.debug(f"Received response: {summary}")
        return summary
    else:
        logging.error(f"Error: {response.status_code}, {response.text}")
        return None
