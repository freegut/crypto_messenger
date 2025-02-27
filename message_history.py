import sqlite3
from encryption import encrypt_message, decrypt_message

def init_db():
    conn = sqlite3.connect('message_history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (sender TEXT, encrypted_message BLOB, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def save_message(sender, private_key, public_key, message):
    encrypted_message = encrypt_message(private_key, public_key, message)
    conn = sqlite3.connect('message_history.db')
    c = conn.cursor()
    c.execute("INSERT INTO messages (sender, encrypted_message) VALUES (?, ?)", (sender, encrypted_message))
    conn.commit()
    conn.close()

def load_messages(private_key, public_key):
    conn = sqlite3.connect('message_history.db')
    c = conn.cursor()
    c.execute("SELECT sender, encrypted_message FROM messages ORDER BY timestamp")
    messages = []
    for sender, encrypted_message in c.fetchall():
        decrypted_message = decrypt_message(private_key, public_key, encrypted_message)
        messages.append((sender, decrypted_message.decode()))
    conn.close()
    return messages