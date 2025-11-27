import json
import os
import logging

CONFIG_FILE = "config.json"

def load_config():
    """Carga la configuración desde el archivo JSON."""
    if not os.path.exists(CONFIG_FILE):
        return {"current_db_alias": None, "databases": {}}
    
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error al cargar la configuración: {e}", exc_info=True)
        return {"current_db_alias": None, "databases": {}}

def save_config(config):
    """Guarda la configuración en el archivo JSON."""
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        logging.error(f"Error al guardar la configuración: {e}", exc_info=True)

def add_database(alias, db_id):
    """Añade una nueva base de datos a la configuración."""
    config = load_config()
    config["databases"][alias] = db_id
    # Si es la primera DB, la establecemos como actual por defecto
    if config["current_db_alias"] is None:
        config["current_db_alias"] = alias
    save_config(config)
    return True

def set_current_database(alias):
    """Establece la base de datos actual por su alias."""
    config = load_config()
    if alias in config["databases"]:
        config["current_db_alias"] = alias
        save_config(config)
        return True
    return False

def get_current_database_id():
    """Obtiene el ID de la base de datos actual."""
    config = load_config()
    alias = config.get("current_db_alias")
    if alias:
        return config["databases"].get(alias)
    return None

def get_databases():
    """Devuelve el diccionario de bases de datos."""
    config = load_config()
    return config.get("databases", {})

def get_current_alias():
    """Devuelve el alias de la base de datos actual."""
    config = load_config()
    return config.get("current_db_alias")
