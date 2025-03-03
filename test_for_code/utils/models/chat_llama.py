import requests
import json
from langchain_openai import ChatOpenAI
from langchain.llms.utils import enforce_stop_tokens

class LlamaChat(ChatOpenAI):
    temperature: float = 0.1
    history = []
    api_secret: str = ""

    def __init__(self, api_secret: str):
        super().__init__()
        self.api_secret = api_secret
        print("construct LlamaChat")

    @property
    def _llm_type(self) -> str:
        return "LlamaChat"

    def llama_completion(self, messages):
        url = "https://api.atomecho.cn/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_secret}",
        }
        data = {
            "model": "Atom-7B-Chat",
            "messages": messages,
            "temperature": self.temperature,
            "stream": False,
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return None

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        messages = [{"role": "user", "content": prompt}]
        response = self.llama_completion(messages)
        if stop is not None:
            response = enforce_stop_tokens(response, stop)
        return response

    def __call__(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        return self._call(prompt, stop)
