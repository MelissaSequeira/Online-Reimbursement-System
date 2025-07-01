import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, send_from_directory, url_for, session, flash

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

def generate_reimbursement_report(data, output_path):
    """
    data = {
        'id': 1,
        'student_name': 'Melissa Sequeira',
        'email': 'melissa@email.com',
        'department': 'IT',
        'purpose': 'Workshop',
        'amount': 500,
        'submitted_at': '2024-07-01',
        'teacher_status': 'Approved',
        'teacher_remarks': 'Genuine reason',
        ...
    }
    """
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    y = height - 50

    c.setFont("Helvetica-Bold", 16)
    c.drawString(180, y, "Reimbursement Report")
    y -= 30

    c.setFont("Helvetica", 12)

    fields = [
        ('Request ID', data['id']),
        ('Student Name', data['student_name']),
        ('Email', data['email']),
        ('Department', data['department']),
        ('Purpose', data['purpose']),
        ('Amount', f"₹{data['amount']}"),
        ('Submitted At', data['submitted_at']),
        ('Teacher Status', f"{data['teacher_status']} - {data['teacher_remarks']}"),
        ('HOD Status', f"{data['hod_status']} - {data['hod_remarks']}"),
        ('Principal Status', f"{data['principal_status']} - {data['principal_remarks']}"),
        ('MD Status', f"{data['md_status']} - {data['md_remarks']}"),
        ('Accountant Status', f"{data['accountant_status']} - {data['accountant_remarks']}"),
    ]

    for label, value in fields:
        c.drawString(50, y, f"{label}: {value}")
        y -= 20
        if y < 100:
            c.showPage()
            y = height - 50

    c.save()


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
    return user


def get_emails_by_role_and_dept(role, department):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT email FROM users WHERE role = ? AND department = ?", (role, department))
    result = cur.fetchall()
    conn.close()
    return [email[0] for email in result]

def reimb_db():
    conn = sqlite3.connect('reimbreeze.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS reimb_form(
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
            accountant_remarks TEXT,
            department TEXT DEFAULT 'Unknown'
        )
    ''')
    conn.commit()
    conn.close()

# ---------------- User Management ----------------

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
    return user

def get_emails_by_role_and_dept(role, department):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT email FROM users WHERE role = ? AND department = ?", (role, department))
    result = cur.fetchall()
    conn.close()
    return [email[0] for email in result]

def get_emails_by_role(role):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT email FROM users WHERE role = ?", (role,))
    result = cur.fetchall()
    conn.close()
    return [email[0] for email in result]

def get_name_by_email(email):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT name FROM users WHERE email = ?", (email,))
    name = cur.fetchone()
    conn.close()
    return name[0] if name else None

# ---------------- Reimbursement Flow ----------------

def insert_reimbursement(email, purpose, amount, letter, certificate, brochure, bill):
    conn = sqlite3.connect('reimbreeze.db')
    c = conn.cursor()

    # Get department of student
    c.execute("SELECT department FROM users WHERE email = ?", (email,))
    department = c.fetchone()
    department = department[0] if department else "Unknown"

    c.execute('''
        INSERT INTO reimb_form (
            email, purpose, amount, letter, certificate, brochure, bill,
            status, submitted_at, department
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 'Pending Teacher', ?, ?)
    ''', (email, purpose, amount, letter, certificate, brochure, bill, datetime.now(), department))

    conn.commit()
    conn.close()

def get_reimbursement_by_email(email):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT purpose, amount, status, submitted_at FROM reimb_form WHERE email = ?", (email,))
    data = cur.fetchall()
    conn.close()
    return data

def get_pending_requests_for_teacher(department):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('''
        SELECT * FROM reimb_form 
        WHERE teacher_status = 'Pending' AND department = ?
    ''', (department,))
    data = cur.fetchall()
    conn.close()
    return data

def get_pending_requests_for_hod(department):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('''
        SELECT * FROM reimb_form 
        WHERE hod_status = 'Pending' AND teacher_status = 'Approved' AND department = ?
    ''', (department,))
    data = cur.fetchall()
    conn.close()
    return data

def get_pending_requests_for_principal():
    department = session.get('department')  # if you want to restrict to dept-wise
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('''
        SELECT * FROM reimb_form 
        WHERE principal_status = 'Pending'
          AND teacher_status = 'Approved'
          AND hod_status = 'Approved'
    ''')
    data = cur.fetchall()
    conn.close()
    return data

def get_pending_requests_for_md():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('''
        SELECT * FROM reimb_form 
        WHERE md_status = 'Pending'
          AND teacher_status = 'Approved'
          AND hod_status = 'Approved'
          AND principal_status = 'Approved'
    ''')
    data = cur.fetchall()
    conn.close()
    return data

def get_pending_requests_for_accountant():
    conn = connect_db()
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

# ---------------- Approval Updates ----------------

def update_teacher_approval(req_id, status, remarks):
    conn = connect_db()
    cur = conn.cursor()
    new_status = "Pending HOD" if status == "Approved" else "Rejected by Teacher"
    cur.execute('''
        UPDATE reimb_form
        SET teacher_status = ?, teacher_remarks = ?, status = ?
        WHERE id = ?
    ''', (status, remarks, new_status, req_id))
    conn.commit()
    conn.close()

def update_hod_approval(req_id, status, remarks):
    conn = connect_db()
    cur = conn.cursor()
    new_status = "Pending Principal" if status == "Approved" else "Rejected by HOD"
    cur.execute('''
        UPDATE reimb_form
        SET hod_status = ?, hod_remarks = ?, status = ?
        WHERE id = ?
    ''', (status, remarks, new_status, req_id))
    conn.commit()
    conn.close()

def update_principal_approval(req_id, status, remarks):
    conn = connect_db()
    cur = conn.cursor()
    new_status = "Pending MD" if status == "Approved" else "Rejected by Principal"
    cur.execute('''
        UPDATE reimb_form
        SET principal_status = ?, principal_remarks = ?, status = ?
        WHERE id = ?
    ''', (status, remarks, new_status, req_id))
    conn.commit()
    conn.close()

def update_md_approval(req_id, status, remarks):
    conn = connect_db()
    cur = conn.cursor()
    new_status = "Pending Accountant" if status == "Approved" else "Rejected by MD"
    cur.execute('''
        UPDATE reimb_form
        SET md_status = ?, md_remarks = ?, status = ?
        WHERE id = ?
    ''', (status, remarks, new_status, req_id))
    conn.commit()
    conn.close()

def update_accountant_approval(req_id, status, remarks):
    conn = connect_db()
    cur = conn.cursor()
    final_status = 'Processed' if status == 'Approved' else 'Rejected by Accountant'
    cur.execute('''
        UPDATE reimb_form
        SET accountant_status = ?, accountant_remarks = ?, status = ?
        WHERE id = ?
    ''', (status, remarks, final_status, req_id))
    conn.commit()
    conn.close()

# ---------------- Utility ----------------

def get_request_details(req_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT email, department FROM reimb_form WHERE id = ?", (req_id,))
    result = cur.fetchone()
    conn.close()
    return result  # returns (email, department)

def add_department_column_to_reimb_form():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(reimb_form)")
    columns = [row[1] for row in cur.fetchall()]
    if 'department' not in columns:
        cur.execute("ALTER TABLE reimb_form ADD COLUMN department TEXT DEFAULT 'Unknown'")
        print("✅ 'department' column added.")
    else:
        print("ℹ️ 'department' column already exists.")
    conn.commit()
    conn.close()


# Optional: Run this once manually
# add_department_column_to_reimb_form()
