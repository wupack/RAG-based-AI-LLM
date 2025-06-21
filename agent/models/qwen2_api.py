import requests
from typing import List
import os
from langchain.embeddings.base import Embeddings
#from config import Config

class DashScopeEmbeddings(Embeddings):  # 继承 LangChain 的 Embeddings 基类
    def __init__(self, model: str = "text-embedding-v2"): 
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding"
        self.api_key = os.getenv("QWEN_API_KEY")  # 从环境变量读取
        self.model = model  # 指定模型，如 "text-embedding-v2" 或 "text-embedding-v3"

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """批量文本嵌入（适配 LangChain）"""
        response = requests.post(
            self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.model,
                "input": {
                    "texts": texts  # DashScope 的输入字段是 input.texts
                }
            }
        )
        response.raise_for_status()
        return [item["embedding"] for item in response.json()["output"]["embeddings"]]
    
    def embed_query(self, text: str) -> List[float]:
        """单条文本嵌入（适配 LangChain）"""
        return self.embed_documents([text])[0]