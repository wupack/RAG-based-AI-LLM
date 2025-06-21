# 在 qwen2_api.py 中添加调试信息
import os
api_key = os.getenv("DEEPSEEK_API_KEY")
print(f"使用的 API Key 前5位：{api_key[:5]}...")