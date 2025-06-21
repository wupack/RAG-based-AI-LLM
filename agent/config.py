import os
from pathlib import Path

class Config:
    # 模型配置
    #QWEN2_API_BASE = os.getenv("QWEN2_API_BASE", "https://api.qwen.com/v1")
    QWEN2_API_KEY = os.getenv("QWEN2_API_KEY", "")
    
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    
    # 路径配置
    DATA_DIR = Path("data\product_docs")
    DB_DIR = Path("data\chroma_db")
    
    # 文本处理
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200