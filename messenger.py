import socket
import threading
from dht import DHTServer
from network import Network
from encryption import encrypt_message, decrypt_message

class P2PMessenger:
    def __init__(self, user_id, private_key):
        self.user_id = user_id
        self.private_key = private_key
        self.host = self.get_local_ip()
        self.port = self.get_free_port()
        self.network = Network(self.host, self.port, self.private_key)
        self.dht_server = DHTServer()

        # Запуск сервера в отдельном потоке
        threading.Thread(target=self.network.start_server).start()

        # Регистрация в DHT
        asyncio.run(self.dht_server.bootstrap())
        asyncio.run(self.dht_server.register_user(self.user_id, self.host, self.port))

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

    def send_message(self, user_id, message):
        """
        Отправляет сообщение другому пользователю.
        """
        user_info = asyncio.run(self.dht_server.find_user(user_id))
        if user_info:
            host, port = user_info.split(":")
            self.network.send_message(host, int(port), user_id, message)
        else:
            print(f"Пользователь {user_id} не найден.")