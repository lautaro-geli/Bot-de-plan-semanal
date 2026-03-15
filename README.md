# Planificador Semanal de Comidas

Aplicación web + bot de WhatsApp para planificación semanal de comidas para una familia. Desarrollado como proyecto de prácticas profesionalizantes.

---

## Tecnologías utilizadas

- **Python 3 + Flask** — backend y API REST
- **HTML + CSS + JavaScript** — frontend sin frameworks
- **Twilio WhatsApp API** — bot de mensajería
- **Railway** — hosting en la nube con persistencia de datos
- **ngrok** — túnel para desarrollo local
- **APScheduler** — mensajes automáticos programados
- **Git + GitHub** — control de versiones

---

## ¿Qué hace?

- Genera un plan semanal de comidas con distribución balanceada de proteínas
- Permite editar el plan desde la web
- Genera la lista de compras automáticamente sumando ingredientes
- Bot de WhatsApp con comandos: `plan`, `hoy`, `compras`, `menu`
- Envía las comidas del día cada mañana por WhatsApp de forma automática

---
> Proyecto desarrollado con asistencia de IA (Claude - Anthropic) como herramienta de apoyo en el proceso de desarrollo
---

## Producción

Hosteado en Railway con Volume para persistencia de datos.  
Web: `https://bot-de-plan-semanal-production.up.railway.app`
