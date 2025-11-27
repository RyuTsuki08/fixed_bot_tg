from datetime import datetime, timedelta
import re

def parse_spanish_date(date_text):
    """
    Convierte expresiones de fecha en español a formato YYYY-MM-DD.
    Soporta: hoy, mañana, pasado mañana, próximo [día], en X días, etc.
    """
    if not date_text:
        return None
    
    date_text = date_text.lower().strip()
    today = datetime.now()
    
    # Casos exactos
    if date_text in ["hoy", "today"]:
        return today.strftime("%Y-%m-%d")
    
    if date_text in ["mañana", "tomorrow"]:
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")
    
    if date_text in ["pasado mañana", "pasadomañana"]:
        return (today + timedelta(days=2)).strftime("%Y-%m-%d")
    
    # "En X días"
    match = re.search(r'en (\d+) d[ií]as?', date_text)
    if match:
        days = int(match.group(1))
        return (today + timedelta(days=days)).strftime("%Y-%m-%d")
    
    # Días de la semana
    days_of_week = {
        "lunes": 0, "monday": 0,
        "martes": 1, "tuesday": 1,
        "miércoles": 2, "miercoles": 2, "wednesday": 2,
        "jueves": 3, "thursday": 3,
        "viernes": 4, "friday": 4,
        "sábado": 5, "sabado": 5, "saturday": 5,
        "domingo": 6, "sunday": 6
    }
    
    for day_name, day_num in days_of_week.items():
        if day_name in date_text:
            days_ahead = day_num - today.weekday()
            if days_ahead <= 0:  # Si ya pasó esta semana
                days_ahead += 7
            if "próximo" in date_text or "siguiente" in date_text or "next" in date_text:
                days_ahead += 7  # Próxima semana
            return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
    
    # Si ya está en formato YYYY-MM-DD, validar
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_text):
        try:
            datetime.strptime(date_text, "%Y-%m-%d")
            return date_text
        except ValueError:
            return None
    
    # No se pudo parsear
    return None

def validate_date(date_str):
    """
    Valida que una fecha esté en formato YYYY-MM-DD correcto.
    Retorna (True, date_str) si es válida, (False, error_msg) si no.
    """
    if not date_str:
        return True, date_str  # Null es válido (campo opcional)
    
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return False, f"Formato incorrecto: '{date_str}'. Debe ser YYYY-MM-DD"
    
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True, date_str
    except ValueError:
        return False, f"Fecha inválida: '{date_str}'"
