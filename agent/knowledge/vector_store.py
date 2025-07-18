from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from models.qwen2_api import DashScopeEmbeddings 
from knowledge.loader import load_documents
from config import Config
from pathlib import Path
from typing import Optional

def create_vector_store(documents,db_dir):
    
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP,
        length_function=len,
        is_separator_regex=False
    )
    splits = text_splitter.split_documents(documents)
    
    embeddings = DashScopeEmbeddings()
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=str(db_dir)
    )
    print("step:4")
    return vectorstore

def load_vector_store(db_dir: str) -> Optional[Chroma]:
    try:
        # 检查数据库目录是否存在
        if not Path(db_dir).exists():
            return None
            
        # 检查目录是否为空
        if not any(Path(db_dir).iterdir()):
            return None
            
        # 初始化嵌入模型
        embeddings = DashScopeEmbeddings()
        
        # 加载向量数据库
        vectorstore = Chroma(
            persist_directory=db_dir,
            embedding_function=embeddings
        )
        
        # 验证是否加载成功
        if not hasattr(vectorstore, '_collection'):
            return None
            
        return vectorstore
        
    except Exception as e:
        return None