import os
import logging
from notion_client import Client
from dotenv import load_dotenv
import config_manager
import time

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_INTEGRATION_TOKEN")

logger = logging.getLogger(__name__)

def retry_on_failure(max_retries=3, delay=1):
    """Decorador para reintentar llamadas a API en caso de fallo."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(f"Intento {attempt + 1} falló: {e}. Reintentando en {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"Todos los intentos fallaron: {e}", exc_info=True)
                        raise
        return wrapper
    return decorator

def get_select_options(database_id, property_name):
    """
    Obtiene las opciones válidas de un campo select desde Notion.
    Retorna una lista de opciones válidas.
    """
    try:
        client = Client(auth=NOTION_TOKEN)
        db = client.databases.retrieve(database_id=database_id)
        
        properties = db.get("properties", {})
        prop = properties.get(property_name)
        
        if not prop:
            return []
        
        if prop.get("type") == "select":
            options = prop.get("select", {}).get("options", [])
            return [opt["name"] for opt in options]
        
        return []
    except Exception as e:
        logger.error(f"Error obteniendo opciones de select: {e}")
        return []

@retry_on_failure(max_retries=3, delay=1)
def create_page(title, user_id=None, description=None, date=None, status=None, type_val=None):
    """
    Crea una página en la base de datos de Notion.
    Incluye reintentos automáticos y validación.
    Si user_id es None, usa credenciales globales.
    """
    # Obtener token del usuario o usar global
    if user_id:
        import user_config_manager
        notion_token = user_config_manager.get_user_notion_token(user_id)
        database_id = user_config_manager.get_user_current_db_id(user_id)
    else:
        notion_token = NOTION_TOKEN
        database_id = config_manager.get_current_database_id()
        if not database_id:
            database_id = os.getenv("NOTION_DATABASE_ID")
    
    if not notion_token:
        logger.error("NOTION_TOKEN no configurado")
        return "❌ Error: No tienes configurado tu token de Notion. Usa /config"

    if not database_id:
        logger.error("No hay database_id configurado")
        return "❌ Error: No tienes bases de datos configuradas. Usa /add_db"

    client = Client(auth=notion_token)

    try:
        logger.info(f"Creando página: '{title}' en DB {database_id}")
        
        # Validar opciones de select antes de crear
        if status:
            valid_options = get_select_options(database_id, "Estado del Proyecto")
            if valid_options and status not in valid_options:
                options_str = ", ".join(valid_options)
                return f"❌ Error: '{status}' no es un estado válido.\n✅ Opciones disponibles: {options_str}"
        
        # Construct properties
        properties = {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": title
                        }
                    }
                ]
            }
        }
        
        if description:
            properties["descripcion"] = {
                "rich_text": [
                    {
                        "text": {
                            "content": description
                        }
                    }
                ]
            }
            
        if date:
            properties["Fecha de Inicio"] = {
                "date": {
                    "start": date
                }
            }
            
        if status:
            properties["Estado del Proyecto"] = {
                "select": {
                    "name": status
                }
            }
            
        if type_val:
            properties["Tipo (Personal, negocio, etc.)"] = {
                "rich_text": [
                    {
                        "text": {
                            "content": type_val
                        }
                    }
                ]
            }

        response = client.pages.create(
            parent={"database_id": database_id},
            properties=properties
        )
        
        logger.info(f"Página creada exitosamente: {response['id']}")
        return f"✅ Página creada: {title}\n🔗 {response['url']}"
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error creando página: {error_msg}", exc_info=True)
        
        # Mensajes específicos según el error
        if "Could not find database" in error_msg:
            return "❌ Error: No encuentro la base de datos. Verifica que esté compartida con el bot."
        elif "is not a property" in error_msg:
            return "❌ Error: Una de las propiedades no existe en la base de datos."
        elif "invalid" in error_msg.lower() and "select" in error_msg.lower():
            return f"❌ Error: El estado '{status}' no es válido. Usa opciones existentes."
        else:
            return "❌ Error al crear la página. Revisa los logs para más detalles."

def search_pages(query, limit=10):
    """
    Busca páginas en la base de datos de Notion por título.
    Retorna una lista de diccionarios con id, title, url.
    """
    if not NOTION_TOKEN:
        return []
    
    database_id = config_manager.get_current_database_id()
    if not database_id:
        database_id = os.getenv("NOTION_DATABASE_ID")
    
    if not database_id:
        return []
    
    try:
        client = Client(auth=NOTION_TOKEN)
        
        # Traer las últimas 50 páginas sin filtrar (más rápido y seguro)
        response = client.databases.query(
            database_id=database_id,
            page_size=50
        )
        
        results = []
        query_lower = query.lower()
        
        for page in response.get("results", []):
            # Obtener título de manera segura
            title = "Sin título"
            props = page.get("properties", {})
            
            # Intentar encontrar la propiedad de título
            for prop_name, prop_data in props.items():
                if prop_data.get("id") == "title":
                    title_list = prop_data.get("title", [])
                    if title_list:
                        title = title_list[0].get("plain_text", "Sin título")
                    break
            
            # Filtrar en Python (case insensitive)
            if query_lower in title.lower():
                results.append({
                    "id": page["id"],
                    "title": title,
                    "url": page["url"]
                })
                
            if len(results) >= limit:
                break
            
        return results

    except Exception as e:
        logger.error(f"Error buscando páginas: {e}")
        return []

def update_page(page_id, **kwargs):
    """
    Actualiza una página en Notion.
    Acepta: title, description, date, status, type_val.
    """
    if not NOTION_TOKEN:
        return "❌ Error: Token de Notion no configurado."
    
    client = Client(auth=NOTION_TOKEN)
    
    try:
        properties = {}
        
        if "title" in kwargs and kwargs["title"]:
            properties["Name"] = {
                "title": [{"text": {"content": kwargs["title"]}}]
            }
        
        if "description" in kwargs and kwargs["description"]:
            properties["descripcion"] = {
                "rich_text": [{"text": {"content": kwargs["description"]}}]
            }
        
        if "date" in kwargs and kwargs["date"]:
            properties["Fecha de Inicio"] = {
                "date": {"start": kwargs["date"]}
            }
        
        if "status" in kwargs and kwargs["status"]:
            properties["Estado del Proyecto"] = {
                "select": {"name": kwargs["status"]}
            }
        
        if "type_val" in kwargs and kwargs["type_val"]:
            properties["Tipo (Personal, negocio, etc.)"] = {
                "rich_text": [{"text": {"content": kwargs["type_val"]}}]
            }
        
        client.pages.update(page_id=page_id, properties=properties)
        logger.info(f"Página {page_id} actualizada")
        return "✅ Tarea actualizada correctamente."
        
    except Exception as e:
        logger.error(f"Error actualizando página: {e}")
        return f"❌ Error al actualizar: {str(e)}"
