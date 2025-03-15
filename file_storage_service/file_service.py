from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from pydantic import BaseModel
from typing import Dict
from kafka import KafkaProducer
import shutil
import os
import redis
import json

class FileMetadata(BaseModel):
    filename: str
    size: int
    filetype: str

# Подключение к MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://root:example@mongo:27017/file_metadata?authSource=admin")
client = MongoClient(MONGO_URI)
db = client["file_metadata"]
files_collection = db["files"]

# Создание индекса для поиска файлов по имени
files_collection.create_index("filename")

# Подключение к Redis
REDIS_HOST = os.getenv("REDIS_HOST", "redis")  # По умолчанию "redis" для Docker
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Подключение к Kafka
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "file_events")
kafka_producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER],
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

router = APIRouter()
app = FastAPI()

# Временное хранилище файлов и папок
files_db: Dict[str, str] = {}
folders_db: Dict[str, str] = {}

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

### 📂 Папки ###
@router.post("/folders")
async def create_folder(folder_name: str):
    folder_path = os.path.join(UPLOAD_DIR, folder_name)
    if os.path.exists(folder_path):
        raise HTTPException(status_code=400, detail="Папка уже существует")
    os.makedirs(folder_path)
    folders_db[folder_name] = folder_path
    return {"message": "Папка создана", "folder": folder_name}

@router.get("/folders")
async def list_folders():
    return {"folders": list(folders_db.keys())}

@router.delete("/folders/{folder_name}")
async def delete_folder(folder_name: str):
    folder_path = folders_db.get(folder_name)
    if not folder_path or not os.path.exists(folder_path):
        raise HTTPException(status_code=404, detail="Папка не найдена")
    shutil.rmtree(folder_path)
    del folders_db[folder_name]
    return {"message": "Папка удалена"}

### 📁 Файлы ###
@router.post("/files/{folder_name}")
async def upload_file(folder_name: str, file: UploadFile = File(...)):
    folder_path = os.path.join(UPLOAD_DIR, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    file_location = os.path.join(folder_path, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Отправка события в Kafka
# Публикуем событие в Kafka (команда на создание файла)
    file_event = {
        "filename": file.filename,
        "path": file_location,
        "folder": folder_name
    }
    kafka_producer.send(KAFKA_TOPIC, file_event)
    kafka_producer.flush()
    print(f"[Kafka Producer] Отправлено событие: {file_event}")
    
    # Здесь мы не записываем данные напрямую в MongoDB и Redis,
    # так как ответственность за запись берет на себя отдельный сервис (Consumer)
    return {"message": "Файл загружен, событие отправлено в Kafka", "filename": file.filename}

@router.get("/files/{file_id}")
async def get_file(file_id: str):
    # Проверка кеша Redis
    cached_path = redis_client.get(file_id)
    if cached_path:
        return {"filename": file_id, "path": cached_path, "source": "cache"}

    # Проверка в MongoDB
    file_metadata = files_collection.find_one({"filename": file_id})
    if not file_metadata:
        raise HTTPException(status_code=404, detail="Файл не найден")

    # Кеширование пути файла в Redis
    redis_client.setex(file_id, 3600, file_metadata["path"])
    
    return {"filename": file_id, "path": file_metadata["path"], "source": "db"}

@router.delete("/files/{file_id}")
async def delete_file(file_id: str):
    file_metadata = files_collection.find_one({"filename": file_id})
    
    if not file_metadata:
        raise HTTPException(status_code=404, detail="Файл не найден")

    os.remove(file_metadata["path"])
    files_collection.delete_one({"filename": file_id})

    # Удаление файла из кеша Redis
    redis_client.delete(file_id)

    return {"message": "Файл удален"}

### 🧪 Тест кеша Redis ###
@app.get("/cache_test")
def cache_example():
    redis_client.set("cache_test", "FastAPI + Redis")
    return {"cached_value": redis_client.get("cache_test")}

### 📡 Загрузка файлов ###
@app.post("/files/files/{folder}")
async def upload_file(folder: str, file: UploadFile = File(...)):
    return {"filename": file.filename, "folder": folder}

### 🔎 Получение файла по имени (исправленный) ###
@app.get("/files/files/{file_id}")
async def get_file_from_storage(file_id: str):
    file_metadata = files_collection.find_one({"filename": file_id})
    if file_metadata and os.path.exists(file_metadata["path"]):
        return FileResponse(file_metadata["path"], media_type="application/octet-stream", filename=file_id)
    return JSONResponse(status_code=404, content={"message": "File not found"})

app.include_router(router)
