import sqlite3

def init_db():
    conn = sqlite3.connect('message_history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (sender TEXT, message TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def save_message(sender, message):
    conn = sqlite3.connect('message_history.db')
    c = conn.cursor()
    c.execute("INSERT INTO messages (sender, message) VALUES (?, ?)", (sender, message))
    conn.commit()
    conn.close()

def load_messages():
    conn = sqlite3.connect('message_history.db')
    c = conn.cursor()
    c.execute("SELECT sender, message FROM messages ORDER BY timestamp")
    messages = c.fetchall()
    conn.close()
    return messages