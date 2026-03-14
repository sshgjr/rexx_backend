import json
from typing import Optional, List

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from database import Base, engine, get_db
from auth import (
    User,
    hash_password,
    verify_password,
    create_access_token,
    get_user_by_email,
    get_current_user,
)

# =========================
# 환경변수 로드
# =========================
load_dotenv()

# =========================
# FastAPI 앱
# =========================
app = FastAPI()

# Flutter에서 접근 가능하게 CORS 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB 테이블 생성
Base.metadata.create_all(bind=engine)

# =========================
# Pydantic 스키마
# =========================
class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    height: Optional[float] = None
    weight: Optional[float] = None
    is_body_public: Optional[bool] = False
    interests: Optional[List[str]] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    height: Optional[float] = None
    weight: Optional[float] = None
    is_body_public: bool = False
    interests: Optional[List[str]] = None

class AuthResponse(BaseModel):
    success: bool
    token: str
    user: UserResponse

class MeResponse(BaseModel):
    success: bool
    user: UserResponse

def _user_response(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "height": user.height,
        "weight": user.weight,
        "is_body_public": user.is_body_public,
        "interests": json.loads(user.interests) if user.interests else None,
    }

# =========================
# 테스트용 라우트
# =========================
@app.get("/")
def root():
    return {"message": "FastAPI server is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

# =========================
# 회원가입
# =========================
@app.post("/register", response_model=AuthResponse)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db, data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")

    new_user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
        height=data.height,
        weight=data.weight,
        is_body_public=data.is_body_public if data.is_body_public is not None else False,
        interests=json.dumps(data.interests) if data.interests else None,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(data={"sub": new_user.email})
    return {"success": True, "token": access_token, "user": _user_response(new_user)}

# =========================
# 로그인
# =========================
@app.post("/login", response_model=AuthResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 틀렸습니다.")

    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 틀렸습니다.")

    access_token = create_access_token(data={"sub": user.email})

    return {
        "success": True,
        "token": access_token,
        "user": _user_response(user),
    }

# =========================
# 내 정보 조회
# =========================
@app.get("/me", response_model=MeResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "success": True,
        "user": _user_response(current_user),
    }

# =========================
# 자세 평가 라우터
# =========================
from routers.pose_feedback import router as pose_router, limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.include_router(pose_router)
