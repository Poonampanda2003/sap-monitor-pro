from flask import Flask, render_template, request, redirect, url_for, session, send_file, jsonify
from datetime import datetime
import csv
import os
import random
import psutil
import sqlite3



app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Change to something secure in production

@app.route('/')
def home():
    return "Hello, SAP Monitor Pro is running!"

@app.route('/metrics')
def metrics():
    # Simulate random data for testing
    cpu = random.randint(10, 100)  # Random CPU %
    memory = round(random.uniform(2.0, 16.0), 2)  # Random Memory in GB

    if cpu < 50:
        status = "OK"
    elif cpu < 80:
        status = "WARNING"
    else:
        status = "CRITICAL"

    # Save to SQLite DB
    conn = sqlite3.connect('metrics.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO metrics (timestamp, cpu, memory, status)
        VALUES (?, ?, ?, ?)
    ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), cpu, memory, status))
    conn.commit()
    conn.close()

    return {
        "cpu": cpu,
        "memory": memory,
        "status": status
    }


@app.route('/healthcheck')
def healthcheck():
    return jsonify({"status": "Application is healthy"})


@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/history')
def history():
    conn = sqlite3.connect('metrics.db')
    cursor = conn.cursor()
    cursor.execute('SELECT timestamp, cpu, memory, status FROM metrics ORDER BY id DESC LIMIT 20')
    rows = cursor.fetchall()
    conn.close()

    return {
        "history": [
            {"timestamp": r[0], "cpu": r[1], "memory": r[2], "status": r[3]}
            for r in rows
        ]
    }


@app.route('/export')
def export_csv():
    filename = 'exported_metrics.csv'

    # Connect to database and fetch all records
    conn = sqlite3.connect('metrics.db')
    cursor = conn.cursor()
    cursor.execute('SELECT timestamp, cpu, memory, status FROM metrics')
    rows = cursor.fetchall()
    conn.close()

    # Write to CSV
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Timestamp', 'CPU (%)', 'Memory (GB)', 'Status'])  # Header
        writer.writerows(rows)

    response = send_file(filename, as_attachment=True)
    return response

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin123':
            session['user'] = request.form['username']
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid username or password'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    from os import environ
    port = int(environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


