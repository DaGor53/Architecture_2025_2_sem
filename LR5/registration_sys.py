from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import List, Optional, Literal
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from sqlalchemy import func

import redis
import json

REDIS_URL = os.getenv("REDIS_URL", "redis://cache:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# Секретный ключ для подписи JWT
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

# Зависимости для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Настройка паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Настройка OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Зависимости для получения текущего пользователя
async def get_current_client(token: str = Depends(oauth2_scheme)):
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
        else:
            return username
    except JWTError:
        raise credentials_exception

# Создание и проверка JWT токенов
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Маршрут для получения токена
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Поиск пользователя в базе данных
    user = db.query(User).filter(User.email == form_data.username).first()
    
    # Проверка, существует ли такой пользователь
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Проверка пароля
    if not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Создание токена
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": form_data.username}, expires_delta=access_token_expires)
    
    return {"access_token": access_token, "token_type": "bearer"}
    
    
# Настройка SQLAlchemy
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://stud:stud@db:5432/archdb")
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Модель SQLAlchemy
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    role = Column(String, default="user")
    password = Column(String)
    email = Column(String, unique=True, index=True, nullable=False)
    
Base.metadata.create_all(bind=engine)


# Модель Pydantic для валидации данных
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    role: Literal["user", "admin"] = "user"  # по умолчанию "user"
    password: str  # вводимый пользователем пароль
    email: EmailStr  # типизируем как email

class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    role: str  # возвращаем также роль
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)
        
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

#Маршрут для создания пользователя
@app.post("/users/", response_model=UserResponse, tags=["Users"])
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = hash_password(user.password)
    db_user = User(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    user_data = UserResponse.model_validate(db_user).model_dump()
    redis_client.set(f"user:{db_user.id}", json.dumps(user_data), ex=180)

    return db_user

# Маршрут для получения пользователя по id
@app.get("/users/{user_id}", response_model=UserResponse, tags=["Users"])
def get_user(user_id: int, db: Session = Depends(get_db)):
    cache_key = f"user:{user_id}"
    if redis_client.exists(cache_key):
        cached_user = redis_client.get(cache_key)
        return json.loads(cached_user)

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_data = UserResponse.model_validate(user).model_dump()
    redis_client.set(cache_key, json.dumps(user_data), ex=180)
    return user_data
    #return user

# Маршрут для получения всех пользователей
@app.get("/users/", response_model=list[UserResponse], tags=["Users"])
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


# Маршрут для получения пользователя по логину (требует аутентификации)
@app.get("/users/login/{login}", response_model=UserResponse)
def get_user_by_login(login: str, current_user: str = Depends(get_current_client), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Маршрут для получения пользователей по маске имя+фамилия (требует аутентификации)
@app.get("/users/mask/{mask}", response_model=List[UserResponse])
def get_users_by_mask(mask: str, current_user: str = Depends(get_current_client), db: Session = Depends(get_db)):
    users = db.query(User).filter(
        func.concat(User.first_name, " ", User.last_name).like(f"%{mask}%")
    ).all()
    if not users:
        raise HTTPException(status_code=404, detail="Users not found")
    return users

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Запуск сервера
# http://localhost:8000/openapi.json swagger
# http://localhost:8000/docs портал документации

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

