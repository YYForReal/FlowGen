from typing import List, Optional
import torch
from transformers import AutoTokenizer, AutoModel
from langchain_openai import ChatOpenAI
from langchain.llms.utils import enforce_stop_tokens

class ChatGLM3(ChatOpenAI):
    max_token: int = 8192
    temperature: float = 0.01
    top_p = 0.9
    tokenizer: object = None
    model: object = None
    history = []

    def __init__(self):
        super().__init__()
        print("construct ChatGLM3")

    @property
    def _llm_type(self) -> str:
        return "ChatGLM3"

    def load_model(self, model_path=None, quantize=False):
        torch.cuda.empty_cache()
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        self.model = AutoModel.from_pretrained(model_path, trust_remote_code=True).half()
        if quantize:
            self.model = self.model.quantize(8)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self.model.to(device)
        self.model.eval()

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        response, _ = self.model.chat(
            self.tokenizer,
            prompt,
            history=self.history,
            max_length=self.max_token,
            temperature=self.temperature,
            top_p=self.top_p,
        )
        if stop is not None:
            response = enforce_stop_tokens(response, stop)
        return response

    def __call__(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        torch.cuda.empty_cache()
        return self._call(prompt, stop)
