import socket
import threading
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import tkinter as tk
from tkinter import scrolledtext, messagebox
from kademlia.network import Server
from kademlia.utils import digest
import pyperclip
import nacl.utils
from nacl.public import PrivateKey, Box
import nacl.secret
import nacl.hash

# Генерация ключей для шифрования
private_key = PrivateKey.generate()
public_key = private_key.public_key

# Функция для шифрования сообщения
def encrypt_message(message, recipient_public_key):
    box = Box(private_key, recipient_public_key)
    encrypted = box.encrypt(message.encode())
    return encrypted

# Функция для расшифрования сообщения
def decrypt_message(encrypted_message, sender_public_key):
    box = Box(private_key, sender_public_key)
    decrypted = box.decrypt(encrypted_message)
    return decrypted.decode()

# Автоматическое определение IP-адреса
def get_local_ip():
    try:
        temp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        temp_sock.connect(("8.8.8.8", 80))
        local_ip = temp_sock.getsockname()[0]
        temp_sock.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

# Автоматический выбор свободного порта
def get_free_port(start_port=12345):
    port = start_port
    while True:
        try:
            temp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            temp_sock.bind(("0.0.0.0", port))
            temp_sock.close()
            return port
        except OSError:
            port += 1

# Класс для P2P-мессенджера
class P2PMessenger:
    def __init__(self):
        self.host = get_local_ip()
        self.port = get_free_port()
        self.user_id = None
        self.private_key = private_key
        self.public_key = public_key
        self.contacts = {}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        self.connection = None
        self.address = None

        # Инициализация DHT
        self.dht_server = Server()
        self.dht_server.listen(8468)
        threading.Thread(target=self.bootstrap_dht).start()

    # Подключение к DHT
    def bootstrap_dht(self):
        self.dht_server.bootstrap([("127.0.0.1", 8468)])

    # Генерация ID на основе открытого ключа
    def generate_user_id(self):
        public_key_bytes = self.public_key.__bytes__()
        return digest(public_key_bytes).hex()

    # Ожидание подключения
    def wait_for_connection(self):
        print("Ожидание подключения...")
        self.connection, self.address = self.sock.accept()
        print(f"Подключен: {self.address}")

    # Отправка сообщения
    def send_message(self, contact_id, message):
        if contact_id in self.contacts:
            recipient_public_key = self.contacts[contact_id]['public_key']
            encrypted_message = encrypt_message(message, recipient_public_key)
            self.contacts[contact_id]['socket'].send(encrypted_message)

    # Получение сообщения
    def receive_message(self):
        if self.connection:
            encrypted_message = self.connection.recv(1024)
            if encrypted_message:
                sender_public_key = self.connection.getpeername()
                return decrypt_message(encrypted_message, sender_public_key)
        return None

    # Добавление контакта по ID
    def add_contact(self, contact_id):
        contact_info = self.dht_server.get(contact_id)
        if contact_info:
            contact_host, contact_port, contact_public_key = contact_info.split(":")
            contact_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            contact_sock.connect((contact_host, int(contact_port)))
            self.contacts[contact_id] = {'socket': contact_sock, 'public_key': contact_public_key}
            print(f"Контакт {contact_id} добавлен.")
            return True
        else:
            print(f"Контакт {contact_id} не найден.")
            return False

    # Регистрация в DHT
    def register_in_dht(self):
        self.user_id = self.generate_user_id()
        self.dht_server.set(self.user_id, f"{self.host}:{self.port}:{self.public_key.__bytes__().hex()}")
        print(f"Зарегистрирован в DHT с ID: {self.user_id}")

