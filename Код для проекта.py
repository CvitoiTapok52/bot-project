import cv2
import numpy as np
from PIL import Image
import pytesseract

# Функция для распознавания мусора на изображении
def detect_waste(image_path):
    # Загрузка изображения
    image = cv2.imread(image_path)
    if image is None:
        print("Ошибка загрузки изображения!")
        return False

    # Преобразование в серый цвет
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Пороговое значение для выделения объектов
    _, threshold = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    # Нахождение контуров
    contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Определение объектов, похожих на мусор (условный критерий)
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 1000:  # Условный порог площади
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Отображение результатов
    cv2.imshow('Detected Waste', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Функция для анализа текстовых данных
def analyze_complaints(text):
    keywords = ["свалка", "мусор", "загрязнение", "нарушение", "отходы"]
    violations = [word for word in keywords if word in text.lower()]
    if violations:
        print("Обнаружены возможные нарушения:", ", ".join(violations))
    else:
        print("Нарушений не обнаружено.")

# Пример использования
# Анализ изображения
image_path = "nomysor1.png"  # Замените на путь к вашему изображению
detect_waste(image_path)

# Анализ текстовых данных
complaint_text = "На улице Лесной образовалась большая свалка отходов."
analyze_complaints(complaint_text)
