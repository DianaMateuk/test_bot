# Базовый образ
FROM python:3.11-slim

# Рабочая директория
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходники
COPY . .

# Указываем .env (если он в том же каталоге)

# Запускаем бота
CMD ["python", "bot.py"]
