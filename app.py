from flask import Flask, render_template, session, redirect, url_for, request, jsonify
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'matcha-grader-secret-key-2024'

# ── DATA ────────────────────────────────────────────────────────────────────────

LESSONS = [
    {
        "id": 1,
        "title": "Lesson 1: Color is Your Best Clue",
        "type": "text",
        "content": [
            "The single most reliable visual indicator of matcha quality is color.",
            "High-grade ceremonial matcha is a deep, vibrant green. Lower-grade culinary matcha shifts toward yellow-green or olive tones. This happens because premium matcha is shade-grown longer, producing more chlorophyll."
        ],
        "has_gradient": True
    },
    {
        "id": 2,
        "title": "Lesson 2: Texture Tells the Story",
        "type": "text",
        "content": [
            "Beyond color, powder fineness separates grades.",
            "Ceremonial matcha is stone-ground to particles around 5–10 microns - finer than baby powder. It feels silky between your fingers. Culinary matcha has larger, grittier particles that are visible to the naked eye.",
            "A quick 'smear test' on paper can reveal the difference."
        ],
        "has_gradient": False
    },
    {
        "id": 3,
        "title": "Summary",
        "type": "summary",
        "bullets": [
            "Color: Deep emerald green = high grade, yellow-olive = low grade",
            "Texture: Silky fine powder = ceremonial, visible grains = culinary",
            "Smear test: Smooth streak (good) vs grainy line (low)"
        ]
    },
    {
        "id": 4,
        "title": "4 Matcha Grades",
        "type": "grades",
        "subtitle": "Notice how color shifts from deep emerald to dull olive - and how texture coarsens.",
        "grades": [
            {
                "label": "Grade A", "name": "Premium Ceremonial",
                "desc": "Pure emerald green + ultra-fine silky particles",
                "color": "#2d6a1f",
                "img": "img/grade_a.jpg"
            },
            {
                "label": "Grade B", "name": "Ceremonial",
                "desc": "Vibrant green + fine powder, slight texture",
                "color": "#4a8c2a",
                "img": "img/grade_b.jpg"
            },
            {
                "label": "Grade C", "name": "Premium Culinary",
                "desc": "Muted green + visible coarser grains",
                "color": "#7aaa35",
                "img": "img/grade_c.jpg"
            },
            {
                "label": "Grade D", "name": "Culinary",
                "desc": "Yellow-green + coarse, gritty texture",
                "color": "#a8b830",
                "img": "img/grade_d.jpg"
            }
        ]
    },
    {
        "id": 5,
        "title": "Matcha in Drinks",
        "type": "drinks",
        "content": [
            "You can also judge matcha quality after it is whisked into a drink.",
            "A ceremonial-grade latte will have a vivid, saturated green hue - think bright jade. A culinary-grade latte tends toward a muted, brownish or yellowish green.",
            "The color difference becomes especially obvious in iced drinks, where the matcha sits against a white milk background."
        ],
        "tip": "Always compare under the same light source for accuracy.",
        "img_ceremonial": "img/drink_ceremonial.jpg",
        "img_culinary": "img/drink_culinary.jpg"
    },
    {
        "id": 6,
        "title": "Foam",
        "type": "foam",
        "content": [
            "Higher-quality matcha produces more foam because it contains more saponins (natural foaming compounds) and is ground much finer, trapping air more effectively when whisked.",
            "The result is a dense, creamy microfoam that holds its shape. Culinary-grade matcha produces little to no foam and a flat surface."
        ],
        "img": "img/foam.jpg"
    },
    {
        "id": 7,
        "title": "Time for practice!",
        "type": "final",
        "content": ["You've learned how to visually grade matcha by color, texture, and foam. Now put your skills to the test!"]
    }
]

TOTAL_LESSONS = len(LESSONS)

QUIZ_QUESTIONS = [
    {
        "id": 1,
        "title": "Identify This Matcha",
        "text": "Look at this sample. Is it ceremonial or culinary grade? Select your answer and give one visual reason.",
        "type": "image_choice",
        "image_desc": "ceremonial_powder",
        "options": [
            {"key": "A", "text": "Ceremonial Grade"},
            {"key": "B", "text": "Culinary Grade"}
        ],
        "correct": "A",
        "feedback": {
            "correct": {
                "title": "You are correct! 🎉",
                "body": "This is a typical ceremonial grade matcha, with a vibrant green color and fine particles. Culinary matcha tends to look more yellowish and dull."
            },
            "incorrect": {
                "title": "You are wrong! 😭",
                "body": "This is actually ceremonial grade matcha, which is brighter green and finer in texture. The vivid green hue and silky powder are the key giveaways."
            }
        }
    },
    {
        "id": 2,
        "title": "Rank These Matcha Samples",
        "text": "Rank these three matcha powder samples from highest to lowest grade.",
        "type": "rank_choice",
        "image_desc": "three_samples",
        "options": [
            {"key": "A", "text": "Right > Left > Middle"},
            {"key": "B", "text": "Middle > Right > Left"},
            {"key": "C", "text": "Right > Middle > Left"}
        ],
        "correct": "B",
        "feedback": {
            "correct": {
                "title": "You are correct! 🎉",
                "body": "The middle sample is highest quality due to its deep emerald green and fine texture. The right sample is slightly less vibrant but still good. The left sample is lowest quality due to yellow tones and coarser texture.",
                "tip": "The more vibrant and saturated the green, the more chlorophyll from shade-growing, which signals a higher grade."
            },
            "incorrect": {
                "title": "You are wrong! 😭",
                "body": "Correct answer: Middle > Right > Left. The middle sample's deep emerald green and fine texture mark it as the highest grade. Look for deeper green and finer texture to identify higher grade matcha.",
                "tip": "The more vibrant and saturated the green, the more chlorophyll from shade-growing, which signals a higher grade."
            }
        }
    },
    {
        "id": 3,
        "title": "Which Bowl is Higher Quality?",
        "text": "Which bowl was made with higher-grade matcha? Base your answer on color and foam.",
        "type": "bowl_choice",
        "image_desc": "two_bowls",
        "options": [
            {"key": "A", "text": "Bowl X"},
            {"key": "B", "text": "Bowl Y"}
        ],
        "correct": "A",
        "feedback": {
            "correct": {
                "title": "You are correct! 🎉",
                "body": "Bowl X has a brighter, more vivid jade green color, while Bowl Y leans darker and more olive-brown. Bowl X also has a fine, creamy froth with tiny uniform bubbles - only possible when the powder is ground finely enough to whisk properly.",
                "tip": "In whisked matcha, froth quality is a bonus visual indicator on top of color."
            },
            "incorrect": {
                "title": "You are wrong! 😭",
                "body": "Bowl X is higher quality because of its vibrant green color and smooth foam texture. Bowl Y's flat, foam-free surface suggests coarser particles that couldn't hold air.",
                "tip": "In whisked matcha, froth quality is a bonus visual indicator on top of color."
            }
        }
    }
]

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
