# Dockerfile — инструкция для сборки Docker образа backend
# Используем официальный лёгкий Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
# --no-cache-dir уменьшает размер образа
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь backend код
COPY . .

# Открываем порт 8000 (FastAPI по умолчанию)
EXPOSE 8000

# Команда запуска сервера
# --host 0.0.0.0 важен — иначе контейнер не будет доступен снаружи
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
