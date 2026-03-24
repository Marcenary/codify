import csv
import os

from flask import Blueprint
from flask_login import login_required, current_user
from models import Clients, Template
from flask import (
	url_for, redirect,
	render_template,
	session, request,
	jsonify, json
)

# from routes_tasks import Flask, jsonify, render_template, request, abort
# app = Flask(__name__)

def quests_routes(app, db):
    quests_bp = Blueprint("quests", __name__, url_prefix="/quests")
    BASE_DIR = os.path.dirname(__file__)
    CSV_PATH = os.path.join(BASE_DIR, "data", "questions.csv")

    TOPIC_META = {
        "intro":    {"name": "Введение в платформу",        "icon": "bi-mortarboard",  "color": "#6366F1"},
        "webdev":   {"name": "Веб-разработка и ИБ",         "icon": "bi-globe2",       "color": "#0EA5E9"},
        "crypto":   {"name": "Криптография в ИБ",           "icon": "bi-shield-lock",  "color": "#10B981"},
        "vulns":    {"name": "Уязвимости и атаки",          "icon": "bi-bug",          "color": "#EF4444"},
        "seccode":  {"name": "Безопасное программирование", "icon": "bi-code-slash",   "color": "#F59E0B"},
        "platform": {"name": "Архитектура платформы",       "icon": "bi-diagram-3",    "color": "#8B5CF6"},
    }


    def load_questions(topic_id: str) -> list[dict]:
        rows = []
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row["topic_id"] == topic_id:
                    rows.append(row)
        return rows


    def get_all_topics() -> list[dict]:
        counts: dict[str, int] = {}
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                counts[row["topic_id"]] = counts.get(row["topic_id"], 0) + 1
        return [
            {"id": tid, **meta, "count": counts.get(tid, 0)}
            for tid, meta in TOPIC_META.items()
        ]


    # ── Маршруты ──────────────────────────────────────────────────────────────────

    @quests_bp.get("/")
    @login_required
    def list_quests():
        return render_template("quests.html", topics=get_all_topics())


    @quests_bp.route("/quiz/<topic_id>")
    def quiz(topic_id: str):
        if topic_id not in TOPIC_META:
            abort(404)
        meta  = TOPIC_META[topic_id]
        rows  = load_questions(topic_id)

        questions = []
        for i, row in enumerate(rows):
            q = {"index": i, "type": row["type"], "text": row["question"]}
            if row["type"] in ("single", "multi"):
                q["options"] = {
                    "A": row["option_a"],
                    "B": row["option_b"],
                    "C": row["option_c"],
                    "D": row["option_d"],
                }
            questions.append(q)

        return render_template(
            "quiz.html",
            topic_id    = topic_id,
            topic_name  = meta["name"],
            topic_color = meta["color"],
            questions   = questions,
            total       = len(questions),
        )


    @quests_bp.route("/api/check", methods=["POST"])
    def check():
        """
        Принимает JSON:
        {
            "topic_id": "webdev",
            "answers": [
            {"index": 0, "selected": "B"},           // single  — строка
            {"index": 1, "selected": ["A", "C"]},    // multi   — список
            {"index": 2, "selected": "мой ответ"}    // text    — строка
            ]
        }

        Возвращает:
        {
            "score": 2, "total": 3,
            "results": [
            {
                "index": 0,
                "type": "single",
                "correct": true,
                "correct_answer": "B",       // для single — буква; для multi — список букв; для text — эталон
                "explanation": "..."
            }, ...
            ]
        }
        """
        data     = request.get_json(force=True)
        topic_id = data.get("topic_id", "")
        answers  = data.get("answers", [])

        if topic_id not in TOPIC_META:
            return jsonify({"error": "unknown topic"}), 400

        rows       = load_questions(topic_id)
        answer_map = {int(a["index"]): a["selected"] for a in answers}

        results, score = [], 0

        for i, row in enumerate(rows):
            if i not in answer_map:
                continue

            selected    = answer_map[i]
            qtype       = row["type"]
            correct_raw = row["correct"].strip().upper()

            if qtype == "single":
                is_correct     = (str(selected).upper() == correct_raw)
                correct_answer = correct_raw

            elif qtype == "multi":
                correct_set  = set(correct_raw)                                    # {"A","C","D"}
                selected_set = set(selected) if isinstance(selected, list) else set()
                is_correct   = (selected_set == correct_set)
                correct_answer = sorted(correct_set)

            else:  # text
                user    = str(selected).strip().lower()
                pattern = correct_raw.lower()
                is_correct     = (pattern in user) or (user in pattern)
                correct_answer = row["correct"].strip()

            if is_correct:
                score += 1

            results.append({
                "index":          i,
                "type":           qtype,
                "correct":        is_correct,
                "correct_answer": correct_answer,
                "explanation":    row.get("explanation", ""),
            })

        return jsonify({"score": score, "total": len(results), "results": results})
    
    return quests_bp