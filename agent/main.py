from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from models.deepseek_r1 import DeepSeekR1
from models.qwen2_api import DashScopeEmbeddings
from knowledge.vector_store import create_vector_store, load_vector_store
from agents.workflow import create_workflow
from config import Config
from langchain_core.messages import HumanMessage, AIMessage
from fastapi import UploadFile, File
import shutil
from pathlib import Path
from knowledge.loader import load_documents
import os
from typing import List, Dict

# Global variables
llm = DeepSeekR1()
vectorstore = None
agent = None
vector_dbs = []
current_db = None

def scan_existing_databases():
    """Scan existing vector database directories"""
    VECTOR_DB_DIR = Path("data/vector_dbs")
    VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)
    
    databases = []
    
    # Scan all subdirectories in data/vector_dbs
    for db_dir in VECTOR_DB_DIR.iterdir():
        if db_dir.is_dir():
            db_name = db_dir.name
            databases.append({
                "name": db_name,
                "path": str(db_dir)
            })
    
    # If no databases exist, create a default one
    if not databases:
        default_db_path = VECTOR_DB_DIR / "default_db"
        default_db_path.mkdir(exist_ok=True)
        documents = load_documents(data_dir=r"data\product_docs")
        create_vector_store(documents, db_dir=str(default_db_path))
        databases.append({
            "name": "default_db",
            "path": str(default_db_path)
        })
    
    return databases

def initialize_database(db_name: str) -> bool:
    """初始化指定的数据库"""
    global vectorstore, agent, current_db
    
    # 查找对应的数据库路径
    db_info = next((db for db in vector_dbs if db["name"] == db_name), None)
    if not db_info:
        return False
    
    # 加载向量数据库
    vectorstore = load_vector_store(db_dir=db_info["path"])
    if vectorstore is None:
        return False
    
    try:
        # 创建agent工作流
        agent = create_workflow(vectorstore.as_retriever(search_kwargs={"k": 3}), llm)
        current_db = db_name
        return True
    except Exception as e:
        return False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application lifecycle events"""
    global vector_dbs, current_db
    
    # Scan existing databases
    vector_dbs = scan_existing_databases()
    
    # Select first database by default
    if vector_dbs:
        initialize_database(vector_dbs[0]["name"])
    
    yield  # Application runs here
    
    # Cleanup code (if needed)

app = FastAPI(
    title="RAG Intelligent Customer Service System",
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", include_in_schema=False)
async def chat_interface(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "vector_dbs": vector_dbs,
        "current_db": current_db
    })

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    if not agent:
        raise HTTPException(status_code=400, detail="Please select a knowledge base first")
    
    data = await request.json()
    try:
        result = agent.invoke({
            "messages": [HumanMessage(content=data["message"])],
            "retrieved_docs": []
        })
        return {"response": result["messages"][-1].content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/switch_vector_db")
async def switch_vector_db(request: Request):
    form_data = await request.form()
    db_name = form_data.get("db_name")
    
    try:
        initialize_database(db_name)
        return {"status": "success", "db_name": db_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

UPLOAD_DIR = Path("data/uploaded_files")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_DB_DIR = Path("data/vector_dbs")

@app.get("/upload")
async def upload_interface(request: Request):
    return templates.TemplateResponse("upload.html", {
        "request": request,
        "vector_dbs": vector_dbs
    })

@app.post("/api/rebuild_vector_db")
async def rebuild_vector_db(
    db_name: str = Form(...),
    files: List[UploadFile] = File(...)
):
    try:
        # Validate database name
        if not db_name or len(db_name) > 50:
            raise ValueError("Invalid database name")
        
        # Check if database already exists
        if any(db["name"] == db_name for db in vector_dbs):
            raise ValueError("Database name already exists")
        
        # 1. Create upload directory
        upload_subdir = UPLOAD_DIR / db_name
        upload_subdir.mkdir(exist_ok=True)
        
        # 2. Save uploaded files
        saved_files = []
        for file in files:
            file_path = upload_subdir / file.filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            saved_files.append(file_path)
        
        # 3. Create vector database directory
        db_path = VECTOR_DB_DIR / db_name
        db_path.mkdir(exist_ok=True)
        
        # 4. Generate new vector database
        documents = load_documents(data_dir=str(upload_subdir))
        create_vector_store(documents, db_dir=str(db_path))
        
        # 5. Update available databases list
        vector_dbs.append({"name": db_name, "path": str(db_path)})
        
        # 6. Automatically switch to new database
        initialize_database(db_name)
        
        return {
            "status": "success", 
            "db_name": db_name,
            "processed_files": len(saved_files)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)