from flask import Flask, render_template, request, session, redirect, url_for
import random

app = Flask(__name__)
app.secret_key = "my-secret-key"

QUESTIONS = {
    "logic": [
        {
            "question": "Что становится больше, если от него отнимать?",
            "answers": ["Яма", "Дом", "Дерево", "Книга"],
            "correct": "Яма"
        },
        {
            "question": "Что можно увидеть с закрытыми глазами?",
            "answers": ["Сон", "Телефон", "Дом", "Стол"],
            "correct": "Сон"
        },
        {
            "question": "У Маши было 5 яблок. Она отдала 2. Сколько осталось?",
            "answers": ["2", "3", "4", "5"],
            "correct": "3"
        },
        {
            "question": "Какой месяц идёт после марта?",
            "answers": ["Май", "Апрель", "Июнь", "Февраль"],
            "correct": "Апрель"
        },
        {
            "question": "Что имеет руки, но не может обнять?",
            "answers": ["Часы", "Стул", "Робот", "Дерево"],
            "correct": "Часы"
        }
    ],

    "math": [
        {
            "question": "Сколько будет 7 × 8?",
            "answers": ["54", "56", "64", "48"],
            "correct": "56"
        },
        {
            "question": "Сколько будет 100 − 37?",
            "answers": ["63", "67", "73", "53"],
            "correct": "63"
        },
        {
            "question": "Сколько будет 12 × 5?",
            "answers": ["50", "55", "60", "65"],
            "correct": "60"
        },
        {
            "question": "Сколько будет 81 ÷ 9?",
            "answers": ["7", "8", "9", "10"],
            "correct": "9"
        },
        {
            "question": "Сколько будет 25 + 36?",
            "answers": ["51", "61", "71", "59"],
            "correct": "61"
        }
    ],

    "cartoon": [
        {
            "question": "🐱 Какой мультсериал про котёнка, который постоянно попадает в разные приключения?",
            "answers": ["Том и Джерри", "Губка Боб", "Симпсоны", "Шрек"],
            "correct": "Том и Джерри"
        },
        {
            "question": "🧽 Какой мультсериал происходит в Бикини Боттом?",
            "answers": ["Губка Боб", "Футурама", "Смешарики", "Рик и Морти"],
            "correct": "Губка Боб"
        },
        {
            "question": "🟢 Как зовут зелёного огра из известного мультфильма?",
            "answers": ["Шрек", "Халк", "Фиона", "Осёл"],
            "correct": "Шрек"
        },
        {
            "question": "🧪 Какой мультсериал рассказывает о приключениях Рика и Морти?",
            "answers": ["Рик и Морти", "Гравити Фолз", "Симпсоны", "Футурама"],
            "correct": "Рик и Морти"
        },
        {
            "question": "👽 В каком мультсериале есть персонаж по имени Морти?",
            "answers": ["Рик и Морти", "Губка Боб", "Том и Джерри", "Шрек"],
            "correct": "Рик и Морти"
        }
    ]
}


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        session["name"] = request.form.get("name", "")
        session["age"] = request.form.get("age", "")
        session["crystals"] = 0

        return redirect(url_for("menu"))

    return render_template("index.html", page="start")


@app.route("/menu")
def menu():
    if "name" not in session:
        return redirect(url_for("home"))

    return render_template(
        "index.html",
        page="menu",
        name=session["name"],
        age=session["age"],
        crystals=session.get("crystals", 0)
    )


@app.route("/game/<mode>")
def game(mode):
    if "name" not in session:
        return redirect(url_for("home"))

    if mode not in QUESTIONS:
        return redirect(url_for("menu"))

    questions = QUESTIONS[mode].copy()
    random.shuffle(questions)

    session["mode"] = mode
    session["questions"] = questions
    session["current"] = 0
    session["score"] = 0

    return redirect(url_for("question"))


@app.route("/question", methods=["GET", "POST"])
def question():
    if "questions" not in session:
        return redirect(url_for("menu"))

    questions = session["questions"]
    current = session.get("current", 0)

    if current >= len(questions):
        return redirect(url_for("result"))

    message = ""

    if request.method == "POST":
        answer = request.form.get("answer")

        if answer == questions[current]["correct"]:
            session["score"] = session.get("score", 0) + 1
            session["crystals"] = session.get("crystals", 0) + 1
            message = "correct"
        else:
            message = "wrong"

        session["current"] = current + 1

        return redirect(
            url_for(
                "question",
                result=message
            )
        )

    result = request.args.get("result")

    if current >= len(questions):
        return redirect(url_for("result"))

    q = questions[current]

    return render_template(
        "index.html",
        page="question",
        name=session["name"],
        crystals=session.get("crystals", 0),
        question=q["question"],
        answers=q["answers"],
        number=current + 1,
        total=len(questions),
        result=result
    )


@app.route("/skip")
def skip():
    if "questions" not in session:
        return redirect(url_for("menu"))

    crystals = session.get("crystals", 0)

    if crystals < 1:
        return redirect(url_for("question", result="no_crystals"))

    session["crystals"] = crystals - 1
    session["current"] = session.get("current", 0) + 1

    return redirect(url_for("question", result="skipped"))


@app.route("/result")
def result():
    if "name" not in session:
        return redirect(url_for("home"))

    score = session.get("score", 0)
    total = len(session.get("questions", []))

    return render_template(
        "index.html",
        page="result",
        name=session["name"],
        score=score,
        total=total,
        crystals=session.get("crystals", 0)
    )


@app.route("/restart")
def restart():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
