# ReimBreeze – Smart College Reimbursement Automation System

## 🧩 Problem Statement
The current reimbursement process in colleges is:
- Manual and time-consuming
- Requires physical approvals from multiple authorities
- Lacks document tracking and notification system
- Depends on staff availability, leading to delays and confusion

## ✅ Solution
ReimBreeze is a role-based, OTP-verified reimbursement management system that automates the approval workflow across all stakeholders — from students to accountant — with secure email validation, tracking, and PDF record generation.

---

## ✨ Features
- College email-based OTP verification
- Role-based access: Student, Teacher, HOD, Principal, MD, Accountant
- Reimbursement form with document upload
- Sequential approval flow with comments
- Status tracking and alerts after every action
- Admin dashboard (optional)
- Final downloadable approval summary
- Secure password hashing and session-based login

---

## 🛠 Tech Stack

| Layer        | Technology              |
|--------------|--------------------------|
| Backend      | Flask (Python)           |
| Frontend     | HTML, CSS, Bootstrap     |
| Database     | SQLite                   |
| Authentication | Flask-Login + OTP       |
| Email        | Flask-Mail (Gmail SMTP)  |
| Deployment   | Render / Heroku (Optional)

---

## 📁 File Structure

```
reimbreeze/
├── app.py                 # Main Flask app
├── init_db.py             # Creates SQLite DB
├── requirements.txt       # Project dependencies
├── .env                   # Mail credentials (not shared)
├── templates/             # HTML templates
│   ├── register.html
│   ├── otp.html
│   └── signup.html
├── static/                # CSS/JS if needed
├── users.db               # SQLite database file
└── README.md              # This file
```

---

## 💻 Running Locally

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/reimbreeze.git
cd reimbreeze
```

### 2. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # Mac/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file:

```env
MAIL_USERNAME=yourprojectemail@gmail.com
MAIL_PASSWORD=your_app_password
```

### 5. Initialize the Database
```bash
python init_db.py
```

### 6. Run the App
```bash
python app.py
```

Open in browser: `http://127.0.0.1:5000/register`

---

## 🚀 Future Enhancements
- Google OAuth (college email-only login)
- Admin dashboard
- QR code approval validation
- Digital signature integration
- Flutter mobile app

---

## 📦Deployment
- ✅ Postgres version: https://github.com/MelissaSequeira/postgres-rms
- ✅ Deployed on Render : https://postgres-rms.onrender.com

---

> 💡 Built with love and Flask by Melissa
