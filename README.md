# Coach Virtual 🏃‍♂️🤖

¡Tu entrenador personal automatizado por WhatsApp! Este proyecto conecta una planilla de Google Sheets con WhatsApp usando GitHub Actions, enviando recordatorios diarios de entrenamiento y un resumen semanal de tu rendimiento.

---

## 🛠️ Funcionalidades Principales

1. **Recordatorio Diario (Lunes a Sábado a las 07:00 AM)**
   - El bot revisa la planilla de Google Sheets buscando la fecha de hoy.
   - Envía un WhatsApp con el tipo de entrenamiento, distancia a correr, ritmo objetivo y notas especiales.
   - Si hoy toca "Descanso" o no hay entrenamiento, te envía un mensaje motivacional para que te recuperes.

2. **Resumen Semanal de Rendimiento (Domingos a las 20:00)**
   - El bot lee todos los entrenamientos de la semana que acaba de pasar (de Lunes a Domingo).
   - Calcula tu **% de Cumplimiento** comparando el Volumen Planeado vs. el Volumen Real.
   - Calcula tu **Ritmo Promedio Real** de la semana.
   - Te informa de tu última variación de **peso** registrada.
   - Te felicita o te da ánimos dependiendo de si cumpliste más del 90%, 70% o menos.

---

## ⚙️ ¿Cómo funciona por debajo?

- **Google Sheets:** Funciona como base de datos amigable. Puedes modificarla desde tu celular o computadora sin tocar código.
- **Python (`main.py`):** Es el "cerebro". Se conecta a Google Sheets usando la librería `gspread`, extrae la información, formatea el texto y llama a la API de CallMeBot.
- **CallMeBot:** Un servicio gratuito que sirve de puente para enviar mensajes de texto a tu cuenta personal de WhatsApp.
- **GitHub Actions (`.github/workflows/recordatorio.yml`):** Es el "motor" que se encarga de ejecutar el archivo Python de manera automática todos los días y semanas, sin que tengas que tener tu computadora encendida.

---

## 📝 Estructura de la Planilla en Google Sheets

Tu planilla debe llamarse **"Entrenamiento Media Maraton"** (o cambiar el nombre en `main.py`). Debe contener las siguientes columnas (exactamente con estos nombres en la fila 1):

1. `Fecha` *(Ejemplo: 05-05-2026 o 05/05/2026)*
2. `Tipo_Entreno` *(Ejemplo: Easy, Long, Fuerza, Descanso)*
3. `Distancia_Planeada (km)` *(Ejemplo: 5)*
4. `Ritmo_Objetivo` *(Ejemplo: 6:30/km)*
5. `Distancia_Real (km)` *(Ejemplo: 5.2)*
6. `Tiempo_Real (min)` *(Ejemplo: 34)*
7. `Peso_Semanal (kg)` *(Ejemplo: 75.5 - Se anota preferiblemente los domingos)*
8. `Notas`

---

## 🚀 Despliegue y Configuración

El repositorio cuenta con 3 "Secrets" en GitHub que son vitales para su funcionamiento:

- `GOOGLE_CREDENTIALS_JSON`: La llave de la cuenta de servicio de Google Cloud para poder leer tu Google Sheet privado de forma automatizada.
- `WHATSAPP_PHONE`: Tu número de teléfono personal (incluyendo el código de país, ej: `+56912345678`).
- `WHATSAPP_API_KEY`: La clave API entregada por el bot de WhatsApp CallMeBot tras enviar el mensaje de autorización.

¡Listo para correr los 21K! 🥇
