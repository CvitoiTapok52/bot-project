# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем необходимые системные пакеты
RUN apt-get update && apt-get install -y libgl1-mesa-glx

# Устанавливаем зависимости
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Указываем команду для запуска
CMD ["python", "bot.py"]

