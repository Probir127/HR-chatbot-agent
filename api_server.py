"""
api_server.py - FastAPI Server for HR Chatbot with Integrated Authentication
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from typing import List, Optional, Dict, Any
import uuid
import json
import os
from datetime import datetime, timedelta
import jwt
from backend import ask_hr_bot_api

# ==================== CONFIGURATION ====================
SECRET_KEY = "your-secret-key-change-in-production"  # Change in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours
USERS_FILE = "users.json"

# Initialize FastAPI app
app = FastAPI(
    title="HR Chatbot API",
    description="API for Acme AI Ltd. HR Chatbot with Authentication",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# ==================== PYDANTIC MODELS ====================

# Authentication Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    employee_id: Optional[str] = None
    department: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    email: str
    full_name: str
    employee_id: Optional[str]
    department: Optional[str]
    created_at: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Chat Models
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

# ==================== HELPER FUNCTIONS ====================

# User Database Functions
def load_users():
    """Load users from JSON file"""
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    """Save users to JSON file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

# Password Functions
def hash_password(password: str) -> str:
    """Hash a password (truncate to 72 bytes for bcrypt compatibility)"""
    # Bcrypt has a max password length of 72 bytes
    # Truncate to 72 bytes to prevent errors
    password_bytes = password.encode('utf-8')[:72]
    truncated_password = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.hash(truncated_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    # Truncate password to 72 bytes for consistency
    password_bytes = plain_password.encode('utf-8')[:72]
    truncated_password = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.verify(truncated_password, hashed_password)

# JWT Token Functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str):
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Authentication Dependency
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from token"""
    token = credentials.credentials
    payload = decode_token(token)
    email = payload.get("sub")
    
    if email is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    users = load_users()
    if email not in users:
        raise HTTPException(status_code=401, detail="User not found")
    
    user = users[email]
    return UserResponse(
        email=user["email"],
        full_name=user["full_name"],
        employee_id=user.get("employee_id"),
        department=user.get("department"),
        created_at=user["created_at"]
    )

# Session storage
active_sessions = {}

def create_session():
    session_token = str(uuid.uuid4())
    active_sessions[session_token] = {
        "created_at": datetime.now(),
        "chat_history": []
    }
    return session_token

# ==================== ENDPOINTS ====================

@app.get("/")
async def root():
    return {
        "status": "online", 
        "service": "HR Chatbot API with Authentication",
        "version": "2.0.0"
    }

# ==================== AUTHENTICATION ENDPOINTS ====================

@app.post("/auth/register", response_model=Token)
async def register(user_data: UserRegister):
    """Register a new user"""
    try:
        # Validate password length
        if len(user_data.password) > 72:
            raise HTTPException(
                status_code=400, 
                detail="Password must be 72 characters or less"
            )
        
        users = load_users()
        
        # Check if user already exists
        if user_data.email in users:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user
        hashed_password = hash_password(user_data.password)
        user = {
            "email": user_data.email,
            "password": hashed_password,
            "full_name": user_data.full_name,
            "employee_id": user_data.employee_id,
            "department": user_data.department,
            "created_at": datetime.now().isoformat(),
            "is_active": True
        }
        
        users[user_data.email] = user
        save_users(users)
        
        # Create access token
        access_token = create_access_token(data={"sub": user_data.email})
        
        # Return user info and token
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                email=user["email"],
                full_name=user["full_name"],
                employee_id=user["employee_id"],
                department=user["department"],
                created_at=user["created_at"]
            )
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin):
    """Login user and return token"""
    try:
        users = load_users()
        
        # Check if user exists
        if user_data.email not in users:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        user = users[user_data.email]
        
        # Verify password
        if not verify_password(user_data.password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Check if user is active
        if not user.get("is_active", True):
            raise HTTPException(status_code=401, detail="Account is deactivated")
        
        # Create access token
        access_token = create_access_token(data={"sub": user_data.email})
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                email=user["email"],
                full_name=user["full_name"],
                employee_id=user.get("employee_id"),
                department=user.get("department"),
                created_at=user["created_at"]
            )
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@app.post("/auth/verify")
async def verify_user_token(token: str):
    """Verify if token is valid"""
    try:
        payload = decode_token(token)
        email = payload.get("sub")
        
        users = load_users()
        if email not in users:
            return {"valid": False, "user": None}
        
        user = users[email]
        return {
            "valid": True,
            "user": {
                "email": user["email"],
                "full_name": user["full_name"],
                "employee_id": user.get("employee_id"),
                "department": user.get("department")
            }
        }
    except HTTPException:
        return {"valid": False, "user": None}

# ==================== CHAT ENDPOINTS (Protected) ====================

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Protected chat endpoint - requires authentication"""
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
        
        # Update session chat history with user info
        if session_token in active_sessions:
            active_sessions[session_token]["chat_history"].append({
                "user": request.message,
                "bot": bot_response,
                "timestamp": datetime.now().isoformat(),
                "user_email": current_user.email
            })
        
        return ChatResponse(
            response=bot_response,
            session_token=session_token,
            is_new_session=is_new_session
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/new-session", response_model=SessionResponse)
async def new_session(current_user: UserResponse = Depends(get_current_user)):
    """Create new chat session - requires authentication"""
    session_token = create_session()
    return SessionResponse(
        session_token=session_token,
        message="New session created successfully"
    )

@app.post("/rate", response_model=RatingResponse)
async def rate_response(
    request: RatingRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Submit rating - requires authentication"""
    try:
        # Simple rating logging with user info
        rating_data = {
            "timestamp": datetime.now().isoformat(),
            "message": request.message,
            "response": request.response,
            "rating": request.rating,
            "feedback": request.feedback,
            "user_email": current_user.email,
            "user_name": current_user.full_name
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

# ==================== SYSTEM ENDPOINTS ====================

@app.get("/system/status")
async def system_status():
    return {
        "status": "online",
        "active_sessions": len(active_sessions),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/sessions/{session_token}")
async def get_session(
    session_token: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get session details - requires authentication"""
    if session_token in active_sessions:
        return active_sessions[session_token]
    else:
        raise HTTPException(status_code=404, detail="Session not found")

@app.delete("/sessions/{session_token}")
async def delete_session(
    session_token: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete session - requires authentication"""
    if session_token in active_sessions:
        del active_sessions[session_token]
        return {"status": "success", "message": "Session deleted"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

if __name__ == "__main__":
    import uvicorn
    print(" Starting HR Chatbot API Server with Authentication...")
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
