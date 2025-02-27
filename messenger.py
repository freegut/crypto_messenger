import socket
import threading
from dht import DHTServer
from encryption import encrypt_message, decrypt_message

class P2PMessenger:
    def __init__(self, user_id):
        self.user_id = user_id
        self.host = self.get_local_ip()
        self.port = self.get_free_port()
        self.contacts = {}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        self.connection = None
        self.address = None

        # Инициализация DHT
        self.dht_server = DHTServer()
        threading.Thread(target=self.dht_server.bootstrap).start()

    def get_local_ip(self):
        try:
            temp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            temp_sock.connect(("8.8.8.8", 80))
            local_ip = temp_sock.getsockname()[0]
            temp_sock.close()
            return local_ip
        except Exception:
            return "127.0.0.1"

    def get_free_port(self, start_port=12345):
        port = start_port
        while True:
            try:
                temp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                temp_sock.bind(("0.0.0.0", port))
                temp_sock.close()
                return port
            except OSError:
                port += 1

    def wait_for_connection(self):
        print("Ожидание подключения...")
        self.connection, self.address = self.sock.accept()
        print(f"Подключен: {self.address}")

    def send_message(self, contact_id, message):
        if contact_id in self.contacts:
            encrypted_message = encrypt_message(message)
            self.contacts[contact_id]['socket'].send(encrypted_message)

    def receive_message(self):
        if self.connection:
            encrypted_message = self.connection.recv(1024)
            if encrypted_message:
                return decrypt_message(encrypted_message)
        return None

    def add_contact(self, contact_id):
        contact_info = self.dht_server.get(contact_id)
        if contact_info:
            contact_host, contact_port = contact_info.split(":")
            contact_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            contact_sock.connect((contact_host, int(contact_port)))
            self.contacts[contact_id] = {'socket': contact_sock}
            print(f"Контакт {contact_id} добавлен.")
            return True
        else:
            print(f"Контакт {contact_id} не найден.")
            return False

    def register_in_dht(self):
        self.dht_server.set(self.user_id, f"{self.host}:{self.port}")
        print(f"Зарегистрирован в DHT с ID: {self.user_id}")