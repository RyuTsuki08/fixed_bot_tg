import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
import date_utils

load_dotenv()

# API key global como fallback
DEFAULT_GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("DEFAULT_GEMINI_API_KEY")

def get_chat_response(message, user_id=None):
    """
    Genera respuesta de chat usando Gemini.
    Si user_id es None, usa la API key global.
    """
    try:
        # Obtener API key del usuario o usar global
        if user_id:
            import user_config_manager
            api_key = user_config_manager.get_user_gemini_key(user_id)
        else:
            api_key = DEFAULT_GEMINI_API_KEY
        
        if not api_key:
            return "❌ No tienes configurada tu API key de Gemini. Usa /config para configurarla."
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        response = model.generate_content(message)
        return response.text
    except Exception as e:
        return f"Error al conectar con Gemini: {e}"

def extract_task_info(text, user_id=None):
    """
    Usa Gemini para extraer información estructurada de una tarea.
    Retorna un diccionario con: title, description, date, status, type_val.
    """
    try:
        print(f"DEBUG: Enviando a Gemini: {text}")
        
        # Obtener API key del usuario o usar global
        if user_id:
            import user_config_manager
            api_key = user_config_manager.get_user_gemini_key(user_id)
        else:
            api_key = DEFAULT_GEMINI_API_KEY
        
        if not api_key:
            print("❌ No hay API key de Gemini configurada")
            return {"title": text, "description": None, "date": None, "status": None, "type_val": None}
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        prompt = f"""
        Analiza el siguiente texto y extrae la información para crear una tarea en Notion.
        El texto es: "{text}"
        
        Devuelve SOLO un JSON válido con las siguientes claves (si no encuentras algo, usa null):
        - title: El título principal de la tarea.
        - description: Detalles adicionales.
        - date_raw: Expresión de fecha tal como aparece (ej: "mañana", "próximo lunes", "2025-12-25").
        - status: El estado (ej: "En progreso", "Por hacer", "Completado"). Si no se menciona, usa "Por hacer".
        - type_val: El tipo de proyecto (ej: "Personal", "Negocio").
        
        Ejemplo de salida:
        {{
            "title": "Comprar leche",
            "description": "Leche descremada y pan",
            "date_raw": "mañana",
            "status": "Por hacer",
            "type_val": "Personal"
        }}
        """
        response = model.generate_content(prompt)
        print(f"DEBUG: Respuesta cruda de Gemini: {response.text}")
        
        # Clean response to ensure it's just JSON
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        task_data = json.loads(clean_text)
        
        # Parsear fecha con date_utils
        date_raw = task_data.get("date_raw")
        if date_raw:
            parsed_date = date_utils.parse_spanish_date(date_raw)
            task_data["date"] = parsed_date
        else:
            task_data["date"] = None
            
        return task_data
        
    except Exception as e:
        print(f"❌ Error extrayendo info con Gemini: {e}")
        return {"title": text, "description": None, "date": None, "status": None, "type_val": None}

def transcribe_audio(audio_file_path, user_id=None):
    """
    Transcribe un archivo de audio usando Gemini.
    Soporta archivos de voz de Telegram (.ogg).
    """
    try:
        print(f"DEBUG: Transcribiendo audio: {audio_file_path}")
        
        # Obtener API key del usuario o usar global
        if user_id:
            import user_config_manager
            api_key = user_config_manager.get_user_gemini_key(user_id)
        else:
            api_key = DEFAULT_GEMINI_API_KEY
        
        if not api_key:
            print("❌ No hay API key de Gemini configurada")
            return None
        
        genai.configure(api_key=api_key)
        
        # Upload del archivo a Gemini
        audio_file = genai.upload_file(path=audio_file_path)
        print(f"DEBUG: Archivo subido: {audio_file.uri}")
        
        # Usar modelo con soporte de audio
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        prompt = """Transcribe el siguiente audio a texto en español.
        Devuelve SOLO el texto transcrito, sin comentarios adicionales."""
        
        response = model.generate_content([prompt, audio_file])
        
        print(f"DEBUG: Transcripción: {response.text}")
        
        return response.text.strip()
        
    except Exception as e:
        print(f"❌ Error transcribiendo audio: {e}")
        return None
