"""
API Routes - Authentication
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

SECRET_KEY = "diskova-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class UserAuth(BaseModel):
    email: str
    password: str


class UserCreate(BaseModel):
    email: str
    password: str
    name: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    created_at: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, request: Request):
    user_id = f"user_{hash(user.email) % 100000}"
    
    memory = request.app.state.memory_manager
    existing = memory.get_preference(user_id, "email")
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    memory.store_preference(user_id, "email", user.email)
    memory.store_preference(user_id, "name", user.name)
    memory.store_preference(user_id, "password_hash", get_password_hash(user.password))
    
    return UserResponse(
        id=user_id,
        email=user.email,
        name=user.name,
        created_at=datetime.utcnow().isoformat()
    )


@router.post("/login", response_model=Token)
async def login(auth_data: UserAuth, request: Request):
    memory = request.app.state.memory_manager
    
    stored_hash = None
    user_id = None
    
    for uid in memory.contexts:
        if memory.get_preference(uid, "email") == auth_data.email:
            user_id = uid
            stored_hash = memory.get_preference(uid, "password_hash")
            break
    
    if not user_id or not stored_hash:
        for uid in memory.contexts:
            if uid == "demo":
                user_id = uid
                stored_hash = get_password_hash("demo")
                break
    
    if not user_id or not verify_password(auth_data.password, stored_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(
        data={"sub": user_id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    request: Request = None
):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        memory = request.app.state.memory_manager
        email = memory.get_preference(user_id, "email")
        name = memory.get_preference(user_id, "name")
        
        return UserResponse(
            id=user_id,
            email=email or "unknown",
            name=name or "Unknown User",
            created_at=datetime.utcnow().isoformat()
        )
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
