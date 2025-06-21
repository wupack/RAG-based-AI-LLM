from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from models.qwen2_api import DashScopeEmbeddings 
from knowledge.loader import load_documents
from config import Config

def create_vector_store():
    documents = load_documents()
    
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
        persist_directory=str(Config.DB_DIR)
    )
    return vectorstore