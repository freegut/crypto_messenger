import tkinter as tk
from tkinter import messagebox
from auth import register_user, authenticate_user, get_all_users
from messenger import P2PMessenger
from messenger_gui import MessengerGUI

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

        # Кнопка входа
        self.login_button = tk.Button(self.root, text="Войти", command=self.login)
        self.login_button.pack(padx=10, pady=10)

        # Кнопка регистрации
        self.register_button = tk.Button(self.root, text="Зарегистрироваться", command=self.open_register_window)
        self.register_button.pack(padx=10, pady=5)

    def login(self):
        username = self.username_entry.get()
        if username:
            user_id = authenticate_user(username)
            if user_id:
                # Получаем private_key из базы данных или другого источника
                private_key = self.get_private_key(user_id)  # Нужно реализовать эту функцию
                if private_key:
                    self.root.destroy()
                    messenger = P2PMessenger(user_id, private_key)  # Передаем private_key
                    messenger_gui = MessengerGUI(messenger)
                    messenger_gui.run()
                else:
                    messagebox.showerror("Ошибка", "Не удалось получить закрытый ключ!")
            else:
                messagebox.showerror("Ошибка", "Пользователь не найден!")
        else:
            messagebox.showerror("Ошибка", "Введите логин!")

    def get_private_key(self, user_id):
        """
        Получает закрытый ключ пользователя из базы данных или другого источника.
        """
        # Здесь нужно реализовать логику получения private_key
        # Например, можно хранить private_key в базе данных или в файле
        # В данном примере просто возвращаем None
        return None

    def open_register_window(self):
        register_window = tk.Toplevel(self.root)
        register_window.title("Регистрация")

        # Поле для ввода логина
        reg_username_label = tk.Label(register_window, text="Логин:")
        reg_username_label.pack(padx=10, pady=5)
        self.reg_username_entry = tk.Entry(register_window)
        self.reg_username_entry.pack(padx=10, pady=5)

        # Кнопка регистрации
        reg_button = tk.Button(register_window, text="Зарегистрироваться", command=self.register)
        reg_button.pack(padx=10, pady=10)

    def register(self):
        username = self.reg_username_entry.get()
        if username:
            user_id, private_key = register_user(username)
            if user_id:
                messagebox.showinfo("Успех", f"Пользователь {username} зарегистрирован с ID: {user_id}")
                self.root.destroy()
                messenger = P2PMessenger(user_id, private_key)  # Передаем private_key
                messenger_gui = MessengerGUI(messenger)
                messenger_gui.run()
            else:
                messagebox.showerror("Ошибка", "Пользователь уже существует!")
        else:
            messagebox.showerror("Ошибка", "Введите логин!")

    def run(self):
        self.root.mainloop()