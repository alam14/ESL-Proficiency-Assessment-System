from flask import Flask, request, render_template_string
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_NAME = "esl_assessment.db"


def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        created_at TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        score INTEGER,
        level TEXT,
        report TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()


questions = [
    {
        "question": "Choose the correct sentence:",
        "options": ["He go to school.", "He goes to school.", "He going school.", "He gone school."],
        "answer": "He goes to school."
    },
    {
        "question": "What is the past tense of 'eat'?",
        "options": ["eated", "ate", "eating", "eats"],
        "answer": "ate"
    },
    {
        "question": "Choose the correct word: I am interested ___ learning English.",
        "options": ["on", "at", "in", "for"],
        "answer": "in"
    },
    {
        "question": "Which sentence is correct?",
        "options": ["She have a book.", "She has a book.", "She having book.", "She had book now."],
        "answer": "She has a book."
    },
    {
        "question": "What does 'improve' mean?",
        "options": ["to make better", "to destroy", "to forget", "to stop"],
        "answer": "to make better"
    },
    {
        "question": "Choose the correct sentence:",
        "options": ["They are playing football.", "They is playing football.", "They playing football.", "They plays football."],
        "answer": "They are playing football."
    },
    {
        "question": "What is the opposite of 'difficult'?",
        "options": ["hard", "simple", "heavy", "strong"],
        "answer": "simple"
    },
    {
        "question": "Choose the correct form: If I study hard, I ___ pass.",
        "options": ["will", "would", "was", "am"],
        "answer": "will"
    }
]


def assign_level(score):
    if score <= 2:
        return "Level 1 - Beginner"
    elif score <= 4:
        return "Level 2 - Elementary"
    elif score <= 6:
        return "Level 3 - Intermediate"
    else:
        return "Level 4 - Advanced"


@app.route("/")
def home():
    return render_template_string("""
    <html>
    <head>
        <title>ESL Proficiency Assessment System</title>
        <style>
            body { font-family: Arial; background: #f4f7fb; margin: 40px; }
            .box { background: white; padding: 30px; border-radius: 12px; width: 600px; margin: auto; box-shadow: 0 0 10px #ccc; }
            h1 { color: #0b2d5c; text-align: center; }
            input { width: 100%; padding: 10px; margin: 10px 0; }
            button { background: #0b2d5c; color: white; padding: 12px; border: none; width: 100%; font-size: 16px; border-radius: 6px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>ESL Proficiency Assessment System</h1>
            <form action="/start_test" method="post">
                <label>Student Name:</label>
                <input type="text" name="name" required>

                <label>Email:</label>
                <input type="email" name="email" required>

                <button type="submit">Start ESL Test</button>
            </form>
        </div>
    </body>
    </html>
    """)


@app.route("/start_test", methods=["POST"])
def start_test():
    name = request.form["name"]
    email = request.form["email"]

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO students (name, email, created_at) VALUES (?, ?, ?)",
        (name, email, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )

    student_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return render_template_string("""
    <html>
    <head>
        <title>ESL Test</title>
        <style>
            body { font-family: Arial; background: #f4f7fb; margin: 30px; }
            .box { background: white; padding: 30px; border-radius: 12px; width: 800px; margin: auto; box-shadow: 0 0 10px #ccc; }
            h1 { color: #0b2d5c; text-align: center; }
            .question { margin-bottom: 25px; padding: 15px; border-bottom: 1px solid #ddd; }
            label { display: block; margin: 8px 0; cursor: pointer; }
            button { background: #0b2d5c; color: white; padding: 12px; border: none; width: 100%; font-size: 16px; border-radius: 6px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>ESL Test</h1>

            <form action="/submit_test" method="post">
                <input type="hidden" name="student_id" value="{{ student_id }}">

                {% for q in questions %}
                <div class="question">
                    <p><b>{{ loop.index }}. {{ q.question }}</b></p>

                    {% set question_number = loop.index0 %}

                    {% for option in q.options %}
                    <label>
                        <input type="radio" name="q{{ question_number }}" value="{{ option }}" required>
                        {{ option }}
                    </label>
                    {% endfor %}
                </div>
                {% endfor %}

                <button type="submit">Submit Test</button>
            </form>
        </div>
    </body>
    </html>
    """, questions=questions, student_id=student_id)


@app.route("/submit_test", methods=["POST"])
def submit_test():
    student_id = request.form["student_id"]
    score = 0

    for i, q in enumerate(questions):
        selected_answer = request.form.get(f"q{i}")
        if selected_answer == q["answer"]:
            score += 1

    level = assign_level(score)

    report = f"""
ESL Proficiency Assessment Report

Student ID: {student_id}
Total Questions: {len(questions)}
Score: {score} out of {len(questions)}
Assigned ESL Level: {level}

Interpretation:
The student has been evaluated automatically based on the ESL test responses.
The assigned level can be used for ESL course placement.
"""

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO results (student_id, score, level, report, created_at) VALUES (?, ?, ?, ?, ?)",
        (student_id, score, level, report, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )

    conn.commit()
    conn.close()

    return render_template_string("""
    <html>
    <head>
        <title>ESL Result</title>
        <style>
            body { font-family: Arial; background: #f4f7fb; margin: 40px; }
            .box { background: white; padding: 30px; border-radius: 12px; width: 700px; margin: auto; box-shadow: 0 0 10px #ccc; }
            h1 { color: #0b2d5c; text-align: center; }
            .result { font-size: 20px; background: #e8f0ff; padding: 20px; border-radius: 10px; }
            a { display: block; text-align: center; margin-top: 20px; color: #0b2d5c; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>ESL Test Report</h1>

            <div class="result">
                <p><b>Score:</b> {{ score }} / {{ total }}</p>
                <p><b>Assigned Level:</b> {{ level }}</p>
            </div>

            <h3>Report</h3>
            <pre>{{ report }}</pre>

            <a href="/">Take Another Test</a>
            <a href="/results">View All Results</a>
        </div>
    </body>
    </html>
    """, score=score, total=len(questions), level=level, report=report)


@app.route("/results")
def view_results():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT students.name, students.email, results.score, results.level, results.created_at
    FROM results
    JOIN students ON students.id = results.student_id
    ORDER BY results.id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return render_template_string("""
    <html>
    <head>
        <title>All ESL Results</title>
        <style>
            body { font-family: Arial; background: #f4f7fb; margin: 40px; }
            h1 { color: #0b2d5c; text-align: center; }
            table { width: 100%; border-collapse: collapse; background: white; }
            th, td { border: 1px solid #ccc; padding: 10px; text-align: left; }
            th { background: #0b2d5c; color: white; }
            a { display: block; margin-bottom: 20px; color: #0b2d5c; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>All ESL Assessment Results</h1>
        <a href="/">Back to Home</a>

        <table>
            <tr>
                <th>Student Name</th>
                <th>Email</th>
                <th>Score</th>
                <th>ESL Level</th>
                <th>Date</th>
            </tr>

            {% for row in rows %}
            <tr>
                <td>{{ row[0] }}</td>
                <td>{{ row[1] }}</td>
                <td>{{ row[2] }}</td>
                <td>{{ row[3] }}</td>
                <td>{{ row[4] }}</td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """, rows=rows)


if __name__ == "__main__":
    create_database()
if __name__ == "__main__":
    create_database()
    app.run(host="0.0.0.0", port=10000)