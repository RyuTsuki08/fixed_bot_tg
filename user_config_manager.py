import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

CONFIG_FILE = "users_config.json"

def load_config():
    """Carga la configuración de todos los usuarios."""
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error cargando users_config.json: {e}", exc_info=True)
        return {}

def save_config(config):
    """Guarda la configuración de todos los usuarios."""
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        logger.error(f"Error guardando users_config.json: {e}", exc_info=True)

def _create_default_user_config():
    """Crea una configuración por defecto para un nuevo usuario."""
    return {
        "gemini_api_key": None,
        "notion_token": None,
        "notion_databases": {},
        "current_db_alias": None,
        "created_at": datetime.now().isoformat()
    }

def get_user_config(user_id):
    """Obtiene la configuración de un usuario específico."""
    config = load_config()
    return config.get(str(user_id), None)

def has_user_config(user_id):
    """Verifica si un usuario tiene configuración."""
    user_config = get_user_config(user_id)
    if not user_config:
        return False
    return bool(user_config.get("gemini_api_key") or user_config.get("notion_token"))

def set_user_gemini_key(user_id, api_key):
    """Configura la API key de Gemini para un usuario."""
    config = load_config()
    user_id_str = str(user_id)
    
    if user_id_str not in config:
        config[user_id_str] = _create_default_user_config()
    
    config[user_id_str]["gemini_api_key"] = api_key
    config[user_id_str]["updated_at"] = datetime.now().isoformat()
    save_config(config)
    logger.info(f"Usuario {user_id} configuró Gemini API key")

def set_user_notion_token(user_id, notion_token):
    """Configura el token de Notion para un usuario."""
    config = load_config()
    user_id_str = str(user_id)
    
    if user_id_str not in config:
        config[user_id_str] = _create_default_user_config()
    
    config[user_id_str]["notion_token"] = notion_token
    config[user_id_str]["updated_at"] = datetime.now().isoformat()
    save_config(config)
    logger.info(f"Usuario {user_id} configuró Notion token")

def add_user_database(user_id, alias, db_id):
    """Añade una base de datos de Notion para un usuario."""
    config = load_config()
    user_id_str = str(user_id)
    
    if user_id_str not in config:
        config[user_id_str] = _create_default_user_config()
    
    config[user_id_str]["notion_databases"][alias] = db_id
    
    # Si es la primera BD, establecerla como activa
    if not config[user_id_str]["current_db_alias"]:
        config[user_id_str]["current_db_alias"] = alias
    
    save_config(config)
    logger.info(f"Usuario {user_id} añadió BD '{alias}'")
    return True

def set_user_current_database(user_id, alias):
    """Establece la base de datos activa para un usuario."""
    config = load_config()
    user_id_str = str(user_id)
    
    if user_id_str not in config:
        return False
    
    if alias not in config[user_id_str]["notion_databases"]:
        return False
    
    config[user_id_str]["current_db_alias"] = alias
    save_config(config)
    logger.info(f"Usuario {user_id} cambió BD activa a '{alias}'")
    return True

def get_user_gemini_key(user_id):
    """Obtiene la API key de Gemini del usuario o fallback global."""
    user_config = get_user_config(user_id)
    if user_config and user_config.get("gemini_api_key"):
        return user_config["gemini_api_key"]
    
    # Fallback a credencial global
    fallback = os.getenv("DEFAULT_GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    if fallback:
        logger.warning(f"Usuario {user_id} usando Gemini API key global (fallback)")
    return fallback

def get_user_notion_token(user_id):
    """Obtiene el token de Notion del usuario o fallback global."""
    user_config = get_user_config(user_id)
    if user_config and user_config.get("notion_token"):
        return user_config["notion_token"]
    
    # Fallback a credencial global
    fallback = os.getenv("NOTION_INTEGRATION_TOKEN")
    if fallback:
        logger.warning(f"Usuario {user_id} usando Notion token global (fallback)")
    return fallback

def get_user_current_db_id(user_id):
    """Obtiene el ID de la base de datos activa del usuario."""
    user_config = get_user_config(user_id)
    if not user_config:
        # Fallback a config_manager antiguo
        import config_manager
        return config_manager.get_current_database_id()
    
    alias = user_config.get("current_db_alias")
    if alias:
        return user_config["notion_databases"].get(alias)
    
    # Fallback a config_manager antiguo
    import config_manager
    return config_manager.get_current_database_id()

def get_user_databases(user_id):
    """Obtiene todas las bases de datos de un usuario."""
    user_config = get_user_config(user_id)
    if user_config:
        return user_config.get("notion_databases", {})
    
    # Fallback a config_manager antiguo
    import config_manager
    return config_manager.get_databases()

def get_user_current_alias(user_id):
    """Obtiene el alias de la BD activa del usuario."""
    user_config = get_user_config(user_id)
    if user_config:
        return user_config.get("current_db_alias")
    
    # Fallback a config_manager antiguo
    import config_manager
    return config_manager.get_current_alias()

def delete_user_config(user_id):
    """Elimina la configuración de un usuario (comando /reset_config)."""
    config = load_config()
    user_id_str = str(user_id)
    
    if user_id_str in config:
        del config[user_id_str]
        save_config(config)
        logger.info(f"Usuario {user_id} eliminó su configuración")
        return True
    return False
