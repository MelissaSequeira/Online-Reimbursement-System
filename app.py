from flask import Flask, render_template, request, redirect, url_for, session, flash  #application hi flask ka hai
from flask_mail import *  #for email system
import random   #otp generate karne ke liye
from dotenv import load_dotenv
import os

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


if __name__=='__main__':
    app.run(debug=True)