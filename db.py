import sqlite3

def connect_db():
    return sqlite3.connect('reimbreeze.db')

def create_users_table():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def insert_user(name, email, password_hash, role):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO users (name, email, password_hash, role)
        VALUES (?, ?, ?, ?)
    ''', (name, email, password_hash, role))
    conn.commit()
    conn.close()

def get_user_by_email(email):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cur.fetchone()
    conn.close()
    return user
