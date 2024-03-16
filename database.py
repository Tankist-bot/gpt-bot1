import sqlite3

# Подключение к базе данных
conn = sqlite3.connect('users_data.db',check_same_thread=False)
cursor = conn.cursor()

# Создание таблицы для хранения данных пользователей
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        system_content TEXT,
        question TEXT,
        assistant_content TEXT
    )
''')

# Функция для сохранения данных пользователя в базе данных
def save_user_data(conn, user_id, system_content, question, assistant_content):
    cur = conn.cursor()
    cur.execute('''
        INSERT OR REPLACE INTO users (user_id, system_content, question, assistant_content)
        VALUES (?, ?, ?, ?)
    ''', (user_id, system_content, question, assistant_content))
    conn.commit()

# Функция для получения данных пользователя из базы данных
def get_user_data(conn, user_id):
    cur = conn.cursor()
    cur.execute('SELECT system_content, question, assistant_content FROM users WHERE user_id = ?', (user_id,))
    row = cur.fetchone()
    if row:
        system_content, question, assistant_content = row
        return system_content, question, assistant_content
    else:
        return None, None, None

def update_user_data(conn, user_id, system_content, question, assistant_content):
    cur = conn.cursor()
    cur.execute('''
    UPDATE users
    SET system_content = ?,
    question = ?,
    assistant_content = ?
    WHERE user_id = ?
    ''', (system_content, question, assistant_content, user_id))
    conn.commit()

# Пример использования функций
save_user_data(conn, '123456', 'content', 'question', 'assistant')
content, question, assistant = get_user_data(conn, '123456')
print(content, question, assistant)

# Не забудьте закрыть соединение с базой данных после использования
conn.close()

