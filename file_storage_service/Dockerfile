# Используем официальный образ Python с уменьшенным размером
FROM python:3.9-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Устанавливаем pip и зависимости Python
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем оставшиеся файлы проекта
COPY . /app

# Запускаем приложение
CMD ["python", "database.py"]
