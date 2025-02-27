import tkinter as tk
from tkinter import scrolledtext, messagebox
from message_history import save_message, load_messages
from notifications import show_notification

class MessengerGUI:
    def __init__(self, messenger):
        self.messenger = messenger
        self.setup_ui()

    def setup_ui(self):
        self.root = tk.Tk()
        self.root.title(f"Мессенджер - Пользователь {self.messenger.user_id}")

        # Колонка с пользователями
        self.users_frame = tk.Frame(self.root)
        self.users_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.users_label = tk.Label(self.users_frame, text="Пользователи")
        self.users_label.pack()

        self.users_listbox = tk.Listbox(self.users_frame)
        self.users_listbox.pack(fill=tk.Y)
        self.update_users_list()

        # Поле для отображения сообщений
        self.chat_area = scrolledtext.ScrolledText(self.root, state='disabled')
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Поле для ввода сообщений
        self.entry_field = tk.Entry(self.root)
        self.entry_field.pack(padx=10, pady=10, fill=tk.X)

        # Кнопка отправки сообщения
        self.send_button = tk.Button(self.root, text="Отправить", command=self.send_message)
        self.send_button.pack(padx=10, pady=10)

    def update_users_list(self):
        """
        Обновляет список пользователей.
        """
        self.users_listbox.delete(0, tk.END)
        for user_id, username in get_all_users():
            self.users_listbox.insert(tk.END, f"{username} ({user_id[:8]}...)")

    def send_message(self):
        """
        Отправляет сообщение выбранному пользователю.
        """
        selected_user = self.users_listbox.get(tk.ACTIVE)
        if selected_user:
            user_id = selected_user.split("(")[1].split(")")[0]
            message = self.entry_field.get()
            if message:
                self.messenger.send_message(user_id, message)
                save_message("Вы", self.messenger.private_key, user_id, message)
                self.display_message(f"Вы: {message}")
                self.entry_field.delete(0, tk.END)

    def display_message(self, message):
        """
        Отображает сообщение в чате.
        """
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, message + "\n")
        self.chat_area.config(state='disabled')
        self.chat_area.yview(tk.END)
        show_notification("Новое сообщение", message)

    def run(self):
        self.root.mainloop()