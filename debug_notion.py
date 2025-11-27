import os
from notion_client import Client
from dotenv import load_dotenv
import config_manager
import json

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_INTEGRATION_TOKEN")

def debug_notion():
    print("--- INICIO DEBUG ---")
    if not NOTION_TOKEN:
        print("Error: No hay token configurado.")
        return

    db_id = config_manager.get_current_database_id()
    if not db_id:
        print("Error: No hay base de datos configurada en config.json")
        return

    notion = Client(auth=NOTION_TOKEN)
    
    print(f"Inspeccionando ID: {db_id}")
    
    try:
        db = notion.databases.retrieve(database_id=db_id)
        print("✅ Objeto recuperado!")
        
        print("\nPropiedades:")
        for name, prop in db.get("properties", {}).items():
            print(f"- {name} ({prop['type']})")

    except Exception as e:
        print(f"\n❌ Error al inspeccionar: {e}")
    
    print("--- FIN DEBUG ---")

if __name__ == "__main__":
    debug_notion()
