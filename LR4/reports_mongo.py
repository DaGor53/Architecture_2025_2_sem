from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pymongo import MongoClient
from pydantic import BaseModel
import os

client = MongoClient(host=['mongodb:27017'])

db = client['arch']

collection = db['reports']
collection.create_index("id", unique=True)

class ReportMeta(BaseModel):
    id: str
    title: str
    author: str

app = FastAPI()

#Список CRUD-операций

@app.post("/upload-report/", response_model=ReportMeta)
async def upload_report(
    id: str = Form(...),
    title: str = Form(...),
    author: str = Form(...),
    file: UploadFile = File(...)
):
    if not file.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="Файл должен быть в формате .docx")

    content = await file.read()

    if len(content) > 16 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Файл слишком большой (макс. 16 МБ)")

    report_doc = {
        "id": id,
        "title": title,
        "author": author,
        "filename": file.filename,
        "content": content 
    }

    collection.insert_one(report_doc)
    return ReportMeta(id=id, title=title, author=author)

@app.get("/download-report/{report_id}")
def download_report(report_id: str):
    report = collection.find_one({"id": report_id})
    if not report:
        raise HTTPException(status_code=404, detail="Доклад не найден")

    download_folder = os.path.join("/app", "downloads")
    os.makedirs(download_folder, exist_ok=True)

    file_path = os.path.join(download_folder, report['filename'])

    with open(file_path, "wb") as f:
        f.write(report["content"])

    return {"message": "Файл сохранён", "filename": report['filename'],"saved_to": file_path}


@app.get("/download-all-reports")
def download_all_reports():
    
    download_folder = os.path.join("/app", "downloads")
    os.makedirs(download_folder, exist_ok=True)

    reports_cursor = collection.find({}, {"_id": 0, "id": 1, "title": 1, "author": 1, "filename": 1, "content": 1})
    
    for report in reports_cursor:
        try:
            file_path = os.path.join(download_folder, report['filename'])
            with open(file_path, "wb") as f:
                f.write(report["content"])
            print(f"Файл {file_path} сохранён.")
        except Exception as e:
            print(f"Ошибка при сохранении файла {report['filename']}: {e}")

    return {"message": "Все файлы сохранены"}


@app.delete("/delete-report/{report_id}")
def delete_report(report_id: str):
    report = collection.find_one({"id": report_id})
    if not report:
        raise HTTPException(status_code=404, detail="Доклад не найден")
    collection.delete_one({"id": report_id})
    return {"message": f"Доклад с id {report_id} удалён"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

