from fastapi import FastAPI, Depends
import uvicorn
from auth import router as auth_router
from user_service import router as user_router
from file_service import router as file_router
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="File Management System")

app.mount("/static", StaticFiles(directory="static"), name="static")
# Подключаем роутеры
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(file_router, prefix="/files", tags=["Files"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешает запросы со всех источников (лучше указать конкретные)
    allow_credentials=True,
    allow_methods=["*"],  # Разрешает все методы (GET, POST и т. д.)
    allow_headers=["*"],  # Разрешает все заголовки
)

# Запуск сервера
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
