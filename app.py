"""
Planificador Semanal de Comidas — Fase 1
Flask backend
"""

import json
import os
from flask import Flask, jsonify, request, render_template
from meal_data import (
    generate_plan, generate_shopping_list,
    get_available_meals, rebuild_day,
    MEALS_DB, DIAS, ACOMPAÑAMIENTOS_LISTA
)

app = Flask(__name__)
PLAN_FILE = os.path.join(os.path.dirname(__file__), "plan_semanal.json")


# ─── Helpers ─────────────────────────────────────────────────────────────────

def load_plan():
    if os.path.exists(PLAN_FILE):
        with open(PLAN_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_plan(plan):
    with open(PLAN_FILE, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/generate", methods=["POST"])
def api_generate():
    plan = generate_plan()
    save_plan(plan)
    return jsonify({"status": "ok", "plan": plan})


@app.route("/api/plan", methods=["GET"])
def api_get_plan():
    plan = load_plan()
    if not plan:
        return jsonify({"status": "empty", "plan": {}})
    return jsonify({"status": "ok", "plan": plan})


@app.route("/api/plan/<day>", methods=["PUT"])
def api_update_day(day):
    """Update a single day. Accepts partial or full update."""
    plan = load_plan()
    if day not in plan:
        return jsonify({"error": f"Día '{day}' no encontrado"}), 404

    data = request.get_json(force=True)

    # If we received the pieces to rebuild ingredients, do so
    base = data.get("base", plan[day]["base"])
    almuerzo_id = data.get("almuerzo_id", plan[day].get("almuerzo_id"))
    cena_id = data.get("cena_id", plan[day].get("cena_id"))
    alm_acomp = data.get("almuerzo_acomp", plan[day].get("almuerzo_acomp"))
    cen_acomp = data.get("cena_acomp", plan[day].get("cena_acomp"))

    rebuilt = rebuild_day(base, almuerzo_id, cena_id, alm_acomp, cen_acomp)
    if rebuilt:
        plan[day] = rebuilt
    else:
        # Fallback: just update the fields we received
        plan[day].update(data)

    save_plan(plan)
    return jsonify({"status": "ok", "day": day, "data": plan[day]})


@app.route("/api/shopping", methods=["GET"])
def api_shopping():
    plan = load_plan()
    if not plan:
        return jsonify({"status": "empty", "items": []})
    items = generate_shopping_list(plan)
    return jsonify({"status": "ok", "items": items})


@app.route("/api/meals/<base>", methods=["GET"])
def api_get_meals(base):
    """Return available meals for a base ingredient (for edit dropdowns)."""
    meals = get_available_meals(base)
    if not meals:
        return jsonify({"error": "Base no encontrada"}), 404
    return jsonify(meals)


@app.route("/api/meta", methods=["GET"])
def api_meta():
    """Return static metadata used by the frontend."""
    return jsonify({
        "bases": list(MEALS_DB.keys()),
        "dias": DIAS,
        "acompañamientos": ACOMPAÑAMIENTOS_LISTA
    })


# ─── Run ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print("  🍽️  Planificador Semanal de Comidas — Fase 1")
    print("  Abrí tu navegador en: http://localhost:5000")
    print("=" * 55)
    app.run(debug=True, port=5000)