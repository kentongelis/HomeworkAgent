from flask import Flask, render_template, request, jsonify
from repo import get_repo
from tutor import MarkdownTutor

app = Flask(__name__)

active_tutors = {}


@app.route("/")
def homepage():
    return render_template("home.html")


@app.route("/tutor")
def tutor():
    path = request.args.get("path")
    parts = path.split("/")
    result = "/".join(parts[3:5])

    repo = get_repo(result)

    tutors = []
    for name, markdown_text in repo.items():
        tutor = MarkdownTutor(markdown_text, name)
        tutors.append(tutor)
        active_tutors[name] = tutor

    return render_template("tutor.html", tutors=tutors)


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    name = data["name"]
    question = data["question"]
    tutor = active_tutors.get(name)

    if not tutor:
        return jsonify({"error": "Tutor not found"}), 404

    answer = tutor.ask(question)
    return jsonify({"answer": answer})


@app.route("/quiz", methods=["POST"])
def quiz():
    data = request.get_json()
    name = data["name"]
    action = data.get("action", "start")
    answer = data.get("answer")

    tutor = active_tutors.get(name)
    if not tutor:
        return jsonify({"error": "Tutor not found"}), 404

    if action == "start":
        quiz = tutor.generate_quiz()
        question = tutor.ask_quiz_question()
        return jsonify({"question": question})
    elif action == "answer":
        feedback = tutor.answer_quiz(answer)
        next_q = tutor.ask_quiz_question()
        return jsonify({"feedback": feedback, "next": next_q})
    else:
        return jsonify({"error": "Invalid quiz action"}), 400


if __name__ == "__main__":
    app.run(debug=True, port=3000)
