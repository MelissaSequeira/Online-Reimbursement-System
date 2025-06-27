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
            role TEXT NOT NULL,
            department TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def insert_user(name, email, password_hash, role, department):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO users (name, email, password_hash, role, department)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, email, password_hash, role, department))
    conn.commit()
    conn.close()


def get_user_by_email(email):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cur.fetchone()
    conn.close()
    return user  # Ensure you return department-aware structure

def get_emails_by_role_and_dept(role, department):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT email FROM users WHERE role = ? AND department = ?", (role, department))
    result = cur.fetchall()
    conn.close()
    return [email[0] for email in result]


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
            submitted_at TEXT NOT NULL,

            teacher_status TEXT DEFAULT 'Pending',
            teacher_remarks TEXT,
            hod_status TEXT DEFAULT 'Pending',
            hod_remarks TEXT,
            principal_status TEXT DEFAULT 'Pending',
            principal_remarks TEXT,
            md_status TEXT DEFAULT 'Pending',
            md_remarks TEXT,
            accountant_status TEXT DEFAULT 'Pending',
            accountant_remarks TEXT)
        
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


def get_pending_requests_for_teacher():
    conn= sqlite3.connect("reimbreeze.db")
    cur=conn.cursor()
    cur.execute("SELECT * FROM reimb_form WHERE teacher_status = 'Pending'")
    data = cur.fetchall()
    conn.close()
    return data

def get_pending_requests_for_hod():
    conn= sqlite3.connect("reimbreeze.db")
    cur=conn.cursor()
    cur.execute("SELECT * FROM reimb_form WHERE hod_status = 'Pending'")
    data = cur.fetchall()
    conn.close()
    return data

def get_pending_requests_for_principal():
    conn= sqlite3.connect("reimbreeze.db")
    cur=conn.cursor()
    cur.execute("SELECT * FROM reimb_form WHERE principal_status = 'Pending'")
    data = cur.fetchall()
    conn.close()
    return data

def get_pending_requests_for_md():
    conn= sqlite3.connect("reimbreeze.db")
    cur=conn.cursor()
    cur.execute("SELECT * FROM reimb_form WHERE md_status = 'Pending'")
    data = cur.fetchall()
    conn.close()
    return data

def update_teacher_approval(req_id, status, remarks):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('''
        UPDATE reimb_form
        SET teacher_status = ?, teacher_remarks = ?, status = ?
        WHERE id = ?
    ''', (status, remarks, f"Pending HOD" if status == "Approved" else "Rejected by Teacher", req_id))
    conn.commit()
    conn.close()

def update_hod_approval(req_id, status, remarks):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('''
        UPDATE reimb_form
        SET hod_status = ?, hod_remarks = ?, status = ?
        WHERE id = ?
    ''', (status, remarks, f"Pending Principal" if status == "Approved" else "Rejected by HOD", req_id))
    conn.commit()
    conn.close()

def update_principal_approval(req_id, status, remarks):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('''
        UPDATE reimb_form
        SET principal_status = ?, principal_remarks = ?, status = ?
        WHERE id = ?
    ''', (status, remarks, f"Pending MD" if status == "Approved" else "Rejected by Principal", req_id))
    conn.commit()
    conn.close()

def update_md_approval(req_id, status, remarks):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('''
        UPDATE reimb_form
        SET md_status = ?, md_remarks = ?, status = ?
        WHERE id = ?
    ''', (status, remarks, f"Pending Accountant" if status == "Approved" else "Rejected by Accountant", req_id))
    conn.commit()
    conn.close()

def get_emails_by_role(role):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT email FROM users WHERE role = ?", (role,))
    result = cur.fetchall()
    conn.close()
    return [email[0] for email in result]


def get_pending_requests_for_accountant():
    conn = sqlite3.connect("reimbreeze.db")
    cur = conn.cursor()
    cur.execute('''
        SELECT * FROM reimb_form 
        WHERE teacher_status = 'Approved'
          AND hod_status = 'Approved'
          AND principal_status = 'Approved'
          AND md_status = 'Approved'
          AND accountant_status = 'Pending'
    ''')
    data = cur.fetchall()
    conn.close()
    return data

def update_accountant_approval(req_id, status, remarks):
    conn = sqlite3.connect("reimbreeze.db")
    cur = conn.cursor()
    cur.execute('''
        UPDATE reimb_form
        SET accountant_status = ?, accountant_remarks = ?, status = ?
        WHERE id = ?
    ''', (
        status, remarks,
        'Processed' if status == 'Approved' else 'Rejected by Accountant',
        req_id
    ))
    conn.commit()
    conn.close()
