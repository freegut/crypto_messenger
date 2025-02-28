import sqlite3
import os
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import serialization

def init_db():
    """
    Инициализирует базу данных и создает таблицу users, если она не существует.
    """
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id TEXT PRIMARY KEY,
                  public_key TEXT,
                  private_key TEXT,
                  username TEXT UNIQUE)''')
    conn.commit()
    conn.close()

def generate_user_id():
    """
    Генерирует уникальный ID (256-битный ключ) и возвращает его в виде строки.
    Возвращает:
        - public_key_hex: публичный ключ в виде строки.
        - private_key: закрытый ключ для шифрования.
    """
    private_key = x25519.X25519PrivateKey.generate()
    public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    return public_key.hex(), private_key

def register_user(username):
    """
    Регистрирует нового пользователя в базе данных.
    Аргументы:
        - username: имя пользователя.
    Возвращает:
        - public_key_hex: публичный ключ (ID пользователя).
        - private_key: закрытый ключ для шифрования.
        - None, None: если пользователь уже существует.
    """
    init_db()  # Убедимся, что база данных инициализирована
    public_key_hex, private_key = generate_user_id()
    
    # Сериализуем закрытый ключ в строку
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    try:
        #comment
        # Пытаемся добавить нового пользователя
        c.execute("INSERT INTO users (id, public_key, private_key, username) VALUES (?, ?, ?, ?)",
                  (public_key_hex, public_key_hex, private_key_pem, username))
        conn.commit()
        conn.close()
        return public_key_hex, private_key
    except sqlite3.IntegrityError:
        # Если пользователь уже существует
        conn.close()
        return None, None

def authenticate_user(username):
    """
    Проверяет, существует ли пользователь с указанным именем.
    Аргументы:
        - username: имя пользователя.
    Возвращает:
        - user_id: ID пользователя, если он существует.
        - None: если пользователь не найден.
    """
    init_db()  # Убедимся, что база данных инициализирована
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    c.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    
    conn.close()
    return user[0] if user else None

def get_private_key(user_id):
    """
    Получает закрытый ключ пользователя по его ID.
    Аргументы:
        - user_id: ID пользователя.
    Возвращает:
        - private_key: закрытый ключ для шифрования.
        - None: если пользователь не найден.
    """
    init_db()  # Убедимся, что база данных инициализирована
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    c.execute("SELECT private_key FROM users WHERE id = ?", (user_id,))
    private_key_pem = c.fetchone()
    
    conn.close()
    
    if private_key_pem:
        # Десериализуем закрытый ключ из строки
        return serialization.load_pem_private_key(
            private_key_pem[0].encode('utf-8'),
            password=None
        )
    return None

def get_all_users():
    """
    Возвращает список всех зарегистрированных пользователей.
    Возвращает:
        - Список кортежей (id, username) всех пользователей.
    """
    init_db()  # Убедимся, что база данных инициализирована
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    c.execute("SELECT id, username FROM users")
    users = c.fetchall()
    
    conn.close()
    return users

def get_user_by_id(user_id):
    """
    Возвращает информацию о пользователе по его ID.
    Аргументы:
        - user_id: ID пользователя.
    Возвращает:
        - Кортеж (id, public_key, username) или None, если пользователь не найден.
    """
    init_db()  # Убедимся, что база данных инициализирована
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    c.execute("SELECT id, public_key, username FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    
    conn.close()
    return user

def delete_user(user_id):
    """
    Удаляет пользователя из базы данных по его ID.
    Аргументы:
        - user_id: ID пользователя.
    Возвращает:
        - True: если пользователь удален.
        - False: если пользователь не найден.
    """
    init_db()  # Убедимся, что база данных инициализирована
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    c.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    rows_affected = c.rowcount
    conn.close()
    return rows_affected > 0