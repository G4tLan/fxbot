import os
import signal
import time
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from engine.models.core import User

router = APIRouter()

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = User.get_or_none(User.username == username)
    if user is None:
        raise credentials_exception
    return user

@router.post("/auth/register")
async def register(request: RegisterRequest):
    # Check if user exists
    if User.select().where(User.username == request.username).exists():
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(request.password)
    User.create(
        username=request.username,
        password_hash=hashed_password,
        email=request.email,
        created_at=int(time.time())
    )
    return {"message": "User created successfully"}

@router.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = User.get_or_none(User.username == form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/auth/shutdown")
async def shutdown(current_user: User = Depends(get_current_user)):
    os.kill(os.getpid(), signal.SIGINT)
    return {"message": "Shutting down..."}

@router.post("/auth/terminate-all")
async def terminate_all(current_user: User = Depends(get_current_user)):
    return {"message": "All background tasks terminated"}

@router.post("/auth/engine-trade-token")
async def engine_trade_token(current_user: User = Depends(get_current_user)):
    return {"token": "mock-engine-trade-token"}
