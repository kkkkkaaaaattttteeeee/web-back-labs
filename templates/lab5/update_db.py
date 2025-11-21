import sqlite3
import psycopg2
import os

def update_sqlite_db():
    """Обновляет структуру SQLite базы данных"""
    try:
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        
        print("Проверяем SQLite базу данных...")
        
        # Добавляем столбец full_name в таблицу users если его нет
        cur.execute("PRAGMA table_info(users);")
        columns = [col[1] for col in cur.fetchall()]
        
        if 'full_name' not in columns:
            print("Добавляем столбец full_name в таблицу users...")
            cur.execute("ALTER TABLE users ADD COLUMN full_name TEXT;")
            print("✓ full_name добавлен")
        else:
            print("✓ full_name уже существует")
        
        # Обновляем таблицу articles с новыми полями
        cur.execute("PRAGMA table_info(articles);")
        columns = [col[1] for col in cur.fetchall()]
        
        if 'is_favorite' not in columns:
            print("Добавляем столбец is_favorite в таблицу articles...")
            cur.execute("ALTER TABLE articles ADD COLUMN is_favorite BOOLEAN DEFAULT 0;")
            print("✓ is_favorite добавлен")
        else:
            print("✓ is_favorite уже существует")
        
        if 'is_public' not in columns:
            print("Добавляем столбец is_public в таблицу articles...")
            cur.execute("ALTER TABLE articles ADD COLUMN is_public BOOLEAN DEFAULT 0;")
            print("✓ is_public добавлен")
        else:
            print("✓ is_public уже существует")
        
        conn.commit()
        conn.close()
        print("✅ SQLite база данных успешно обновлена!")
        
    except Exception as e:
        print(f"❌ Ошибка при обновлении SQLite базы: {e}")

def update_postgresql_db():
    """Обновляет структуру PostgreSQL базы данных"""
    try:
        conn = psycopg2.connect(
            host='127.0.0.1',
            database='knowledge_base_df',  
            user='obedina_ekaterina_knowledge_base',
            password='123'
        )
        cur = conn.cursor()
        
        print("Проверяем PostgreSQL базу данных...")
        
        # Добавляем столбец full_name в таблицу users если его нет
        try:
            cur.execute("ALTER TABLE users ADD COLUMN full_name TEXT;")
            print("✓ Добавлен столбец full_name в таблицу users")
        except Exception as e:
            if 'already exists' in str(e):
                print("✓ Столбец full_name уже существует")
            else:
                print(f"⚠ Ошибка с full_name: {e}")
        
        # Добавляем столбцы в таблицу articles если их нет
        try:
            cur.execute("ALTER TABLE articles ADD COLUMN is_favorite BOOLEAN DEFAULT false;")
            print("✓ Добавлен столбец is_favorite в таблицу articles")
        except Exception as e:
            if 'already exists' in str(e):
                print("✓ Столбец is_favorite уже существует")
            else:
                print(f"⚠ Ошибка с is_favorite: {e}")
        
        try:
            cur.execute("ALTER TABLE articles ADD COLUMN is_public BOOLEAN DEFAULT false;")
            print("✓ Добавлен столбец is_public в таблицу articles")
        except Exception as e:
            if 'already exists' in str(e):
                print("✓ Столбец is_public уже существует")
            else:
                print(f"⚠ Ошибка с is_public: {e}")
        
        conn.commit()
        conn.close()
        print("✅ PostgreSQL база данных успешно обновлена!")
        
    except Exception as e:
        print(f"❌ Ошибка при подключении к PostgreSQL: {e}")

if __name__ == '__main__':
    print("=" * 60)
    print("ОБНОВЛЕНИЕ СТРУКТУРЫ БАЗ ДАННЫХ")
    print("=" * 60)
    
    print("\n1. Обновление SQLite базы данных:")
    print("-" * 40)
    update_sqlite_db()
    
    print("\n2. Обновление PostgreSQL базы данных:")
    print("-" * 40)
    update_postgresql_db()
    
    print("\n" + "=" * 60)
    print("ОБНОВЛЕНИЕ ЗАВЕРШЕНО!")
    print("=" * 60)