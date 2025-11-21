import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    
    # Таблица пользователей с полем full_name
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT
        )
    ''')
    
    # Таблица статей с полями is_favorite и is_public
    cur.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login_id INTEGER NOT NULL,
            title VARCHAR(50),
            article_text TEXT,
            is_favorite BOOLEAN DEFAULT 0,
            is_public BOOLEAN DEFAULT 0,
            likes INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (login_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("База данных инициализирована с новой структурой!")

if __name__ == '__main__':
    init_db()