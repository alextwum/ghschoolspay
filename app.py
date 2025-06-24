from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

DATABASE = 'payments.db'
ADMIN_USER = os.getenv("ADMIN_USER")
ADMIN_PASS = os.getenv("ADMIN_PASS")

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        name TEXT,
        email TEXT,
        amount INTEGER,
        reference TEXT,
        status TEXT,
        timestamp TEXT
    )''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/payment')
def payment():
    return render_template('payment.html')

@app.route('/admin', methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == ADMIN_USER and password == ADMIN_PASS:
            session["admin_logged_in"] = True
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid credentials"
    return render_template("admin_login.html", error=error)

@app.route('/dashboard')
def dashboard():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM payments ORDER BY id DESC")
    records = c.fetchall()
    conn.close()
    return render_template('dashboard.html', records=records)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("admin_login"))

@app.route('/thank_you')
def thank_you():
    student_id = request.args.get('student_id')
    return render_template('thank_you.html', student_id=student_id)

@app.route('/save_payment', methods=['POST'])
def save_payment():
    data = request.get_json()
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''INSERT INTO payments (student_id, name, email, amount, reference, status, timestamp)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (data['student_id'], data['name'], data['email'], data['amount'],
               data['reference'], data['status'], datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    return {'message': 'Payment saved'}

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
