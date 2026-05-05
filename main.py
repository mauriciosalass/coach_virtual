import os
import json
import urllib.parse
from datetime import datetime, timedelta
import pytz

import gspread
import requests

# -- CONFIGURACIÓN INICIAL --
GOOGLE_CREDENTIALS_JSON = os.environ.get("GOOGLE_CREDENTIALS_JSON")
WHATSAPP_PHONE = os.environ.get("WHATSAPP_PHONE")
WHATSAPP_API_KEY = os.environ.get("WHATSAPP_API_KEY")

# Nombre de la planilla en tu Google Drive
SPREADSHEET_NAME = "Entrenamiento Media Maraton"

def send_whatsapp(message):
    """Envía un mensaje de WhatsApp a través de CallMeBot."""
    if not WHATSAPP_PHONE or not WHATSAPP_API_KEY:
        print("Error: Credenciales de WhatsApp no configuradas.")
        return
    
    encoded_message = urllib.parse.quote(message)
    url = f"https://api.callmebot.com/whatsapp.php?phone={WHATSAPP_PHONE}&text={encoded_message}&apikey={WHATSAPP_API_KEY}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Mensaje de WhatsApp enviado exitosamente.")
        else:
            print(f"Error al enviar mensaje. Código: {response.status_code}, Respuesta: {response.text}")
    except Exception as e:
        print(f"Excepción al enviar WhatsApp: {e}")

def get_sheet():
    """Conecta con Google Sheets usando la Service Account y retorna la hoja principal."""
    if not GOOGLE_CREDENTIALS_JSON:
        raise ValueError("La variable GOOGLE_CREDENTIALS_JSON no está definida.")
        
    credentials = json.loads(GOOGLE_CREDENTIALS_JSON)
    gc = gspread.service_account_from_dict(credentials)
    
    sh = gc.open(SPREADSHEET_NAME)
    # Retornamos la primera pestaña (hoja) del documento
    return sh.sheet1

def recordatorio_diario(sheet):
    """Función 1: Lee la fecha actual y envía el entrenamiento del día."""
    tz = pytz.timezone('America/Santiago')
    today = datetime.now(tz)
    today_str = today.strftime("%Y-%m-%d") # Asumimos formato YYYY-MM-DD en la planilla
    
    records = sheet.get_all_records()
    today_record = next((row for row in records if str(row.get('Fecha', '')).strip() == today_str), None)

    if today_record:
        tipo = str(today_record.get('Tipo_Entreno', '')).strip()
        dist = today_record.get('Distancia_Planeada (km)', '')
        ritmo = today_record.get('Ritmo_Objetivo', '')
        notas = str(today_record.get('Notas', '')).strip()
        
        if 'descanso' in tipo.lower() or not tipo:
            msg = f"🏃‍♂️ *Coach Virtual* \n¡Hola! Hoy es día de *{tipo or 'Descanso'}*. Tómalo con calma y recupérate para los próximos entrenamientos. 💪"
        else:
            msg = f"🏃‍♂️ *Coach Virtual* \n¡Buen día! Este es tu entrenamiento para hoy:\n\n*Tipo:* {tipo}\n*Distancia:* {dist} km\n*Ritmo Objetivo:* {ritmo}"
            if notas:
                msg += f"\n*Notas:* {notas}"
            msg += "\n\n¡A darlo todo! 🔥"
        
        send_whatsapp(msg)
    else:
        print(f"No se encontró entrenamiento para la fecha {today_str}.")
        # Opcional: avisar que no hay entrenamiento. 
        # send_whatsapp("🏃‍♂️ *Coach Virtual* \nNo encontré entrenamiento programado para hoy en tu planilla. ¡Aprovecha de descansar!")

def reporte_semanal(sheet):
    """Función 2: Calcula estadísticas de la última semana y las envía."""
    tz = pytz.timezone('America/Santiago')
    today = datetime.now(tz)
    
    # Validar que sea domingo (weekday 6 es domingo)
    if today.weekday() != 6:
        print("Hoy no es domingo, omitiendo reporte semanal.")
        return

    # Obtener fechas de los últimos 7 días (lunes a domingo)
    past_7_days = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    
    records = sheet.get_all_records()
    week_records = [row for row in records if str(row.get('Fecha', '')).strip() in past_7_days]

    vol_planeado = 0.0
    vol_real = 0.0
    tiempo_total = 0.0
    peso_actual = None
    
    for row in week_records:
        # Distancia Planeada
        try:
            val = str(row.get('Distancia_Planeada (km)', '')).replace(',', '.')
            if val: vol_planeado += float(val)
        except ValueError:
            pass
            
        # Distancia Real
        try:
            val = str(row.get('Distancia_Real (km)', '')).replace(',', '.')
            if val: vol_real += float(val)
        except ValueError:
            pass

        # Tiempo Real
        try:
            val = str(row.get('Tiempo_Real (min)', '')).replace(',', '.')
            if val: tiempo_total += float(val)
        except ValueError:
            pass
            
        # Peso Semanal (se toma el último válido de la semana)
        peso = str(row.get('Peso_Semanal (kg)', '')).replace(',', '.')
        if peso:
            try:
                peso_actual = float(peso)
            except ValueError:
                pass

    cumplimiento = 0.0
    if vol_planeado > 0:
        cumplimiento = (vol_real / vol_planeado) * 100

    ritmo_promedio = "N/A"
    if vol_real > 0 and tiempo_total > 0:
        ritmo_decimal = tiempo_total / vol_real # min/km
        mins = int(ritmo_decimal)
        secs = int((ritmo_decimal - mins) * 60)
        ritmo_promedio = f"{mins}:{secs:02d} min/km"

    msg = f"📊 *Resumen Semanal - Coach Virtual*\n\n"
    msg += f"🎯 *Volumen Planeado:* {vol_planeado:.2f} km\n"
    msg += f"🏃‍♂️ *Volumen Real:* {vol_real:.2f} km\n"
    msg += f"📈 *Cumplimiento:* {cumplimiento:.1f}%\n"
    msg += f"⏱️ *Ritmo Prom. Real:* {ritmo_promedio}\n"
    
    if peso_actual:
        msg += f"⚖️ *Peso Registrado:* {peso_actual} kg\n"
        
    if cumplimiento >= 90:
        msg += "\n¡Excelente semana! Cumpliste de maravilla, sigue así de constante. 🥇"
    elif cumplimiento >= 70:
        msg += "\n¡Buena semana! Vas por buen camino, a afinar esos detalles para la próxima. 👍"
    elif vol_planeado > 0:
        msg += "\nSemana complicada, pero lo importante es no rendirse. ¡Vamos con todo la próxima! 💪"
    else:
        msg += "\nNo hubo entrenamientos planeados esta semana. ¡A planificar la próxima!"
        
    send_whatsapp(msg)

if __name__ == "__main__":
    import sys
    
    # Recibir la acción por argumento (diario o semanal)
    action = sys.argv[1] if len(sys.argv) > 1 else "diario"
    
    try:
        sheet = get_sheet()
        if action == "diario":
            print("Ejecutando recordatorio diario...")
            recordatorio_diario(sheet)
        elif action == "semanal":
            print("Ejecutando reporte semanal...")
            reporte_semanal(sheet)
        else:
            print(f"Acción desconocida: {action}")
    except Exception as e:
        print(f"Error fatal: {e}")
