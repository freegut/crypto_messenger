import os

def send_file(sock, file_path):
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    sock.send(f"FILE:{file_name}:{file_size}".encode())
    with open(file_path, 'rb') as file:
        sock.sendfile(file)
    print(f"Файл {file_name} отправлен.")

def receive_file(sock):
    file_info = sock.recv(1024).decode()
    if file_info.startswith("FILE:"):
        _, file_name, file_size = file_info.split(":")
        file_size = int(file_size)
        with open(file_name, 'wb') as file:
            remaining = file_size
            while remaining > 0:
                data = sock.recv(min(remaining, 4096))
                file.write(data)
                remaining -= len(data)
        print(f"Файл {file_name} получен.")