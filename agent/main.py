from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from models.deepseek_r1 import DeepSeekR1
from models.qwen2_api import DashScopeEmbeddings
from knowledge.vector_store import create_vector_store
from agents.workflow import create_workflow
from config import Config
from langchain_core.messages import HumanMessage, AIMessage
from fastapi import UploadFile, File
import shutil
from pathlib import Path
from knowledge.loader import load_documents

app = FastAPI(title="RAG智能客服系统")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 初始化组件
#embeddings = DashScopeEmbeddings()
documents = load_documents(data_dir=r"data\product_docs")
vectorstore = create_vector_store(documents,db_dir=r"data\chroma_db")
llm = DeepSeekR1()
agent = create_workflow(vectorstore.as_retriever(search_kwargs={"k": 3}), llm)

@app.get("/", include_in_schema=False)
async def chat_interface(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    try:
        result = agent.invoke({
            "messages": [HumanMessage(content=data["message"])],
            "retrieved_docs": []
        })
        return {"response": result["messages"][-1].content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

UPLOAD_DIR = Path("data/uploaded_files")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/upload")
async def upload_interface(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@app.post("/api/rebuild_vector_db")
async def rebuild_vector_db(files: list[UploadFile] = File(...)):
    try:
        # 1. 保存上传文件
        saved_files = []
        for file in files:
            file_path = UPLOAD_DIR / file.filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            saved_files.append(file_path)
        
        # 2. 重新生成向量库
        global vectorstore  # 修改全局变量
        documents = load_documents(data_dir=r"data\uploaded_files")
        print("step:1")
        vectorstore = create_vector_store(documents,db_dir=r"data\anthoer_db")
        print("step:2")
        
        # 3. 更新agent的检索器
        global agent
        agent = create_workflow(vectorstore.as_retriever(search_kwargs={"k": 3}), llm)
        
        return {"status": "success", "processed_files": len(saved_files)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)