from flask import Flask, render_template, request, redirect, send_from_directory, url_for, session, flash  #application hi flask ka hai
from flask_mail import *  #for email system
import random   #otp generate karne ke liye
from dotenv import load_dotenv
import os
#create_users_table, insert_user,get_user_by_email, reimb_db, insert_reimbursement, get_reimbursement_by_email,get_name_by_email,get_pending_requests_for_teacher, update_teacher_approval
from db import *
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
        if not (email.endswith('fcrit.ac.in') or email.endswith('gmail.com')):
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

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    if session.get('role') not in ['Teacher', 'HOD', 'Principal', 'MD', 'Accountant', 'Student']:
        flash("Access denied", "danger")
        return redirect(url_for('login'))
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)



@app.route('/teacher_dashboard')
def teacher_dashboard():
    if session.get('role') != 'Teacher':
        flash('Access Denied', 'danger')
        return redirect(url_for('login'))

    requests = get_pending_requests_for_teacher()
    return render_template('teacher_dashboard.html', requests=requests)

@app.route('/teacher_approve/<int:req_id>', methods=['POST'])
def teacher_approve(req_id):
    if session.get('role') != 'Teacher':
        flash('Access Denied', 'danger')
        return redirect(url_for('login'))

    remarks = request.form['remarks']
    action = request.form['action']

    if action == 'approve':
        update_teacher_approval(req_id, 'Approved', remarks)
        flash('✅ Request approved and sent to HOD', 'success')
    elif action == 'reject':
        update_teacher_approval(req_id, 'Rejected', remarks)
        flash('❌ Request rejected', 'danger')

    return redirect(url_for('teacher_dashboard'))

@app.route('/hod_dashboard')
def hod_dashboard():
    if session.get('role')!='HOD':
        flash('Access denied', 'danger')
        return redirect(url_for('login'))
    requests=get_pending_requests_for_hod();
    return render_template('Hod_dashboard.html', requests=requests)

@app.route('/hod_approve/<int:req_id>',methods=['POST'])
def hod_approve(req_id):
    if session.get('role')!='HOD':
        flash('Access denied', 'danger')
        return redirect(url_for('login'))
    remarks= request.form['remarks']
    action = request.form['action']
    if action=='approve':
        update_hod_approval(req_id,'approved',remarks)
        flash('✅ Request approved and sent to Principal', 'success')
    elif action == 'reject':
        update_hod_approval(req_id, 'Rejected', remarks)
        flash('❌ Request rejected', 'danger')
    return redirect(url_for('hod_dashboard'))

@app.route('/principal_dashboard')
def principal_dashboard():
    if session.get('role')!='Principal':
        flash('Access denied', 'danger')
        return redirect(url_for('login'))
    requests=get_pending_requests_for_principal();
    return render_template('Principal_dashboard.html', requests=requests)

@app.route('/principal_approve/<int:req_id>',methods=['POST'])
def principal_approve(req_id):
    if session.get('role')!='Principal':
        flash('Access denied', 'danger')
        return redirect(url_for('login'))
    remarks= request.form['remarks']
    action = request.form['action']
    if action=='approve':
        update_principal_approval(req_id,'approved',remarks)
        flash('✅ Request approved and sent to MD', 'success')
    elif action == 'reject':
        update_principal_approval(req_id, 'Rejected', remarks)
        flash('❌ Request rejected', 'danger')
    return redirect(url_for('principal_dashboard'))


@app.route('/md_dashboard')
def md_dashboard():
    if session.get('role')!='MD':
        flash('Access denied', 'danger')
        return redirect(url_for('login'))
    requests=get_pending_requests_for_md();
    return render_template('MD_dashboard.html', requests=requests)

@app.route('/md_approve/<int:req_id>',methods=['POST'])
def md_approve(req_id):
    if session.get('role')!='MD':
        flash('Access denied', 'danger')
        return redirect(url_for('login'))
    remarks= request.form['remarks']
    action = request.form['action']
    if action=='approve':
        update_md_approval(req_id,'approved',remarks)
        flash('✅ Request approved and sent to accountant', 'success')
    elif action == 'reject':
        update_md_approval(req_id, 'Rejected', remarks)
        flash('❌ Request rejected', 'danger')
    return redirect(url_for('md_dashboard'))

@app.route('/accountant_dashboard')
def accountant_dashboard():
    if session.get('role')!='Accountant':
        flash('Access Denied','danger')
        return redirect(url_for('login'))
    requests = get_pending_requests_for_accountant()
    return render_template('Accountant_dashboard.html', requests=requests)

@app.route('/accountant_approve/<int:req_id>',methods=['POST'])
def accountant_approve(req_id):
    if session.get('role') != 'Accountant':
        flash('Access Denied', 'danger')
        return redirect(url_for('login'))

    remarks = request.form['remarks']
    action = request.form['action']
    status = 'Approved' if action == 'approve' else 'Rejected'
    update_accountant_approval(req_id, status, remarks)
    conn=connect_db()
    cur=conn.cursor()
    cur.execute("SELECT email FROM reimb_form WHERE id=?", (req_id,))
    student_email = cur.fetchone()[0]
    conn.close()
    msg = Message('Reimbursement Status', sender=app.config['MAIL_USERNAME'], recipients=[student_email])
    msg.body = f"Your reimbursement request has been {'approved and processed' if status == 'Approved' else 'rejected by accountant'}.\n\nRemarks: {remarks}"
    mail.send(msg)

    flash('✅ Final status saved and student notified.', 'success')
    return redirect(url_for('accountant_dashboard'))

if __name__=='__main__':
    app.run(debug=True)