"""
bot_logic.py — Lógica de comandos y formateo de mensajes para WhatsApp
Se mantiene separado del webhook para facilitar testing.
"""

import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

PLAN_FILE = os.path.join(os.path.dirname(__file__), "plan_semanal.json")
TZ = ZoneInfo("America/Argentina/Buenos_Aires")

DIAS_ORDER = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]

CATEGORY_META = {
    "carnes":   "🥩 *CARNES Y PROTEÍNAS*",
    "verduras": "🥦 *VERDURAS Y FRUTAS*",
    "lácteos":  "🧀 *LÁCTEOS*",
    "secos":    "🌾 *SECOS Y ALMACÉN*",
    "otros":    "🫙 *CONDIMENTOS Y OTROS*",
}

BASE_EMOJI = {
    "carne vacuna": "🥩",
    "pollo":        "🍗",
    "pescado":      "🐟",
    "legumbres":    "🫘",
}


# ─── Carga de datos ───────────────────────────────────────────────────────────

def load_plan():
    if not os.path.exists(PLAN_FILE):
        return None
    with open(PLAN_FILE, encoding="utf-8") as f:
        return json.load(f)


def get_today_name():
    """Devuelve el nombre del día actual en español (ej: 'lunes')."""
    now = datetime.now(tz=TZ)
    # weekday(): 0=Monday … 6=Sunday
    return DIAS_ORDER[now.weekday()]


# ─── Comandos ─────────────────────────────────────────────────────────────────

def cmd_menu():
    return (
        "🍽️ *Planificador Semanal de Comidas*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Comandos disponibles:\n\n"
        "📅 *plan* → Plan semanal completo\n"
        "🛒 *compras* → Lista de compras de la semana\n"
        "☀️ *hoy* → Qué hay para comer hoy\n"
        "📋 *menu* → Esta pantalla de ayuda\n\n"
        "_Familia · 5 personas · cocina argentina_ 🇦🇷"
    )


def cmd_hoy():
    plan = load_plan()
    if not plan:
        return "⚠️ No hay un plan generado todavía. Abrí la web y generá uno primero."

    dia = get_today_name()
    day = plan.get(dia)
    if not day:
        return f"⚠️ No encontré el día '{dia}' en el plan."

    base = day.get("base", "")
    emoji = BASE_EMOJI.get(base, "🍴")
    now = datetime.now(tz=TZ)

    return (
        f"☀️ *{dia.upper()}* — {now.strftime('%d/%m/%Y')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{emoji} Base del día: _{base.title()}_\n\n"
        f"🌤️ *Almuerzo*\n{day.get('almuerzo', '—')}\n\n"
        f"🌙 *Cena*\n{day.get('cena', '—')}"
    )


def cmd_plan():
    plan = load_plan()
    if not plan:
        return "⚠️ No hay un plan generado todavía. Abrí la web y generá uno primero."

    today = get_today_name()
    lines = ["📅 *PLAN SEMANAL*\n━━━━━━━━━━━━━━━━━━━━━━"]

    for dia in DIAS_ORDER:
        day = plan.get(dia)
        if not day:
            continue

        base  = day.get("base", "")
        emoji = BASE_EMOJI.get(base, "🍴")
        marker = " ◀ hoy" if dia == today else ""

        lines.append(
            f"\n*{dia.upper()}*{marker}\n"
            f"{emoji} _{base.title()}_\n"
            f"☀️ {day.get('almuerzo', '—')}\n"
            f"🌙 {day.get('cena', '—')}"
        )

    return "\n".join(lines)


def cmd_compras():
    """Devuelve lista de mensajes para no superar el límite de 1600 chars de Twilio."""
    plan = load_plan()
    if not plan:
        return ["⚠️ No hay un plan generado todavía. Abrí la web y generá uno primero."]

    from meal_data import generate_shopping_list
    items = generate_shopping_list(plan)

    if not items:
        return ["⚠️ La lista de compras está vacía."]

    grouped = {}
    for item in items:
        cat = item.get("categoria", "otros")
        grouped.setdefault(cat, []).append(item)

    cat_order = ["carnes", "verduras", "lácteos", "secos", "otros"]
    total = sum(len(v) for v in grouped.values())

    # Mensaje 1 — encabezado + carnes + verduras
    msg1_lines = [f"🛒 *LISTA DE COMPRAS* (1/2)\n_{total} productos · 5 personas_\n━━━━━━━━━━━━━━━━━━━━━━"]
    for cat in ["carnes", "verduras"]:
        if cat not in grouped:
            continue
        msg1_lines.append(f"\n{CATEGORY_META.get(cat, cat.upper())}")
        for item in grouped[cat]:
            msg1_lines.append(f"• {item['nombre']} — {item['cantidad']}")

    # Mensaje 2 — lácteos + secos + otros
    msg2_lines = ["🛒 *LISTA DE COMPRAS* (2/2)\n━━━━━━━━━━━━━━━━━━━━━━"]
    for cat in ["lácteos", "secos", "otros"]:
        if cat not in grouped:
            continue
        msg2_lines.append(f"\n{CATEGORY_META.get(cat, cat.upper())}")
        for item in grouped[cat]:
            msg2_lines.append(f"• {item['nombre']} — {item['cantidad']}")

    return ["\n".join(msg1_lines), "\n".join(msg2_lines)]


def cmd_unknown(texto):
    return (
        f"🤔 No entendí «{texto}».\n\n"
        "Escribí *menu* para ver los comandos disponibles."
    )


# ─── Router principal ─────────────────────────────────────────────────────────

def handle_command(incoming: str) -> str:
    """Recibe el texto del mensaje y devuelve la respuesta adecuada."""
    cmd = incoming.strip().lower()

    # Normalizar variantes comunes
    aliases = {
        "menú": "menu", "ayuda": "menu", "help": "menu", "inicio": "menu",
        "hoy": "hoy", "hoy?": "hoy", "que hay hoy": "hoy", "qué hay hoy": "hoy",
        "plan": "plan", "semana": "plan", "semanal": "plan",
        "compras": "compras", "lista": "compras", "lista de compras": "compras",
        "shopping": "compras",
    }
    cmd = aliases.get(cmd, cmd)

    if cmd == "menu":
        return cmd_menu()
    if cmd == "hoy":
        return cmd_hoy()
    if cmd == "plan":
        return cmd_plan()
    if cmd == "compras":
        return cmd_compras()

    return cmd_unknown(incoming.strip())