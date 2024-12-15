from ultralytics import YOLO
import cv2
import matplotlib.pyplot as plt
import os
from PIL import Image, ImageFilter, ImageDraw, ImageFont
from telegram.ext import Application, CommandHandler, MessageHandler, filters


# Функция для отображения изображения
def show_image(image, title="Image"):
    plt.figure(figsize=(10, 10))
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.title(title)
    plt.axis('off')
    plt.show()


# Функция для распознавания объектов на изображении
def detect_waste(image_path, model_path="yolov5s.pt"):
    # Загрузка модели YOLO (можно использовать предобученную или кастомную)
    model = YOLO(model_path)

    # Загрузка изображения
    image = cv2.imread(image_path)
    if image is None:
        print("Ошибка: изображение не найдено!")
        return

    # Применяем модель для распознавания объектов
    results = model(image)

    # Отображаем результаты
    annotated_image = results[0].plot()
    return annotated_image
    #show_image(annotated_image, title="Detected Objects")

    # Выводим результаты в консоль
    for result in results[0].boxes:
        class_id = int(result.cls)
        confidence = result.conf
        box = result.xyxy
        #print(f"Класс: {model.names[class_id]} | Доверие: {confidence:.2%} | Координаты (X1, Y1, X2, Y2): {box.tolist()}")
        #print(f"Объект: {model.names[class_id]}, Доверие: {confidence:.2f}, Координаты: {box}")



# Команда /start
async def start(update, context):
    user_id = update.effective_chat.id
    await update.message.reply_text(
        "Привет! Я бот для обмена фотографиями. Отправьте фото, чтобы получить обработанную версию!"
    )

# Обработка фото
async def handle_photo(update, context):
    user_id = update.effective_chat.id
    photo_file = await update.message.photo[-1].get_file()
    original_file_path = f"photos/{user_id}_photo.jpg"
    processed_file_path = f"photos/{user_id}_photo_processed.jpg"

    # Создаем папку для сохранения, если её нет
    os.makedirs("photos", exist_ok=True)

    # Скачиваем оригинал
    await photo_file.download_to_drive(original_file_path)

    # Обрабатываем фото
    process_photo(original_file_path, processed_file_path)
    

    # Отправляем обработанное фото обратно
    await context.bot.send_photo(chat_id=user_id, photo=open(processed_file_path, "rb"))
    await update.message.reply_text("Ваше обработанное фото готово!")

# Функция обработки фотографии
def process_photo(input_path, output_path):
    with Image.open(input_path) as img:
        # Пример обработки: добавление размытия и текста
        img = detect_waste(input_path,model_path ="runs/detect/train6/weights/best.pt")  # Применяем фильтр размытия


        # Сохраняем обработанное изображение
        img.save(output_path)

# Команда /stop
async def stop(update, context):
    user_id = update.effective_chat.id
    await update.message.reply_text("Вы завершили сессию.")

# Главная функция
def main():
    # Замените 'YOUR_TOKEN' на токен вашего бота
    TOKEN = "7539936945:AAEniNlf-c-Ag8JZ3RwsOSJQYlNV1XJC-5o"

    # Создаем приложение
    application = Application.builder().token(TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()
