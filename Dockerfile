# Базовый образ Python
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем watchdog для отслеживания изменений
RUN pip install watchdog

# Копируем код приложения
COPY . .

# Запуск через watchdog для отслеживания изменений
CMD ["watchmedo", "auto-restart", "--directory=.", "--pattern=*.py", "--", "python", "main.py"]
