from flask import Flask, render_template, request, redirect, url_for, session, flash  #application hi flask ka hai
from flask_mail import *  #for email system
import random   #otp generate karne ke liye
from dotenv import load_dotenv
import os
from db import create_users_table, insert_user,get_user_by_email, reimb_db, insert_reimbursement, get_reimbursement_by_email,get_name_by_email
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from werkzeug.utils import secure_filename

app= Flask(__name__)
app.secret_key = os.urandom(24)
load_dotenv()
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=587
app.config['MAIL_USE_TLS']=True
#app.config['MAIL_USERNAME']='reimb.flask@gmail.com'
#app.config['MAIL_PASSWORD']='zjts tyfv eodl acut'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
mail= Mail(app)

UPLOAD_FILE='uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'pdf'])
app.config['UPLOAD_FOLDER']=UPLOAD_FILE

if not os.path.exists(UPLOAD_FILE):
    os.makedirs(UPLOAD_FILE)

create_users_table()
reimb_db()

@app.route('/register',methods=['GET','POST'])

def register():
    if request.method=='POST':
        email= request.form['email']
        if not email.endswith('fcrit.ac.in'):
            flash('Only college email id works', 'danger')
            return redirect(url_for('register'))
        otp=str(random.randint (100000,999999))
        session['otp'] = otp
        session['email'] = email


        msg = Message('Your OTP is ', sender='reimb.flask@gmail.com', recipients=[email])

        msg.body=f'Your OTP is {otp}'     
        mail.send(msg)

        flash("email sent on ur mail id", 'info')
        return redirect(url_for('verify'))
    return render_template('register.html')
                    

@app.route('/verify', methods=['GET','POST'])
def verify():
    if request.method=='POST':
        ent_otp=request.form['otp']
        if ent_otp== session.get('otp'):
            flash('Email verified successfully', 'success')
            return "✅ Verified! You can now register/login."
        else:
            flash('invalid otp', 'danger')
    return render_template('otp.html')

@app.route('/complete_registration', methods=['GET', 'POST'])
def complete_registration():
    email = session.get('email')  # always fetch this first

    if not email:
        flash("Session expired. Please restart registration.", "warning")
        return redirect(url_for('register'))

    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        role = request.form['role']

        if get_user_by_email(email):
            flash('User already exists. Please login.', 'warning')
            return redirect(url_for('login'))

        password_hash = generate_password_hash(password)
        insert_user(name, email, password_hash, role)

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('complete_registration.html')


@app.route('/login', methods=['GET', 'POST'])    
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = get_user_by_email(email)

        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['role'] = user[4]
            session['email'] = user[2]  # ✅ Correct: index 2 is email
            flash('Login successful', 'success')
            return redirect(url_for(f"{user[4].lower()}_dashboard"))
        else:
            flash('Invalid credentials', 'danger')

    return render_template('login.html')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/student/apply',methods=['GET', 'POST'])
def student_apply():
    amount=None
    if request.method == 'POST':
        purpose = request.form['purpose']
        amount = float(request.form['amount'])

        letter = request.files['letter']
        certificate = request.files['certificate']
        brochure = request.files['brochure']
        bill = request.files['bill']

        email = session.get('email')
        if not email:
            flash("⚠️ Session expired. Please log in again.", "warning")
            return redirect(url_for('login')) # simulate session for now
        def save_file(file_obj, label):
            if file_obj and allowed_file(file_obj.filename):
                filename = secure_filename(f"{label}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file_obj.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file_obj.save(filepath)
                return filename
            return None
        letter_filename = save_file(letter, 'letter')
        cert_filename = save_file(certificate, 'certificate')
        brochure_filename = save_file(brochure, 'brochure')
        bill_filename = save_file(bill, 'bill')
        insert_reimbursement(email, purpose, amount, letter_filename, cert_filename, brochure_filename, bill_filename)

        flash("✅ Reimbursement request submitted successfully!", "success")
        return redirect(url_for('student_apply'))
    return render_template('student_form.html')

def showName():
    email = session.get('email')
    return get_name_by_email(email)

# Dummy dashboards


@app.route('/student_dashboard')
def student_dashboard():
    email = session.get('email')
    if not email:
        flash("Please log in again.", "warning")
        return redirect(url_for('login'))

    reimbursements = get_reimbursement_by_email(email)
    username = showName()
    return render_template('student.html', reimbursements=reimbursements, username=username )


@app.route('/teacher_dashboard')
def teacher_dashboard():
    return "👨‍🏫 Teacher Dashboard"

@app.route('/hod_dashboard')
def hod_dashboard():
    return "📘 HOD Dashboard"

@app.route('/principal_dashboard')
def principal_dashboard():
    return "🏛️ Principal Dashboard"

@app.route('/md_dashboard')
def md_dashboard():
    return "👔 MD Dashboard"

@app.route('/accountant_dashboard')
def accountant_dashboard():
    return "💼 Accountant Dashboard"

if __name__=='__main__':
    app.run(debug=True)