import tkinter as tk
from tkinter import messagebox
from auth import register_user, authenticate_user
from messenger import P2PMessenger
from messenger_gui import MessengerGUI  # Импорт из нового файла

class AuthGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Авторизация")
        self.setup_ui()

    def setup_ui(self):
        # Поле для ввода логина
        self.username_label = tk.Label(self.root, text="Логин:")
        self.username_label.pack(padx=10, pady=5)
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack(padx=10, pady=5)

        # Поле для ввода пароля
        self.password_label = tk.Label(self.root, text="Пароль:")
        self.password_label.pack(padx=10, pady=5)
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack(padx=10, pady=5)

        # Кнопка входа
        self.login_button = tk.Button(self.root, text="Войти", command=self.login)
        self.login_button.pack(padx=10, pady=10)

        # Кнопка регистрации
        self.register_button = tk.Button(self.root, text="Зарегистрироваться", command=self.open_register_window)
        self.register_button.pack(padx=10, pady=5)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username and password:
            user_id = authenticate_user(username, password)
            if user_id:
                self.root.destroy()
                messenger = P2PMessenger(user_id)
                messenger_gui = MessengerGUI(messenger)
                messenger_gui.run()
            else:
                messagebox.showerror("Ошибка", "Неверный логин или пароль!")
        else:
            messagebox.showerror("Ошибка", "Введите логин и пароль!")

    def open_register_window(self):
        register_window = tk.Toplevel(self.root)
        register_window.title("Регистрация")

        # Поле для ввода логина
        reg_username_label = tk.Label(register_window, text="Логин:")
        reg_username_label.pack(padx=10, pady=5)
        self.reg_username_entry = tk.Entry(register_window)
        self.reg_username_entry.pack(padx=10, pady=5)

        # Поле для ввода пароля
        reg_password_label = tk.Label(register_window, text="Пароль:")
        reg_password_label.pack(padx=10, pady=5)
        self.reg_password_entry = tk.Entry(register_window, show="*")
        self.reg_password_entry.pack(padx=10, pady=5)

        # Кнопка регистрации
        reg_button = tk.Button(register_window, text="Зарегистрироваться", command=self.register)
        reg_button.pack(padx=10, pady=10)

    def register(self):
        username = self.reg_username_entry.get()
        password = self.reg_password_entry.get()
        if username and password:
            user_id = register_user(username, password)
            if user_id:
                messagebox.showinfo("Успех", f"Пользователь {username} зарегистрирован с ID: {user_id}")
                print(f"Пользователь {username} зарегистрирован с ID: {user_id}")  # Отладочное сообщение
            else:
                messagebox.showerror("Ошибка", "Пользователь уже существует!")
                print("Пользователь уже существует!")  # Отладочное сообщение
        else:
            messagebox.showerror("Ошибка", "Введите логин и пароль!")
            print("Введите логин и пароль!")  # Отладочное сообщение

    def run(self):
        self.root.mainloop()