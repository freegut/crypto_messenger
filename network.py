import socket
import threading
from encryption import encrypt_message, decrypt_message

class Network:
    def __init__(self, host, port, private_key):
        self.host = host
        self.port = port
        self.private_key = private_key
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        self.connections = {}

    def start_server(self):
        """
        Запускает сервер для приема входящих соединений.
        """
        print(f"Сервер запущен на {self.host}:{self.port}")
        while True:
            conn, addr = self.sock.accept()
            print(f"Подключен: {addr}")
            threading.Thread(target=self.handle_client, args=(conn, addr)).start()

    def handle_client(self, conn, addr):
        """
        Обрабатывает входящие соединения.
        """
        while True:
            try:
                data = conn.recv(1024)
                if data:
                    decrypted_message = decrypt_message(self.private_key, data)
                    print(f"Получено сообщение от {addr}: {decrypted_message}")
                else:
                    break
            except Exception as e:
                print(f"Ошибка при обработке сообщения: {e}")
                break
        conn.close()

    def send_message(self, host, port, public_key, message):
        """
        Отправляет сообщение другому пользователю.
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            encrypted_message = encrypt_message(public_key, message)
            sock.send(encrypted_message)
            sock.close()
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")