import os
import cv2
from PIL import Image
from ultralytics import YOLO
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import uvicorn

# Список подписчиков
subscribers = set()

# Состояния для ConversationHandler
WAITING_FOR_ADDRESS = range(1)

# Временное хранилище фото и адресов
user_data = {}

# Функция для распознавания объектов на изображении
def detect_waste(image_path, model_path="runs/detect/train6/weights/best.pt"):
    model = YOLO(model_path)
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError("Ошибка: изображение не найдено!")

    results = model(image)
    if len(results[0].boxes) == 0:
        return None

    annotated_image = results[0].plot()
    temp_path = image_path.replace(".jpg", "_temp.jpg")
    cv2.imwrite(temp_path, annotated_image)
    return temp_path

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот для помощи в обнаружении и сообщении о мусоре.\n\n"
        "Отправьте фото, чтобы я мог распознать мусор, и укажите адрес, где он был найден. "
        "Ваши сообщения будут отправлены подписчикам. Чтобы узнать больше, введите /help."
    )

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 **Доступные команды:**\n\n"
        "/start - Начало работы с ботом.\n"
        "/help - Просмотр доступных команд и описания.\n"
        "/subscribe - Подписаться на уведомления о найденном мусоре.\n"
        "/unsubscribe - Отписаться от уведомлений.\n"
        "/stop - Остановить текущий процесс и отписаться от уведомлений.\n"
        "/cancel - Отменить процесс указания адреса.\n\n"
        "Отправьте фото, чтобы я обработал его и нашел мусор. После этого введите адрес места обнаружения."
    )

# Команда /subscribe
async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    if user_id not in subscribers:
        subscribers.add(user_id)
        await update.message.reply_text("Вы подписались на уведомления о найденном мусоре.")
    else:
        await update.message.reply_text("Вы уже подписаны на уведомления.")

# Команда /unsubscribe
async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    if user_id in subscribers:
        subscribers.remove(user_id)
        await update.message.reply_text("Вы отписались от уведомлений.")
    else:
        await update.message.reply_text("Вы не были подписаны на уведомления.")

# Команда /stop
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    if user_id in subscribers:
        subscribers.remove(user_id)
    if user_id in user_data:
        del user_data[user_id]
    await update.message.reply_text(
        "Все процессы остановлены. Вы также отписаны от уведомлений.\n"
        "Если захотите вернуться, используйте /start."
    )

# Обработка фото
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    photo_file = await update.message.photo[-1].get_file()
    original_file_path = f"photos/{user_id}_photo.jpg"

    os.makedirs("photos", exist_ok=True)
    await photo_file.download_to_drive(original_file_path)

    user_data[user_id] = {"photo_path": original_file_path}

    await update.message.reply_text(
        "Фото успешно загружено! Теперь отправьте адрес, где был найден мусор, или введите /cancel для отмены."
    )

    return WAITING_FOR_ADDRESS

# Обработка адреса
async def handle_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    address = update.message.text

    if user_id not in user_data:
        await update.message.reply_text("Пожалуйста, сначала отправьте фото.")
        return ConversationHandler.END

    photo_path = user_data[user_id].get("photo_path")
    processed_file_path = f"photos/{user_id}_photo_processed.jpg"

    try:
        annotated_image_path = detect_waste(
            image_path=photo_path,
            model_path="runs/detect/train6/weights/best.pt"
        )

        if annotated_image_path is None:
            await update.message.reply_text("Мусор не найден на изображении. Спасибо за чистоту!")
        else:
            if os.path.exists(processed_file_path):
                os.remove(processed_file_path)
            os.rename(annotated_image_path, processed_file_path)

            await context.bot.send_photo(chat_id=user_id, photo=open(processed_file_path, "rb"))
            await update.message.reply_text("Ваше обработанное фото готово!")

            for subscriber_id in subscribers:
                try:
                    await context.bot.send_message(
                        chat_id=subscriber_id,
                        text=f"Мусор найден по адресу: {address}"
                    )
                    await context.bot.send_photo(
                        chat_id=subscriber_id,
                        photo=open(processed_file_path, "rb")
                    )
                except Exception as e:
                    print(f"Ошибка отправки уведомления {subscriber_id}: {e}")

    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка при обработке фото: {e}")

    del user_data[user_id]
    return ConversationHandler.END

# Команда отмены
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    if user_id in user_data:
        del user_data[user_id]
    await update.message.reply_text("Вы отменили процесс отправки адреса.")
    return ConversationHandler.END

# Главная функция
def main():
    TOKEN = "7539936945:AAEniNlf-c-Ag8JZ3RwsOSJQYlNV1XJC-5o"
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.PHOTO, handle_photo)],
        states={
            WAITING_FOR_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_address)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("subscribe", subscribe))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(conv_handler)

    application.run_polling()

if __name__ == "__main__":
    # Запуск с помощью uvicorn (для Render)
    uvicorn.run(main, host="0.0.0.0", port=5000)







