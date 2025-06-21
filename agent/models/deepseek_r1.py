import requests
from typing import Optional
import os

class DeepSeekR1:
    def __init__(self):
        self.base = "https://api.deepseek.com/v1"
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
    
    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        response = requests.post(
            f"{self.base}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature
            }
        )
        return response.json()["choices"][0]["message"]["content"]