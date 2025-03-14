# Используем базовый образ с Python 3.11 (или нужную версию)
FROM python:3.12

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Запускаем бота при старте контейнера
CMD ["python", "main.py"]
