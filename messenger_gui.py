import tkinter as tk
from tkinter import scrolledtext, messagebox
import pyperclip
from notifications import show_notification
from message_history import save_message, load_messages

class MessengerGUI:
    def __init__(self, messenger):
        self.messenger = messenger
        self.setup_ui()

    def setup_ui(self):
        self.root = tk.Tk()
        self.root.title(f"Мессенджер - Пользователь {self.messenger.user_id}")

        # Поле для отображения сообщений
        self.chat_area = scrolledtext.ScrolledText(self.root, state='disabled')
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Поле для ввода сообщений
        self.entry_field = tk.Entry(self.root)
        self.entry_field.pack(padx=10, pady=10, fill=tk.X)

        # Кнопка отправки сообщения
        self.send_button = tk.Button(self.root, text="Отправить", command=self.send_message)
        self.send_button.pack(padx=10, pady=10)

        # Кнопка добавления контакта
        self.add_contact_button = tk.Button(self.root, text="Добавить контакт", command=self.open_add_contact_window)
        self.add_contact_button.pack(padx=10, pady=10)

        # Загрузка истории сообщений
        self.load_message_history()

    def load_message_history(self):
        messages = load_messages()
        for sender, message in messages:
            self.display_message(f"{sender}: {message}")

    def send_message(self):
        message = self.entry_field.get()
        if message and self.messenger.contacts:
            contact_id = list(self.messenger.contacts.keys())[0]
            self.messenger.send_message(contact_id, message)
            save_message("Вы", message)
            self.display_message(f"Вы: {message}")
            self.entry_field.delete(0, tk.END)

    def display_message(self, message):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, message + "\n")
        self.chat_area.config(state='disabled')
        self.chat_area.yview(tk.END)

    def open_add_contact_window(self):
        add_contact_window = tk.Toplevel(self.root)
        add_contact_window.title("Добавить контакт")

        # Поле для ввода ID контакта
        contact_id_label = tk.Label(add_contact_window, text="Введите ID контакта:")
        contact_id_label.pack(padx=10, pady=5)
        self.contact_id_entry = tk.Entry(add_contact_window)
        self.contact_id_entry.pack(padx=10, pady=5)

        # Кнопка добавления контакта
        add_button = tk.Button(add_contact_window, text="Добавить", command=self.add_contact)
        add_button.pack(padx=10, pady=10)

    def add_contact(self):
        contact_id = self.contact_id_entry.get()
        if contact_id:
            if self.messenger.add_contact(contact_id):
                messagebox.showinfo("Успех", f"Контакт {contact_id} добавлен!")
            else:
                messagebox.showerror("Ошибка", f"Контакт {contact_id} не найден.")
        else:
            messagebox.showerror("Ошибка", "Введите ID контакта!")

    def run(self):
        self.root.mainloop()