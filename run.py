"""
run.py — Script principal
- Local: Flask + ngrok + scheduler
- Railway: Flask + scheduler (sin ngrok, Railway da la URL pública)
"""

import os
import sys
import time
import threading
import signal
import logging
import importlib.util

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Cargar .env si existe (local). En Railway las vars vienen del entorno.
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

# Railway asigna el puerto via variable PORT
PORT = int(os.getenv("PORT", os.getenv("FLASK_PORT", 5000)))

# Detectar si estamos en Railway
ON_RAILWAY = os.getenv("RAILWAY_ENVIRONMENT") is not None or os.getenv("RAILWAY_PROJECT_ID") is not None


# ── Cargar módulo local por ruta absoluta ─────────────────────────────────────
def load_local(name, filename):
    path = os.path.join(BASE_DIR, filename)
    if not os.path.exists(path):
        print(f"\n❌ No se encontró: {path}")
        sys.exit(1)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# ── Validaciones ──────────────────────────────────────────────────────────────
def check_env():
    required = ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN",
                "TWILIO_WHATSAPP_NUMBER", "TO_WHATSAPP_NUMBER"]
    # ngrok solo requerido en local
    if not ON_RAILWAY:
        required += ["NGROK_AUTHTOKEN", "NGROK_DOMAIN"]

    missing = [k for k in required
               if not os.getenv(k, "").strip()
               or "XXXX" in os.getenv(k, "")
               or "xxxxxxx" in os.getenv(k, "")]
    if missing:
        print("\n❌ Faltan configurar estas variables:\n")
        for m in missing:
            print(f"   • {m}")
        if not ON_RAILWAY:
            print("\n👉 Editá el archivo .env\n")
        else:
            print("\n👉 Agregalas en Railway → Variables\n")
        sys.exit(1)


def check_plan():
    if not os.path.exists(os.path.join(BASE_DIR, "plan_semanal.json")):
        print("\n⚠️  No existe plan_semanal.json")
        print("   Generá un plan desde la web primero.\n")


# ── Flask ─────────────────────────────────────────────────────────────────────
def run_flask():
    load_local("meal_data",  "meal_data.py")
    load_local("bot_logic",  "bot_logic.py")
    bot = load_local("bot",  "bot.py")
    # En Railway usar host 0.0.0.0 es obligatorio
    bot.app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)


# ── ngrok (solo local) ────────────────────────────────────────────────────────
def start_ngrok():
    from pyngrok import ngrok, conf
    conf.get_default().auth_token = os.getenv("NGROK_AUTHTOKEN")
    domain = os.getenv("NGROK_DOMAIN")
    ngrok.connect(PORT, "http", hostname=domain)
    return f"https://{domain}"


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("\n" + "═" * 58)
    print("  🤖  Planificador Semanal — Bot WhatsApp")
    env_label = "☁️  Railway" if ON_RAILWAY else "💻  Local"
    print(f"  Entorno: {env_label}")
    print("═" * 58)

    check_env()
    check_plan()

    # 1. Flask
    print(f"\n▶  Iniciando Flask en puerto {PORT}...")
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    time.sleep(2)
    print(f"   ✅ Flask corriendo")

    # 2. ngrok — solo en local
    if ON_RAILWAY:
        public_url = os.getenv("RAILWAY_PUBLIC_DOMAIN", "")
        if public_url:
            public_url = f"https://{public_url}"
            webhook_url = f"{public_url}/whatsapp"
            print(f"\n   🌐 URL pública: {public_url}")
        else:
            webhook_url = "(configurá RAILWAY_PUBLIC_DOMAIN)"
    else:
        domain = os.getenv("NGROK_DOMAIN")
        print(f"\n▶  Conectando ngrok → {domain}...")
        try:
            public_url = start_ngrok()
        except Exception as e:
            print(f"\n❌ Error ngrok: {e}")
            sys.exit(1)
        print(f"   ✅ Túnel activo: {public_url}")
        webhook_url = f"{public_url}/whatsapp"

    # 3. Scheduler
    print("\n▶  Iniciando mensajes automáticos...")
    load_local("scheduler", "scheduler.py")
    from scheduler import start_scheduler
    scheduler = start_scheduler()

    print("\n" + "═" * 58)
    print("  📋  URL DEL WEBHOOK para Twilio:")
    print(f"\n  👉  {webhook_url}\n")
    print("  ✅  Bot listo. Esperando mensajes...")
    print("  🛑  Para detener: Ctrl+C")
    print("═" * 58 + "\n")

    def on_exit(sig, frame):
        print("\n🛑 Deteniendo...")
        try:
            scheduler.shutdown(wait=False)
            if not ON_RAILWAY:
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