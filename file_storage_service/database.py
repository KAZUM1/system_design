import psycopg2
import redis
import json
import os
from hashlib import sha256
from os import getenv
from pymongo import MongoClient


# Подключение к PostgreSQL
DB_PARAMS = {
    "dbname": "file_storage",
    "user": "user",
    "password": "password",
    "host": "db",
    "port": "5432"
}

# Подключение к Redis
REDIS_HOST = getenv("REDIS_HOST", "redis")
REDIS_PORT = int(getenv("REDIS_PORT", 6379))
CACHE_TTL = 300  # Время жизни кэша в секундах (5 минут)
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Подключение к MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://root:example@mongo:27017/file_metadata?authSource=admin")
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client["file_metadata"]
mongo_collection = mongo_db["files"]

def connect():
    return psycopg2.connect(**DB_PARAMS)


# 1. Создание нового пользователя
def create_user(username, password):
    password_hash = sha256(password.encode()).hexdigest()
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT COUNT(*) FROM users WHERE username = %s', (username,))
        if cursor.fetchone()[0] == 0:
            cursor.execute('INSERT INTO users (username, password_hash) VALUES (%s, %s)', (username, password_hash))
            conn.commit()
            print(f"Создан пользователь: {username}")

            # Добавляем пользователя в кэш
            user_data = {"username": username, "password_hash": password_hash}
            redis_client.setex(f"user:{username}", CACHE_TTL, json.dumps(user_data))

        else:
            print(f"Пользователь {username} уже существует.")
    finally:
        cursor.close()
        conn.close()


# 2. Получение пользователя по логину (сквозное чтение с кэшем)
def get_user(username):
    # Проверяем в кэше
    cached_user = redis_client.get(f"user:{username}")
    if cached_user:
        print(f"Получено из кэша: {cached_user}")
        return json.loads(cached_user)

    # Если нет в кэше – читаем из БД
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT username, password_hash FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        if user:
            user_data = {"username": user[0], "password_hash": user[1]}
            # Кэшируем результат
            redis_client.setex(f"user:{username}", CACHE_TTL, json.dumps(user_data))
            print(f"Добавлено в кэш: {user_data}")
            return user_data
        return None
    finally:
        cursor.close()
        conn.close()


# 3. Получение всех пользователей
def get_users():
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT username, password_hash FROM users;")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


# 4. Очистка кэша при удалении или обновлении пользователя
def clear_user_cache(username):
    redis_client.delete(f"user:{username}")

# 4. Создание папки
def create_folder(folder_name, user_id):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO folders (folder_name, user_id)
            VALUES (%s, %s)
            ON CONFLICT (folder_name, user_id) DO NOTHING;
        """, (folder_name, user_id))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

# 5. Получение всех папок пользователя
def get_folders_by_user(user_id):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM folders WHERE user_id = %s', (user_id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

# 6. Создание файла
def create_file(file_name, file_path, folder_name, user_id):
    conn = connect()
    cursor = conn.cursor()
    try:
        # Получаем ID папки
        cursor.execute("SELECT id FROM folders WHERE folder_name = %s AND user_id = %s ORDER BY id LIMIT 1;", 
                       (folder_name, user_id))
        folder = cursor.fetchone()
        if folder is None:
            raise Exception(f"Ошибка: Папка '{folder_name}' не найдена для пользователя {user_id}!")
        folder_id = folder[0]

        # Проверяем, есть ли уже файл
        cursor.execute('SELECT COUNT(*) FROM files WHERE file_name = %s AND folder_id = %s', (file_name, folder_id))
        if cursor.fetchone()[0] == 0:
            cursor.execute('INSERT INTO files (file_name, file_path, folder_id, user_id) VALUES (%s, %s, %s, %s)',
                           (file_name, file_path, folder_id, user_id))
            conn.commit()
        else:
            print(f"Файл {file_name} уже существует.")
    finally:
        cursor.close()
        conn.close()

# 7. Удаление файла
def delete_file(file_name):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM files WHERE file_name = %s', (file_name,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

# 8. Удаление папки
def delete_folder(folder_id):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM files WHERE folder_id = %s", (folder_id,))
        cursor.execute("DELETE FROM folders WHERE id = %s", (folder_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

# 9. Получение информации о файле по имени
def get_file(file_name):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM files WHERE file_name = %s', (file_name,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

# 10. Инициализация базы данных
def init_db():
    conn = connect()
    cursor = conn.cursor()
    
    try:
        # Создание таблиц
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS folders (
                id SERIAL PRIMARY KEY,
                folder_name VARCHAR(255) NOT NULL,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                CONSTRAINT unique_folder_per_user UNIQUE (folder_name, user_id)
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id SERIAL PRIMARY KEY,
                file_name VARCHAR(255) NOT NULL,
                file_path VARCHAR(255) NOT NULL,
                folder_id INTEGER REFERENCES folders(id) ON DELETE CASCADE,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
            );
        """)

        # Вставка тестовых пользователей
        cursor.execute("""
            INSERT INTO users (username, password_hash)
            VALUES 
                ('admin', 'hashed_admin_password'),
                ('user1', 'hashed_user1_password')
            ON CONFLICT (username) DO NOTHING;
        """)

        # Вставка тестовой папки Documents
        cursor.execute("""
            INSERT INTO folders (folder_name, user_id)
            VALUES ('Documents', (SELECT id FROM users WHERE username = 'admin'))
            ON CONFLICT DO NOTHING;
        """)

        # Вставка тестовых файлов
        cursor.execute("""
            INSERT INTO files (file_name, file_path, folder_id, user_id) 
            VALUES
                ('file1.txt', '/uploads/file1.txt', 
                 (SELECT id FROM folders WHERE folder_name = 'Documents' AND user_id = (SELECT id FROM users WHERE username = 'admin') ORDER BY id LIMIT 1), 
                 (SELECT id FROM users WHERE username = 'admin')),

                ('file2.jpg', '/uploads/file2.jpg', 
                 (SELECT id FROM folders WHERE folder_name = 'Documents' AND user_id = (SELECT id FROM users WHERE username = 'admin') ORDER BY id LIMIT 1), 
                 (SELECT id FROM users WHERE username = 'admin'))
            ON CONFLICT DO NOTHING;
        """)

        conn.commit()

    finally:
        cursor.close()
        conn.close()

# Тестирование функций
if __name__ == "__main__":
    init_db()
    
    users = get_users()
    print("Пользователи:", users)

    create_user('new_user', 'new_password')
    print("Новый пользователь:", get_user('new_user'))

    create_folder('New Folder', 1)
    print("Папки пользователя 1:", get_folders_by_user(1))

    create_file('new_file.txt', '/uploads/new_file.txt', 'Documents', 1)
    print("Файл:", get_file('new_file.txt'))

    delete_file('new_file.txt')
    delete_folder(1)
