"""
run.py — Script principal Fase 2
Usa importlib para cargar módulos por ruta absoluta (evita problemas de sys.path en Windows)
"""

import os
import sys
import time
import threading
import signal
import logging
import importlib.util

# ── Ruta absoluta de este archivo ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Cargar .env manualmente ───────────────────────────────────────────────────
env_path = os.path.join(BASE_DIR, ".env")
if os.path.exists(env_path):
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip())

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

PORT = int(os.getenv("FLASK_PORT", 5000))


# ── Cargar cualquier módulo local por ruta absoluta ───────────────────────────
def load_local(name, filename):
    path = os.path.join(BASE_DIR, filename)
    if not os.path.exists(path):
        print(f"\n❌ No se encontró el archivo: {path}")
        sys.exit(1)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# ── Validaciones ──────────────────────────────────────────────────────────────
def check_env():
    required = [
        "TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN",
        "TWILIO_WHATSAPP_NUMBER", "TO_WHATSAPP_NUMBER",
        "NGROK_AUTHTOKEN", "NGROK_DOMAIN",
    ]
    missing = [k for k in required
               if not os.getenv(k, "").strip()
               or "XXXX" in os.getenv(k, "")
               or "xxxxxxx" in os.getenv(k, "")]
    if missing:
        print("\n❌ Faltan configurar estas variables en .env:\n")
        for m in missing:
            print(f"   • {m}")
        print("\n👉 Editá el archivo .env con tus credenciales reales.\n")
        sys.exit(1)


def check_plan():
    if not os.path.exists(os.path.join(BASE_DIR, "plan_semanal.json")):
        print("\n⚠️  No existe plan_semanal.json")
        print("   Abrí http://localhost:5000 y generá un plan primero.\n")


# ── Flask en hilo ─────────────────────────────────────────────────────────────
def run_flask():
    load_local("meal_data", "meal_data.py")
    load_local("bot_logic", "bot_logic.py")
    bot = load_local("bot", "bot.py")
    bot.app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)


# ── ngrok ─────────────────────────────────────────────────────────────────────
def start_ngrok():
    from pyngrok import ngrok, conf
    conf.get_default().auth_token = os.getenv("NGROK_AUTHTOKEN")
    domain = os.getenv("NGROK_DOMAIN")
    ngrok.connect(PORT, "http", hostname=domain)
    return f"https://{domain}"


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("\n" + "═" * 58)
    print("  🤖  Planificador Semanal — Bot WhatsApp  (Fase 2)")
    print("═" * 58)

    check_env()
    check_plan()

    # 1. Flask
    print("\n▶  Iniciando servidor Flask...")
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    time.sleep(2)
    print(f"   ✅ Flask corriendo en http://localhost:{PORT}")

    # 2. ngrok
    domain = os.getenv("NGROK_DOMAIN")
    print(f"\n▶  Conectando ngrok → {domain}...")
    try:
        public_url = start_ngrok()
    except Exception as e:
        print(f"\n❌ Error ngrok: {e}")
        sys.exit(1)
    print(f"   ✅ Túnel activo: {public_url}")

    # 3. Scheduler
    print("\n▶  Iniciando mensajes automáticos...")
    load_local("scheduler", "scheduler.py")
    from scheduler import start_scheduler
    scheduler = start_scheduler()

    webhook_url = f"{public_url}/whatsapp"
    print("\n" + "═" * 58)
    print("  📋  URL DEL WEBHOOK — pegá esto en Twilio")
    print("═" * 58)
    print(f"\n  👉  {webhook_url}\n")
    print("  Twilio → Messaging → Sandbox settings")
    print("  «WHEN A MESSAGE COMES IN» → pegá la URL → POST → Guardar")
    print("\n" + "═" * 58)
    print("  ✅  Bot listo. Esperando mensajes en WhatsApp...")
    print("  🛑  Para detener: Ctrl+C")
    print("═" * 58 + "\n")

    def on_exit(sig, frame):
        print("\n🛑 Deteniendo...")
        try:
            scheduler.shutdown(wait=False)
            from pyngrok import ngrok
            ngrok.kill()
        except Exception:
            pass
        sys.exit(0)

    signal.signal(signal.SIGINT, on_exit)
    signal.signal(signal.SIGTERM, on_exit)

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()