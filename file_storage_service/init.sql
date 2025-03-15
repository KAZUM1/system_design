CREATE DATABASE file_storage;
\c file_storage;

-- Создание таблицы пользователей
CREATE TABLE IF NOT EXISTS folders (
    id SERIAL PRIMARY KEY,
    folder_name VARCHAR(255) NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT unique_folder_per_user UNIQUE (folder_name, user_id)
);


-- Добавление пользователей
INSERT INTO users (username, password) VALUES
('admin', 'secret'),
('user1', 'password1');

-- Создание таблицы папок
CREATE TABLE IF NOT EXISTS folders (
    id SERIAL PRIMARY KEY,
    folder_name VARCHAR(255) NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
);

-- Добавление папок для пользователей
INSERT INTO folders (folder_name, user_id)
VALUES
    ('Documents', 1),
    ('Photos', 2);

-- Создание таблицы файлов
CREATE TABLE IF NOT EXISTS files (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    folder_id INTEGER REFERENCES folders(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
);

-- Добавление файлов в папки
INSERT INTO files (file_name, file_path, folder_id, user_id)
VALUES
    ('file1.txt', '/uploads/file1.txt', 1, 1),
    ('file2.jpg', '/uploads/file2.jpg', 2, 2);

-- Индексирование
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_folders_folder_name ON folders(folder_name);
CREATE INDEX IF NOT EXISTS idx_files_file_name ON files(file_name);

ALTER TABLE users ADD CONSTRAINT unique_username UNIQUE (username);
ALTER TABLE folders ADD CONSTRAINT unique_folder_per_user UNIQUE (folder_name, user_id);
ALTER TABLE files ADD CONSTRAINT unique_file_per_folder UNIQUE (file_name, folder_id);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_folders_user_id ON folders(user_id);
CREATE INDEX idx_files_folder_id ON files(folder_id);
CREATE INDEX idx_files_user_id ON files(user_id);

