from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Literal
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os

# Секретный ключ для подписи JWT
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()
    
# Настройка SQLAlchemy
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://stud:stud@db:5432/archdb")
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Модель SQLAlchemy
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    role = Column(String, default="user")
    password = Column(String)
    email = Column(String, unique=True, index=True, nullable=False)

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


# Модель SQLAlchemy
class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    title = Column(String, nullable=False, index=True) 
    author_first_name = Column(String, nullable=False, index=True)  
    author_last_name = Column(String, nullable=False, index=True)  
    author_email = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, default="in check")  
    
    
# Создание таблиц
Base.metadata.create_all(bind=engine)


class ReportCreate(BaseModel):
    title: str
    author_first_name: str
    author_last_name: str
    author_email: EmailStr
    status: Literal["in check", "declined", "accepted"] = "in check"

    class Config:
        orm_mode = True

class ReportResponse(BaseModel):
    id: int
    title: str
    author_first_name: str
    author_last_name: str
    author_email: EmailStr
    status: Literal["in check", "declined", "accepted"]

    class Config:
        orm_mode = True

#Создание доклада
@app.post("/reports", response_model=ReportResponse, tags=["Reports"])
def create_report(report: ReportCreate, db: Session = Depends(get_db)):
    db_report = Report(**report.dict())
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

#Получение всех докладов
@app.get("/reports", response_model=List[ReportResponse], tags=["Reports"])
def get_all_reports(db: Session = Depends(get_db)):
    return db.query(Report).all()

#Получение доклада по id
@app.get("/reports/{report_id}", response_model=ReportResponse, tags=["Reports"])
def get_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

#Получение всех докладов конференции
@app.get("/reports/{conference}", response_model=List[ReportResponse], tags=["Reports"])
def get_report(report_status: Optional[str] = "accepted", db: Session = Depends(get_db)):
    return db.query(Report).filter(Report.status == "accepted").all()

#Добавление доклада в конференцию
@app.post("/reports/{report_id}/{status}", response_model=ReportResponse, tags=["Reports"])
def get_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    report.status = "accepted"
    db.commit()
    db.refresh(report) 
    return report


# Запуск сервера
# http://localhost:8000/openapi.json swagger
# http://localhost:8000/docs портал документации

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)