from flask import Flask, render_template, request, redirect, url_for, session, flash  #application hi flask ka hai
from flask_mail import *  #for email system
import random   #otp generate karne ke liye
from dotenv import load_dotenv
import os
from db import create_users_table, insert_user,get_user_by_email
from werkzeug.security import generate_password_hash, check_password_hash

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

create_users_table()

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
            flash('Login successful', 'success')
            return redirect(url_for(f"{user[4].lower()}_dashboard"))
        else:
            flash('Invalid credentials', 'danger')

    # If it's GET or login failed, show the login form
    return render_template('login.html')

# Dummy dashboards
@app.route('/student_dashboard')
def student_dashboard():
    return "🎓 Student Dashboard"

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