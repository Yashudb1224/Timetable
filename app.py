from flask import Flask, render_template, request
from datetime import datetime, timedelta
from tabulate import tabulate

app = Flask(__name__)

def calculate_study_time(total_study_hours, total_difficulty, difficulty):
    # Difficulty scale: 1 (easy) to 10 (difficult)
    # Directly proportional study time: easier subjects have shorter study time
    study_time = (int(difficulty) / total_difficulty) * total_study_hours
    return study_time

def calculate_break_duration(difficulty):
    # Difficulty scale: 1 (easy) to 10 (difficult)
    # Directly proportional break duration: easier subjects have shorter breaks
    max_break_duration = 20  # Maximum break duration in minutes
    min_break_duration = 5   # Minimum break duration in minutes
    difficulty_scale = 10    # Maximum difficulty level
    break_duration = min_break_duration + ((int(difficulty) / difficulty_scale) * (max_break_duration - min_break_duration))
    return int(break_duration)

def generate_timetable(subjects, total_study_hours, start_time):
    total_difficulty = sum(int(difficulty) for subject, difficulty in subjects)

    timetable = []
    current_time = start_time
    for i, (subject, difficulty) in enumerate(subjects):
        study_hours = calculate_study_time(total_study_hours, total_difficulty, difficulty)
        break_duration = calculate_break_duration(difficulty)

        # Add subject
        timetable.append([subject, current_time.strftime("%I:%M %p"), (current_time + timedelta(hours=study_hours)).strftime("%I:%M %p")])
        current_time += timedelta(hours=study_hours)

        # Add break after the subject, except for the last one
        if i < len(subjects) - 1:
            timetable.append(["Break", current_time.strftime("%I:%M %p"), (current_time + timedelta(minutes=break_duration)).strftime("%I:%M %p")])
            current_time += timedelta(minutes=break_duration)

    return timetable

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        subjects = []
        total_study_hours = int(request.form['total_study_hours'])
        start_time = datetime.strptime(request.form['start_time'], "%H:%M")

        for key, value in request.form.items():
            if key.startswith('subject_name_'):
                subject_index = key.split('_')[-1]
                subject_name = value
                difficulty = request.form.get(f'difficulty_{subject_index}', '')
                if difficulty:  # Ensure difficulty is provided
                    subjects.append((subject_name, difficulty))

        timetable = generate_timetable(subjects, total_study_hours, start_time)

        headers = ["Activity", "Start Time", "End Time"]
        timetable_html = tabulate(timetable, headers=headers, tablefmt="html")

        return render_template('timetable.html', timetable_html=timetable_html)
    return render_template('index.html')

import time
from threading import Thread

# Pomodoro timer function
def pomodoro_timer():
    # Initial settings for Pomodoro timer (in seconds)
    pomodoro_duration = 25 * 60  # 25 minutes
    break_duration = 5 * 60      # 5 minutes

    while True:
        # Pomodoro timer
        time.sleep(pomodoro_duration)
        print("Pomodoro finished!")

        # Break timer
        time.sleep(break_duration)
        print("Break finished!")

# Start Pomodoro timer in a separate thread
pomodoro_thread = Thread(target=pomodoro_timer)
pomodoro_thread.daemon = True  # Daemonize the thread so it automatically stops on exit
pomodoro_thread.start()


if __name__ == '__main__':
    app.run(debug=True)

import random

# List of motivational quotes
motivational_quotes = [
    "The only way to do great work is to love what you do. - Steve Jobs",
    "Success is not final, failure is not fatal: It is the courage to continue that counts. - Winston Churchill",
    "Believe you can and you're halfway there. - Theodore Roosevelt",
    "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt"
]


def quotes():
    return random.choice(motivational_quotes)
