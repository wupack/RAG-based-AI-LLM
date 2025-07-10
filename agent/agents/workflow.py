from langgraph.graph import StateGraph
from typing import TypedDict, Annotated, List
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.constants import END

class AgentState(TypedDict):
    messages: Annotated[List, lambda x, y: x + y]
    retrieved_docs: List[str]

def create_workflow(retriever, llm):
    def retrieve(state: AgentState):
        docs = retriever.invoke(state["messages"][-1].content)
        return {"retrieved_docs": [doc.page_content for doc in docs]}
    
    def generate(state: AgentState):
        prompt = f"""请基于以下信息回答问题，如果信息与问题无关，请忽略这些信息，仅根据自己的知识回答问题：
        {state['retrieved_docs']}
        
        问题：{state['messages'][-1].content}（小标题绝对不要用Markdown格式，Markdown格式的小标题会用**去包围）"""
        response = llm.generate(prompt)
        return {"messages": [AIMessage(content=response)]}
    
    workflow = StateGraph(AgentState)
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("generate", generate)
    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", END)
    return workflow.compile()