
from ultralytics import YOLO
import cv2
import matplotlib.pyplot as plt

# Функция для отображения изображения
def show_image(image, title="Image"):
    plt.figure(figsize=(10, 10))
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.title(title)
    plt.axis('off')
    plt.show()

# Функция для обучения модели
def train_model(data_yaml, model_path="yolov5s.pt", epochs=50, imgsz=640):
    # Загрузка модели
    model = YOLO(model_path)

    # Запуск обучения
    model.train(data=data_yaml, epochs=epochs, imgsz=imgsz)
    print("Обучение завершено!")

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
    show_image(annotated_image, title="Detected Objects")

    # Выводим результаты в консоль
    for result in results[0].boxes:
        class_id = int(result.cls)
        confidence = result.conf
        box = result.xyxy
        #print(f"Класс: {model.names[class_id]} | Доверие: {confidence:.2%} | Координаты (X1, Y1, X2, Y2): {box.tolist()}")
        #print(f"Объект: {model.names[class_id]}, Доверие: {confidence:.2f}, Координаты: {box}")

# Обучение модели
#data_yaml = "data.yaml"  # Путь к вашему файлу конфигурации данных
#train_model(data_yaml=data_yaml, model_path="yolov5s.pt", epochs=100, imgsz=640)

# Использование обученной модели
image_path = "mysor1.png"  # Замените на путь к изображению
model_path = "runs/detect/train6/weights/best.pt"  # Путь к обученной модели
detect_waste(image_path, model_path=model_path)
