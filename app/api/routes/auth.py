from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime

from app.schemas.user import CreateUser, ReturnData, Token
from app.services import auth as auth_service
from app.db.database import users_list

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/signup", response_model=ReturnData, status_code=status.HTTP_201_CREATED)
def signup(payload: CreateUser):
    existing = auth_service.get_user_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    hashed_pw = auth_service.hash_password(payload.password)
    doc = {"name": payload.name, "email": payload.email, "password": hashed_pw, "created_at": datetime.now()}
    res = users_list.insert_one(doc)
    return {"id": str(res.inserted_id), "name": payload.name, "email": payload.email}

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth_service.get_user_by_email(form_data.username)
    if not user or not auth_service.verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas", headers={"WWW-Authenticate": "Bearer"})
    token = auth_service.create_access_token(subject=str(user["_id"]))
    return {"access_token": token, "token_type": "bearer"}

@router.get("/profile", response_model=ReturnData)
def me(current_user = Depends(auth_service.get_current_user)):
    return current_user