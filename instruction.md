# Инструкция по проверке кода

## Запуск проекта
Перед началом проверки убедитесь, что у вас установлен **Docker** и **Docker Compose**. Для запуска выполните:

```bash
docker-compose up -d
```

Затем можно открыть **Swagger UI** для тестирования API:

```
http://localhost:8000/docs
```

---

# Лабораторная работа 2
### 1. Создание сервиса (микросервисная архитектура)  
- `user_service.py` — сервис управления пользователями.  
- `file_service.py` — сервис управления файлами.  
- `main.py` — основная точка входа FastAPI, объединяет сервисы.
---

### 2. Аутентификация с JWT-токеном  
- `auth.py` — генерация и валидация JWT.  
- `user_service.py` — логин и регистрация пользователей.  
- `requirements.txt` — библиотека `python-jose[cryptography]` для JWT.
---

### 3. Поддержка GET/POST методов  
**Где реализовано:**  
- `user_service.py` (создание, поиск пользователей).  
- `file_service.py` (загрузка, удаление файлов).  
---

### 4. Данные хранятся в памяти  
**Где реализовано:**  
- `user_service.py` (`users_db: Dict[str, dict]`).  
- `file_service.py` (`files_db`, `folders_db` для временного хранения).  
---

### 5. Мастер-пользователь (admin/secret)  
**Где реализовано:**  
- `user_service.py` (добавляется вручную в коде).  
---

# Лабораторная работа 3
### 6. Данные хранятся в PostgreSQL  
**Где реализовано:**  
- `database.py` (подключение к БД).  
- `init.sql` (создание схемы).  
---

### 7. Созданы таблицы для каждой сущности  
- `init.sql` (таблицы `users`, `folders`, `files`).
---

### 8. Скрипт создания БД и тестовых данных  
- `init.sql` создает БД и добавляет пользователей, файлы, папки.

---

### 9. CRUD-запросы к БД  
- `file_service.py` (добавление/удаление файлов, поиск по имени).  
- `user_service.py` (CRUD для пользователей).  

---

### 10. Логины и пароли (хранение хэша)  
- `auth.py` (bcrypt-хэширование).  
---

### 11. Индексирование в PostgreSQL  
- `init.sql` (индексы на `username`, `folder_id`, `file_name`).
---

# Лабораторная работа 4
### 12. Одна из сущностей хранится в MongoDB  
- `file_service.py` (файлы хранятся в `file_metadata` в MongoDB).  
---

### 13. Создание и чтение документа в MongoDB
- `file_service.py` (добавление и поиск файлов в MongoDB.)
---

### 14. Индексирование данных в MongoDB
- `file_service.py` (индекс для быстрого поиска файлов по filename)
---
### 16. Реализация паттерна "сквозное чтение"
- `file_service.py` (Данные сначала ищутся в Redis, затем в MongoDB.)

# Лабораторная работа 5
### 15. Кэширование сущности (PostgreSQL → Redis)  
**Где реализовано:**  
- `user_service.py`, `file_service.py` (используется `redis_client`).  
---

# Лабораторная работа 6
### 17. Реализован CQRS  
**Где реализовано:**  
- **Команда (Command)**: `file_service.py` записывает файлы в Kafka.  
- **Запрос (Query)**: `kafka_consumer.py` читает из Kafka и сохраняет в MongoDB.  
---

# Дополнительные функции
- **Swagger UI:** `http://localhost:8000/docs`
- **Kafka UI:** `http://localhost:8888`
- **Просмотр файлов:** `http://localhost:8000/files/{file_id}`
