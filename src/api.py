from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import json
import uvicorn

# Import Service Logic
from src.services import call_model_generator, retrieve_context, save_feedback
from src.database import init_db

app = FastAPI(title="Smart Court AI API", version="1.0.0")

# Request Models
class ChatRequest(BaseModel):
    query: str
    username: str
    model: Optional[str] = "Claude 3.5 Sonnet" # Default
    kb_id: Optional[str] = "LOCAL_KB"

class FeedbackRequest(BaseModel):
    username: str
    query: str
    model: str
    answer: str
    score: int

@app.on_event("startup")
def startup_event():
    init_db()

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    """
    Streaming chat endpoint.
    Retrieves context and streams the LLM response.
    """
    # 1. Retrieve Context
    context, citations = retrieve_context(req.query, req.kb_id)
    
    # 2. Generator Wrapper
    async def response_generator():
        # Yield Citations first (as a special event or header if needed, 
        # but for simplicity we stream text. In real app, might separate metadata)
        
        # Call the generator from services
        # Note: call_model_generator is synchronous generator, 
        # so we iterate it. faster than threading for this simple case.
        gen = call_model_generator(req.model, req.query, context, citations)
        for chunk in gen:
            yield chunk

    return StreamingResponse(response_generator(), media_type="text/plain")

@app.post("/feedback")
def feedback_endpoint(req: FeedbackRequest):
    try:
        save_feedback(req.username, req.query, req.model, req.score, req.answer)
        return {"status": "success", "message": "Feedback saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
