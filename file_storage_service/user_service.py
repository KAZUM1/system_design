from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict
from auth import hash_password, verify_password, create_access_token
import redis
import json
import os

router = APIRouter()

# Подключение к Redis
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

# Временное хранилище пользователей (в памяти)
users_db: Dict[str, dict] = {
    "admin": {
        "username": "admin",
        "full_name": "Master Admin",
        "hashed_password": hash_password("secret"),
        "role": "admin"
    }
}

# Модели данных
class UserCreate(BaseModel):
    username: str
    full_name: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

# Регистрация нового пользователя
@router.post("/register")
def register(user: UserCreate):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

    user_data = {
        "username": user.username,
        "full_name": user.full_name,
        "hashed_password": hash_password(user.password),
        "role": "user"
    }
    
    users_db[user.username] = user_data
    
    # Кешируем пользователя в Redis
    redis_client.set(f"user:{user.username}", json.dumps(user_data), ex=600)  # 10 минут

    return {"message": "Пользователь зарегистрирован!"}


# Аутентификация пользователя
@router.post("/login")
def login(user: UserLogin):
    db_user = users_db.get(user.username)
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Неверные учетные данные")

    token = create_access_token({"sub": user.username, "role": db_user["role"]})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/users/{username}")
def get_user(username: str):
    # Сначала ищем в кэше Redis
    cached_user = redis_client.get(f"user:{username}")
    if cached_user:
        return json.loads(cached_user)

    # Если нет в кэше, ищем в БД (здесь просто в памяти)
    user = users_db.get(username)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Кешируем пользователя
    redis_client.set(f"user:{username}", json.dumps(user), ex=600)

    return user