# Графический интерфейс
class MessengerGUI:
    def __init__(self, messenger):
        self.messenger = messenger

        # Создание окна регистрации
        self.registration_window = tk.Tk()
        self.registration_window.title("Регистрация")

        # Генерация ID и регистрация в DHT
        self.messenger.register_in_dht()

        # Отображение ID
        self.id_label = tk.Label(self.registration_window, text=f"Ваш ID: {self.messenger.user_id}")
        self.id_label.pack(padx=10, pady=10)

        # Кнопка "Копировать ID"
        self.copy_button = tk.Button(self.registration_window, text="Копировать ID", command=self.copy_id)
        self.copy_button.pack(padx=10, pady=5)

        # Кнопка завершения регистрации
        self.register_button = tk.Button(self.registration_window, text="Продолжить", command=self.open_chat_window)
        self.register_button.pack(padx=10, pady=10)

        # Окно чата (скрыто до регистрации)
        self.chat_window = None

    # Копирование ID в буфер обмена
    def copy_id(self):
        pyperclip.copy(self.messenger.user_id)
        messagebox.showinfo("Успех", "ID скопирован в буфер обмена!")

    # Открытие окна чата
    def open_chat_window(self):
        self.registration_window.destroy()
        self.chat_window = tk.Tk()
        self.chat_window.title(f"Мессенджер - {self.messenger.user_id}")

        # Поле для отображения сообщений
        self.chat_area = scrolledtext.ScrolledText(self.chat_window, wrap=tk.WORD, state='disabled')
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Поле для ввода сообщений
        self.entry_field = tk.Entry(self.chat_window)
        self.entry_field.pack(padx=10, pady=10, fill=tk.X)

        # Кнопка отправки сообщения
        self.send_button = tk.Button(self.chat_window, text="Отправить", command=self.send_message)
        self.send_button.pack(padx=10, pady=10)

        # Кнопка добавления контакта
        self.add_contact_button = tk.Button(self.chat_window, text="Добавить контакт", command=self.open_add_contact_window)
        self.add_contact_button.pack(padx=10, pady=10)

        # Запуск потока для получения сообщений
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.daemon = True
        self.receive_thread.start()

    # Открытие окна добавления контакта
    def open_add_contact_window(self):
        add_contact_window = tk.Toplevel(self.chat_window)
        add_contact_window.title("Добавить контакт")

        # Поле для ввода ID контакта
        contact_id_label = tk.Label(add_contact_window, text="Введите ID контакта:")
        contact_id_label.pack(padx=10, pady=5)
        self.contact_id_entry = tk.Entry(add_contact_window)
        self.contact_id_entry.pack(padx=10, pady=5)

        # Кнопка добавления контакта
        add_button = tk.Button(add_contact_window, text="Добавить", command=self.add_contact)
        add_button.pack(padx=10, pady=10)

    # Добавление контакта
    def add_contact(self):
        contact_id = self.contact_id_entry.get()
        if contact_id:
            if self.messenger.add_contact(contact_id):
                messagebox.showinfo("Успех", f"Контакт {contact_id} добавлен!")
            else:
                messagebox.showerror("Ошибка", f"Контакт {contact_id} не найден.")
        else:
            messagebox.showerror("Ошибка", "Введите ID контакта!")

    # Отправка сообщения
    def send_message(self):
        message = self.entry_field.get()
        if message and self.messenger.contacts:
            contact_id = list(self.messenger.contacts.keys())[0]  # Отправка первому контакту
            self.messenger.send_message(contact_id, message)
            self.display_message(f"Вы: {message}")
            self.entry_field.delete(0, tk.END)

    # Получение сообщений
    def receive_messages(self):
        while True:
            message = self.messenger.receive_message()
            if message:
                self.display_message(f"Собеседник: {message}")

    # Отображение сообщений в чате
    def display_message(self, message):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, message + "\n")
        self.chat_area.config(state='disabled')
        self.chat_area.yview(tk.END)

    # Запуск интерфейса
    def run(self):
        self.registration_window.mainloop()

# Основная функция
if __name__ == "__main__":
    # Создание P2P-мессенджера
    messenger = P2PMessenger()

    # Ожидание подключения в отдельном потоке
    threading.Thread(target=messenger.wait_for_connection).start()

    # Запуск графического интерфейса
    gui = MessengerGUI(messenger)
    gui.run()