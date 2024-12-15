import tkinter as tk
from tkinter import messagebox

# Создание главного окна приложения
root = tk.Tk()
root.title("Приложение с интерфейсом")
root.geometry("400x300")

# Функция обработки кнопки
def on_button_click():
    user_input = entry.get()
    if user_input:
        messagebox.showinfo("Результат", f"Вы ввели: {user_input}")
    else:
        messagebox.showwarning("Ошибка", "Пожалуйста, введите текст!")

# Создание элементов интерфейса
label = tk.Label(root, text="Введите текст:", font=("Arial", 14))
label.pack(pady=10)

entry = tk.Entry(root, font=("Arial", 14), width=30)
entry.pack(pady=10)

button = tk.Button(root, text="Отправить", font=("Arial", 14), command=on_button_click)
button.pack(pady=10)

# Запуск приложения
root.mainloop()
