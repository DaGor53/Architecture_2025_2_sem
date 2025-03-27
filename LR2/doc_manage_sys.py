from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

# Секретный ключ для подписи JWT
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

class Report(BaseModel):
    id: int
    title: str
    author: str
    abstract: str  

# Временное хранилище для пользователей
reports_db: Dict[int, Report] = {}
conference_reports_db: set = set()



# Псевдо-база данных пользователей
client_db = {
    "admin":  "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"  # hashed "secret"
}

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
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    password_check = False
    if form_data.username in client_db:
        password = client_db[form_data.username]
        print(f"Password retrieved for {form_data.username}: {password}")
        print(f"Type of password: {type(password)}") 
        print(f"form_data.password = {form_data.password}")
        print(f"Type of form_data.password = {type(form_data.password)}")
        if pwd_context.verify(form_data.password, password):
            password_check = True

    if password_check:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": form_data.username}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    

# POST - Создание доклада
@app.post("/reports", response_model=Report)
def create_report(report: Report, current_user: str = Depends(get_current_client)):
    if report.id in reports_db:
        raise HTTPException(status_code=400, detail="Report ID already exists")
    reports_db[report.id] = report
    return report

# GET - Получение списка всех докладов
@app.get("/reports", response_model=List[Report])
def get_all_reports(current_user: str = Depends(get_current_client)):
    return list(reports_db.values())

# POST - Добавление доклада в конференцию
@app.post("/conference/reports/{report_id}")
def add_report_to_conference(report_id: int, current_user: str = Depends(get_current_client)):
    if report_id not in reports_db:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if report_id in conference_reports_db:
        raise HTTPException(status_code=400, detail="Report already added to this conference")

    conference_reports_db.add(report_id)
    return {"message": "Report added to conference successfully"}

# GET - Получение списка докладов в конференции
@app.get("/conference/reports", response_model=List[Report])
def get_reports_in_conference(current_user: str = Depends(get_current_client)):

    report_ids = conference_reports_db
    reports = [reports_db[rep_id] for rep_id in report_ids]
    return reports


# Запуск сервера
# http://localhost:8000/openapi.json swagger
# http://localhost:8000/docs портал документации

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)