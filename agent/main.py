from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from models.deepseek_r1 import DeepSeekR1
from models.qwen2_api import DashScopeEmbeddings
from knowledge.vector_store import create_vector_store
from agents.workflow import create_workflow
from config import Config
from langchain_core.messages import HumanMessage, AIMessage

app = FastAPI(title="RAG智能客服系统")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 初始化组件
embeddings = DashScopeEmbeddings()
vectorstore = create_vector_store()
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)