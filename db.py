import sqlite3
from datetime import datetime


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

def reimb_db():
    conn=sqlite3.connect('reimbreeze.db')
    cur=conn.cursor()
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS reimb_form(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        purpose TEXT NOT NULL,
        amount REAL NOT NULL,
        letter TEXT NOT NULL,
        certificate TEXT NOT NULL,
  brochure TEXT NOT NULL,
            bill TEXT NOT NULL,
            status TEXT NOT NULL,
            submitted_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def insert_reimbursement(email, purpose, amount, letter, certificate, brochure, bill):
    conn = sqlite3.connect('reimbreeze.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO reimb_form (
            email, purpose, amount, letter, certificate, brochure, bill, status, submitted_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 'Pending Teacher', ?)
    ''', (email, purpose, amount, letter, certificate, brochure, bill, datetime.now()))
    conn.commit()
    conn.close()

def get_reimbursement_by_email(email):
    conn=sqlite3.connect('reimbreeze.db')
    cur=conn.cursor()
    cur.execute("SELECT purpose, amount, status, submitted_at FROM reimb_form WHERE email = ?", (email,))
    data = cur.fetchall()
    conn.close()
    return data

def get_name_by_email(email):
    conn=sqlite3.connect('reimbreeze.db')
    cur=conn.cursor()
    cur.execute("SELECT name FROM users WHERE email = ?", (email,))
    name = cur.fetchone()
    if name:
        name = name[0]  # ✅ get only the string value

    conn.close()
    return name