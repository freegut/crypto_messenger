import os
from encryption import encrypt_message, decrypt_message


def 

def send_file(sock, private_key, public_key, file_path):
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    with open(file_path, 'rb') as file:
        file_data = file.read()
    encrypted_data = encrypt_message(private_key, public_key, file_data.decode())
    sock.send(f"FILE:{file_name}:{file_size}".encode())
    sock.send(encrypted_data)
    print(f"Файл {file_name} отправлен.")

def receive_file(sock, private_key, public_key):
    file_info = sock.recv(1024).decode()
    if file_info.startswith("FILE:"):
        _, file_name, file_size = file_info.split(":")
        file_size = int(file_size)
        encrypted_data = sock.recv(file_size)
        decrypted_data = decrypt_message(private_key, public_key, encrypted_data)
        with open(file_name, 'wb') as file:
            file.write(decrypted_data)
        print(f"Файл {file_name} получен.")