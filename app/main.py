from fastapi import FastAPI, HTTPException
from app.agent import run_agent
from app.schemas import ChatRequest, ChatResponse
from app.store import store

app = FastAPI(
    title="Banking Security Agent",
    description="AI assistant for banking security",
    version="1.0.0"
)

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse, tags=["Agent"])
def chat(request: ChatRequest) -> ChatResponse:
    try:
        return run_agent(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/state",tags=["Debug"])
def debug():
    return {
        "cards": store.cards,
        "disputes": store.disputes,
    }