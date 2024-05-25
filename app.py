import csv
from flask import Flask, request, render_template, session, redirect, url_for
from datetime import datetime, timedelta
from tabulate import tabulate
import os
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Load user data from JSON file
USER_DATA_FILE = 'user_data.json'

def load_user_data():
    try:
        with open(USER_DATA_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_user_data(data):
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

def register_user(username, password):
    user_data = load_user_data()
    if username in user_data:
        return False  # User already exists
    user_data[username] = password
    save_user_data(user_data)
    return True  # Registration successful

def authenticate_user(username, password):
    user_data = load_user_data()
    if username in user_data and user_data[username] == password:
        return True  # Authentication successful
    return False  # Authentication failed

def calculate_study_time(total_study_hours, total_difficulty, difficulty):
    return (int(difficulty) / total_difficulty) * total_study_hours

def calculate_break_duration(difficulty):
    max_break_duration = 20
    min_break_duration = 5
    difficulty_scale = 10
    return int(min_break_duration + ((int(difficulty) / difficulty_scale) * (max_break_duration - min_break_duration)))

def generate_timetable(subjects, total_study_hours, start_time):
    total_difficulty = sum(int(difficulty) for subject, difficulty in subjects)
    timetable = []
    current_time = start_time
    for i, (subject, difficulty) in enumerate(subjects):
        study_hours = calculate_study_time(total_study_hours, total_difficulty, difficulty)
        break_duration = calculate_break_duration(difficulty)
        timetable.append([subject, current_time.strftime("%I:%M %p"), (current_time + timedelta(hours=study_hours)).strftime("%I:%M %p")])
        current_time += timedelta(hours=study_hours)
        if i < len(subjects) - 1:
            timetable.append(["Break", current_time.strftime("%I:%M %p"), (current_time + timedelta(minutes=break_duration)).strftime("%I:%M %p")])
            current_time += timedelta(minutes=break_duration)
    return timetable

def save_timetable_to_csv(timetable, filename='timetables.csv'):
    with open(filename, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        for subject, start, end in timetable:
            csvwriter.writerow([subject, start, end, datetime.now()])

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        subjects = []
        total_study_hours = int(request.form['total_study_hours'])
        start_time = datetime.strptime(request.form['start_time'], "%H:%M")

        for key, value in request.form.items():
            if key.startswith('subject_name_'):
                subject_index = key.split('_')[-1]
                subject_name = value
                difficulty = request.form.get(f'difficulty_{subject_index}', '')
                if difficulty:
                    subjects.append((subject_name, difficulty))

        timetable = generate_timetable(subjects, total_study_hours, start_time)

        # Save to CSV file
        save_timetable_to_csv(timetable)

        headers = ["Activity", "Start Time", "End Time"]
        timetable_html = tabulate(timetable, headers=headers, tablefmt="html")

        return render_template('timetable.html', timetable_html=timetable_html)
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if register_user(username, password):
            session['username'] = username
            return redirect(url_for('index'))
        else:
            error_message = "Username already exists. Please choose a different username."
            return render_template('register.html', error=error_message)
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if authenticate_user(username, password):
            session['username'] = username
            return redirect(url_for('index'))
        else:
            error_message = "Invalid username or password. Please try again."
            return render_template('login.html', error=error_message)
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
