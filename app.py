from flask import Flask, render_template, session, redirect, url_for, request, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = 'matcha-grader-secret-key-2024'

# ── DATA ────────────────────────────────────────────────────────────────────────

def load_data():
    """Load lesson and quiz data from JSON."""
    data_path = os.path.join(app.root_path, 'data.json')
    with open(data_path, 'r') as f:
        return json.load(f)

DATA = load_data()
LESSONS = DATA['lessons']
QUIZ_QUESTIONS = DATA['quiz_questions']
TOTAL_LESSONS = len(LESSONS)
TOTAL_QUESTIONS = len(QUIZ_QUESTIONS)


def init_session():
    """Initialise session storage for a fresh user."""
    if 'user_data' not in session:
        session['user_data'] = {
            'start_time': None,
            'lesson_visits': {},   # lesson_id -> ISO timestamp
            'quiz_answers': {},    # question_id -> chosen key
            'score': 0,
            'quiz_complete': False
        }


# ── ROUTES ───────────────────────────────────────────────────────────────────────

@app.route('/')
def home():
    init_session()
    return render_template('home.html')


@app.route('/start', methods=['POST'])
def start():
    """Record that a new user session has begun."""
    init_session()
    session['user_data']['start_time'] = datetime.now().isoformat()
    session['user_data']['lesson_visits'] = {}
    session['user_data']['quiz_answers'] = {}
    session['user_data']['score'] = 0
    session['user_data']['quiz_complete'] = False
    session.modified = True
    dest = request.form.get('destination', 'learn')
    if dest == 'quiz':
        return redirect(url_for('quiz', question_num=1))
    return redirect(url_for('learn', lesson_num=1))


@app.route('/learn/<int:lesson_num>')
def learn(lesson_num):
    init_session()
    if lesson_num < 1 or lesson_num > TOTAL_LESSONS:
        return redirect(url_for('learn', lesson_num=1))

    # Record visit timestamp
    ud = session['user_data']
    ud['lesson_visits'][str(lesson_num)] = datetime.now().isoformat()
    session.modified = True

    lesson = LESSONS[lesson_num - 1]
    next_num = lesson_num + 1 if lesson_num < TOTAL_LESSONS else None
    prev_num = lesson_num - 1 if lesson_num > 1 else None

    return render_template(
        'lesson.html',
        lesson=lesson,
        lesson_num=lesson_num,
        total_lessons=TOTAL_LESSONS,
        next_num=next_num,
        prev_num=prev_num
    )


@app.route('/quiz/<int:question_num>', methods=['GET'])
def quiz(question_num):
    init_session()
    if question_num < 1 or question_num > TOTAL_QUESTIONS:
        return redirect(url_for('quiz', question_num=1))

    question = QUIZ_QUESTIONS[question_num - 1]
    return render_template(
        'quiz.html',
        question=question,
        question_num=question_num,
        total_questions=TOTAL_QUESTIONS
    )


@app.route('/quiz/<int:question_num>/answer', methods=['POST'])
def answer(question_num):
    """Record the user's answer and return feedback."""
    init_session()
    if question_num < 1 or question_num > TOTAL_QUESTIONS:
        return redirect(url_for('quiz', question_num=1))

    question = QUIZ_QUESTIONS[question_num - 1]
    chosen = request.form.get('answer', '')

    # Store answer
    ud = session['user_data']
    ud['quiz_answers'][str(question_num)] = chosen

    is_correct = (chosen == question['correct'])
    if is_correct:
        ud['score'] = ud.get('score', 0) + 1

    session.modified = True

    is_last = (question_num == TOTAL_QUESTIONS)
    next_num = question_num + 1 if not is_last else None

    feedback = question['feedback']['correct' if is_correct else 'incorrect']

    return render_template(
        'feedback.html',
        question=question,
        question_num=question_num,
        total_questions=TOTAL_QUESTIONS,
        is_correct=is_correct,
        feedback=feedback,
        chosen=chosen,
        next_num=next_num,
        is_last=is_last
    )


@app.route('/results')
def results():
    init_session()
    ud = session['user_data']
    ud['quiz_complete'] = True
    session.modified = True

    score = ud.get('score', 0)
    return render_template('results.html', score=score, total=TOTAL_QUESTIONS)


# ── DEBUG / ADMIN ────────────────────────────────────────────────────────────────

@app.route('/session-data')
def session_data():
    """Quick debug endpoint to inspect stored user data."""
    return jsonify(session.get('user_data', {}))


if __name__ == '__main__':
    app.run(debug=True, port=5000)
