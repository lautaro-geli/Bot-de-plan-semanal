"""
bot.py — App Flask unificada: web + webhook WhatsApp
"""

import os
import json
from flask import Flask, request, render_template, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from bot_logic import handle_command
from meal_data import (
    generate_plan, generate_shopping_list,
    get_available_meals, rebuild_day,
    MEALS_DB, DIAS, ACOMPAÑAMIENTOS_LISTA
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Elegir directorio de datos — probar el volume, caer en /app, caer en BASE_DIR
def _resolve_data_dir():
    candidates = [
        os.getenv("RAILWAY_VOLUME_MOUNT_PATH"),  # volume de Railway
        "/app/data",                              # fallback Railway
        "/app",                                   # fallback Railway raíz
        BASE_DIR,                                 # local
    ]
    for path in candidates:
        if not path:
            continue
        try:
            os.makedirs(path, exist_ok=True)
            test = os.path.join(path, ".write_test")
            with open(test, "w") as f:
                f.write("ok")
            os.remove(test)
            print(f"[Storage] Usando directorio: {path}")
            return path
        except Exception as e:
            print(f"[Storage] {path} no escribible: {e}")
    return BASE_DIR

DATA_DIR  = _resolve_data_dir()
PLAN_FILE = os.path.join(DATA_DIR, "plan_semanal.json")
print(f"[Storage] PLAN_FILE = {PLAN_FILE}")

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)


# ─── Helpers JSON ─────────────────────────────────────────────────────────────

def load_plan():
    if os.path.exists(PLAN_FILE):
        with open(PLAN_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_plan(plan):
    print(f"[Storage] Guardando plan en: {PLAN_FILE}")
    with open(PLAN_FILE, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    print(f"[Storage] Plan guardado OK ({os.path.getsize(PLAN_FILE)} bytes)")


# ─── WEB ──────────────────────────────────────────────────────────────────────

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
    plan = load_plan()
    if day not in plan:
        return jsonify({"error": f"Día '{day}' no encontrado"}), 404
    data = request.get_json(force=True)
    base        = data.get("base",           plan[day]["base"])
    almuerzo_id = data.get("almuerzo_id",    plan[day].get("almuerzo_id"))
    cena_id     = data.get("cena_id",        plan[day].get("cena_id"))
    alm_acomp   = data.get("almuerzo_acomp", plan[day].get("almuerzo_acomp"))
    cen_acomp   = data.get("cena_acomp",     plan[day].get("cena_acomp"))
    rebuilt = rebuild_day(base, almuerzo_id, cena_id, alm_acomp, cen_acomp)
    if rebuilt:
        plan[day] = rebuilt
    else:
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
    meals = get_available_meals(base)
    if not meals:
        return jsonify({"error": "Base no encontrada"}), 404
    return jsonify(meals)


@app.route("/api/meta", methods=["GET"])
def api_meta():
    return jsonify({
        "bases": list(MEALS_DB.keys()),
        "dias": DIAS,
        "acompañamientos": ACOMPAÑAMIENTOS_LISTA
    })


# ─── WHATSAPP ─────────────────────────────────────────────────────────────────

@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    incoming = request.form.get("Body", "").strip()
    from_num = request.form.get("From", "")
    print(f"[WhatsApp] De: {from_num} | Mensaje: '{incoming}'")
    respuesta = handle_command(incoming)
    twiml = MessagingResponse()
    if isinstance(respuesta, list):
        for parte in respuesta:
            twiml.message(parte)
    else:
        twiml.message(respuesta)
    return str(twiml), 200, {"Content-Type": "text/xml"}


@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok", "plan_file": PLAN_FILE,
            "plan_exists": os.path.exists(PLAN_FILE)}, 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", os.getenv("FLASK_PORT", 5000)))
    app.run(host="0.0.0.0", port=port, debug=False)