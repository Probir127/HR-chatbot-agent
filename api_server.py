"""
api_server.py - FastAPI Server for HR Chatbot
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
import json
from datetime import datetime
from backend import ask_hr_bot_api

# Initialize FastAPI app
app = FastAPI(
    title="HR Chatbot API",
    description="API for Acme AI Ltd. HR Chatbot",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    chat_history: List[Dict[str, str]] = []
    session_token: Optional[str] = None
    is_new_session: bool = False

class ChatResponse(BaseModel):
    response: str
    session_token: Optional[str] = None
    is_new_session: bool = False

class RatingRequest(BaseModel):
    message: str
    response: str
    rating: int
    feedback: Optional[str] = None

class RatingResponse(BaseModel):
    status: str
    message: str

class SessionResponse(BaseModel):
    session_token: str
    message: str

# Simple session storage (in production, use Redis or database)
active_sessions = {}

def create_session():
    session_token = str(uuid.uuid4())
    active_sessions[session_token] = {
        "created_at": datetime.now(),
        "chat_history": []
    }
    return session_token

@app.get("/")
async def root():
    return {"status": "online", "service": "HR Chatbot API"}

# In your api_server.py, update the chat_endpoint function:

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # Session management
        session_token = request.session_token
        
        if request.is_new_session or not session_token or session_token not in active_sessions:
            session_token = create_session()
            is_new_session = True
        else:
            is_new_session = False
        
        # Get response from HR bot
        bot_response = ask_hr_bot_api(
            question=request.message,
            chat_history=request.chat_history,
            session_id=session_token
        )
        
        # Update session chat history
        if session_token in active_sessions:
            active_sessions[session_token]["chat_history"].append({
                "user": request.message,
                "bot": bot_response,
                "timestamp": datetime.now().isoformat()
            })
        
        return ChatResponse(
            response=bot_response,
            session_token=session_token,
            is_new_session=is_new_session
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/new-session", response_model=SessionResponse)
async def new_session():
    session_token = create_session()
    return SessionResponse(
        session_token=session_token,
        message="New session created successfully"
    )

@app.post("/rate", response_model=RatingResponse)
async def rate_response(request: RatingRequest):
    try:
        # Simple rating logging
        rating_data = {
            "timestamp": datetime.now().isoformat(),
            "message": request.message,
            "response": request.response,
            "rating": request.rating,
            "feedback": request.feedback
        }
        
        # Save to file (in production, use database)
        with open("ratings.json", "a") as f:
            f.write(json.dumps(rating_data) + "\n")
        
        return RatingResponse(
            status="success",
            message="Rating submitted successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/system/status")
async def system_status():
    return {
        "status": "online",
        "active_sessions": len(active_sessions),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/sessions/{session_token}")
async def get_session(session_token: str):
    if session_token in active_sessions:
        return active_sessions[session_token]
    else:
        raise HTTPException(status_code=404, detail="Session not found")

@app.delete("/sessions/{session_token}")
async def delete_session(session_token: str):
    if session_token in active_sessions:
        del active_sessions[session_token]
        return {"status": "success", "message": "Session deleted"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting HR Chatbot API Server...")
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )