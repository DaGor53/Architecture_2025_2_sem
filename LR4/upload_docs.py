import time
from pymongo import MongoClient
import os

time.sleep(5)

client = MongoClient(host=['mongodb:27017'])

db = client['arch']

collection = db['reports']
collection.create_index("id", unique=True)

FILES = [
    {"id": "2", "title": "Advances in AI and Machine Learning", "author": "William Norman", "filename": "test0.docx"},
    {"id": "3", "title": "Cybersecurity in the Age of IoT", "author": "Julian Edmonds", "filename": "test1.docx"},
]

def upload_files():

    for file_info in FILES:
        filepath = file_info["filename"]
        if not os.path.exists(filepath):
            print(f"Файл {filepath} не найден.")
            continue

        with open(filepath, "rb") as f:
            content = f.read()

        if len(content) > 16 * 1024 * 1024:
            print(f"Файл {filepath} слишком большой (макс. 16 МБ)")
            continue

        report_doc = {
            "id": file_info["id"],
            "title": file_info["title"],
            "author": file_info["author"],
            "filename": filepath,
            "content": content
        }

        collection.insert_one(report_doc)
        print(f"Загружен файл: {filepath}")

if __name__ == "__main__":
    upload_files()