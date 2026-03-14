"""
scheduler.py — Mensajes automáticos de WhatsApp
  · 1 vez por día  → comidas del día
  · 1 vez por semana → lista de compras completa

Usa APScheduler con zona horaria de Buenos Aires.
Se inicia junto con el servidor desde run.py.
"""

import os
import logging
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from zoneinfo import ZoneInfo

load_dotenv()

TZ = ZoneInfo("America/Argentina/Buenos_Aires")
logger = logging.getLogger(__name__)


def _safe_send(message_fn):
    """Wrapper que captura errores para no romper el scheduler."""
    try:
        from bot import send_whatsapp
        text = message_fn()
        sid = send_whatsapp(text)
        logger.info(f"[Scheduler] Mensaje enviado. SID: {sid}")
    except Exception as e:
        logger.error(f"[Scheduler] Error al enviar mensaje: {e}")


def job_daily_meals():
    """Envía las comidas del día cada mañana."""
    from bot_logic import cmd_hoy
    logger.info("[Scheduler] Enviando comidas del día...")
    _safe_send(cmd_hoy)


def job_weekly_shopping():
    """Envía la lista de compras una vez por semana."""
    from bot_logic import cmd_compras
    logger.info("[Scheduler] Enviando lista de compras semanal...")
    _safe_send(cmd_compras)


def start_scheduler():
    """
    Crea y arranca el scheduler con los dos jobs configurados desde .env.

    Variables relevantes en .env:
      DAILY_MESSAGE_TIME     = HH:MM  (ej: 08:00)
      WEEKLY_SHOPPING_DAY    = 0-6    (0=lunes, 6=domingo)
      WEEKLY_SHOPPING_TIME   = HH:MM  (ej: 09:00)
    """
    daily_time   = os.getenv("DAILY_MESSAGE_TIME", "08:00")
    weekly_day   = int(os.getenv("WEEKLY_SHOPPING_DAY", "6"))    # domingo por defecto
    weekly_time  = os.getenv("WEEKLY_SHOPPING_TIME", "09:00")

    daily_h,  daily_m  = map(int, daily_time.split(":"))
    weekly_h, weekly_m = map(int, weekly_time.split(":"))

    # Mapeo APScheduler: day_of_week usa nombres en inglés
    DAYS_MAP = {0:"mon", 1:"tue", 2:"wed", 3:"thu", 4:"fri", 5:"sat", 6:"sun"}
    weekly_dow = DAYS_MAP[weekly_day]

    scheduler = BackgroundScheduler(timezone=TZ)

    # Job 1 — Mensaje diario de comidas
    scheduler.add_job(
        job_daily_meals,
        trigger=CronTrigger(hour=daily_h, minute=daily_m, timezone=TZ),
        id="daily_meals",
        name="Comidas del día",
        replace_existing=True,
    )

    # Job 2 — Lista de compras semanal
    scheduler.add_job(
        job_weekly_shopping,
        trigger=CronTrigger(
            day_of_week=weekly_dow, hour=weekly_h, minute=weekly_m, timezone=TZ
        ),
        id="weekly_shopping",
        name="Lista de compras semanal",
        replace_existing=True,
    )

    scheduler.start()

    day_names = ["lunes","martes","miércoles","jueves","viernes","sábado","domingo"]
    print(f"  ⏰  Mensaje diario:   todos los días a las {daily_time}")
    print(f"  📅  Lista de compras: cada {day_names[weekly_day]} a las {weekly_time}")

    return scheduler